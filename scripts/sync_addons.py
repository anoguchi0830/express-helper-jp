#!/usr/bin/env python3
"""
Adobe Express アドオンカタログ 一気通貫同期スクリプト。

Playwright でブラウザを起動し、Adobe Express の Add-ons ページから
IMS トークン（Authorization ヘッダー）を自動採取した上で、
fetch_addons.py → translate.py を順に実行する。

使い方:
  ./venv/bin/python scripts/sync_addons.py
  ./venv/bin/python scripts/sync_addons.py --dry-run
  ./venv/bin/python scripts/sync_addons.py --skip-translate
  ./venv/bin/python scripts/sync_addons.py --timeout 600

初回のみブラウザで Adobe にログインが必要（`.playwright-profile/` に
セッションが保存されるため 2 回目以降は自動でトークンを取得できる）。

フラグ:
  --dry-run        fetch_addons.py に --dry-run を渡し、翻訳は実行しない
  --skip-translate fetch のみ実行（translate.py は実行しない）
  --timeout        トークン捕捉の待機上限（秒、デフォルト 300）
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 定数
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ADD_ONS_URL = "https://new.express.adobe.com/add-ons"
TOKEN_HOST_MARKER = "ffc-addon.adobe.io"
PROFILE_DIR = Path(__file__).resolve().parent.parent / ".playwright-profile"
DEFAULT_TIMEOUT = 300

SCRIPTS_DIR = Path(__file__).resolve().parent
FETCH_SCRIPT = SCRIPTS_DIR / "fetch_addons.py"
TRANSLATE_SCRIPT = SCRIPTS_DIR / "translate.py"

SRC_PATH = "src/ui/data/addons_data.json"
DOCS_PATH = "docs/addons_data.json"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# トークン採取
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def capture_token(timeout_sec: int) -> str:
    """
    Playwright でブラウザを開き、ffc-addon.adobe.io 宛リクエストの
    Authorization ヘッダーを捕捉して返す。ログイン待ちのため待機上限を長めに取る。
    """
    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "[ERROR] playwright がインストールされていません。"
            " ./venv/bin/pip install playwright を実行してください。",
            file=sys.stderr,
        )
        sys.exit(1)

    print("ブラウザで Adobe にログインしてください（初回のみ）。", file=sys.stderr)
    print(f"  待機上限: {timeout_sec} 秒", file=sys.stderr)

    captured: dict = {}

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
        )

        def on_request(request):
            if TOKEN_HOST_MARKER in request.url and "token" not in captured:
                auth = request.headers.get("authorization")
                if auth:
                    captured["token"] = auth

        context.on("request", on_request)

        page = context.new_page()
        page.goto(ADD_ONS_URL)

        # ── トークン捕捉待ち ────────────────────────────
        # ユーザーがブラウザを手動で閉じると Playwright が例外
        # （TargetClosedError 等）を投げるため、捕捉して中断扱いにする
        browser_closed = False
        waited = 0.0
        interval = 0.5
        try:
            while "token" not in captured and waited < timeout_sec:
                page.wait_for_timeout(int(interval * 1000))
                waited += interval
        except PlaywrightError:
            browser_closed = True

        # 手動クローズ後の二重クローズを避ける
        try:
            context.close()
        except PlaywrightError:
            pass

    if "token" not in captured:
        if browser_closed:
            print(
                "[ERROR] ブラウザが閉じられたため中断しました。再実行してください。",
                file=sys.stderr,
            )
        else:
            print(
                f"[ERROR] {timeout_sec} 秒以内にトークンを捕捉できませんでした。"
                " ログインが完了しているか確認して再実行してください。",
                file=sys.stderr,
            )
        sys.exit(1)

    print("トークンを取得しました。", file=sys.stderr)
    return captured["token"]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# サブプロセス実行
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def run_step(step_name: str, args: list) -> None:
    """サブプロセスを実行し、失敗時はどのステップで止まったか明示して終了する。"""
    result = subprocess.run(args)
    if result.returncode != 0:
        print(
            f"[ERROR] {step_name} が失敗しました（exit code {result.returncode}）。"
            " ここで処理を中断します。",
            file=sys.stderr,
        )
        sys.exit(result.returncode)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# メイン
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Adobe Express アドオンカタログを自動同期する（トークン採取 → fetch → translate）"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="fetch_addons.py --dry-run のみ実行し、翻訳は実行しない",
    )
    parser.add_argument(
        "--skip-translate",
        action="store_true",
        help="fetch のみ実行（translate.py は実行しない）",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"トークン捕捉の待機上限（秒、デフォルト {DEFAULT_TIMEOUT}）",
    )
    args = parser.parse_args()

    # ── 1. トークン採取 ────────────────────────────────────
    print("Playwright でブラウザを起動し、トークンを採取します...")
    token = capture_token(args.timeout)

    # ── 2. fetch_addons.py 実行 ────────────────────────────
    print("\nfetch_addons.py を実行中...")
    fetch_args = [sys.executable, str(FETCH_SCRIPT), "--token", token]
    if args.dry_run:
        fetch_args.append("--dry-run")
    run_step("fetch_addons.py", fetch_args)

    if args.dry_run:
        print("\n[DRY-RUN] 翻訳ステップは実行しません。")
        return

    if args.skip_translate:
        print("\n--skip-translate が指定されたため、翻訳ステップをスキップします。")
    else:
        # ── 3. translate.py --dict 実行 ────────────────────
        print("\ntranslate.py --dict を実行中...")
        run_step("translate.py --dict", [sys.executable, str(TRANSLATE_SCRIPT), "--dict"])

        # ── 4. translate.py（API モード）実行 ──────────────
        if os.environ.get("ANTHROPIC_API_KEY"):
            print("\ntranslate.py（API モード）を実行中...")
            run_step("translate.py", [sys.executable, str(TRANSLATE_SCRIPT)])
        else:
            print(
                "\nANTHROPIC_API_KEY 未設定のため API 翻訳をスキップします。"
                " 手動で descriptionJa/Ko を翻訳するか、"
                " ANTHROPIC_API_KEY を設定して translate.py を再実行してください。"
            )

    # ── 5. 差分表示 ────────────────────────────────────────
    print("\n--- 差分サマリー ---")
    subprocess.run(["git", "diff", "--stat", "--", SRC_PATH, DOCS_PATH])

    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  同期処理が完了しました。
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

次のステップ:
  1. git diff {SRC_PATH} で差分確認
  2. 新規エントリを手動補完（category / nameJa / descriptionJa など）
  3. git add {SRC_PATH} {DOCS_PATH}
     git commit -m "chore: sync addon catalog"
""")


if __name__ == "__main__":
    main()

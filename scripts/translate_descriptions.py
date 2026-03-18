#!/usr/bin/env python3
"""
Claude API を使って新規エントリの descriptionJa/Ko と keywordsJa/Ko を翻訳する。

対象:
  - descriptionJa == ""  → descriptionJa / descriptionKo を翻訳
  - keywordsJa == keywordsEn → keywordsJa / keywordsKo を翻訳

使い方:
  export ANTHROPIC_API_KEY="sk-ant-..."
  python3 scripts/translate_descriptions.py

  # 確認のみ（書き込みなし）
  python3 scripts/translate_descriptions.py --dry-run
"""
import json
import os
import sys
import time
import argparse
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 定数
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SRC_PATH   = "src/ui/data/addons_data.json"
DOCS_PATH  = "docs/addons_data.json"
API_URL    = "https://api.anthropic.com/v1/messages"
MODEL      = "claude-haiku-4-5"
BATCH_SIZE = 20   # 1リクエストあたりの最大エントリ数


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Claude API 呼び出し
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def call_claude(api_key: str, prompt: str) -> str:
    body = json.dumps({
        "model": MODEL,
        "max_tokens": 8192,
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")

    req = Request(
        API_URL,
        data=body,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["content"][0]["text"]
    except HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        print(f"\n[ERROR] HTTP {e.code}: {body_text}", file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(f"\n[ERROR] ネットワークエラー: {e.reason}", file=sys.stderr)
        sys.exit(1)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# プロンプト構築
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SYSTEM_PROMPT = """Adobe Express のアドオン（プラグイン）情報を日本語と韓国語に翻訳します。

ルール:
- アプリ名・ブランド名・サービス名（Adobe Express, Shopify, TikTok, WCAG 等）はそのまま残す
- descriptionJa/Ko は自然で簡潔な翻訳にする（機械翻訳っぽくしない）
- keywords は短いキーワード単位で翻訳する（1語〜3語程度）
- 出力は必ず JSON 配列のみ（説明文や前置きは不要）
"""

def build_prompt(entries: list[dict]) -> str:
    input_json = json.dumps(entries, ensure_ascii=False, indent=2)
    return f"""{SYSTEM_PROMPT}

以下の JSON 配列を翻訳してください。
各エントリに `needs_desc` と `needs_kw` フラグがあります。
- needs_desc: true → descriptionJa と descriptionKo を翻訳（descriptionEn を元に）
- needs_kw: true → keywordsJa と keywordsKo を翻訳（keywordsEn を元に）

入力:
{input_json}

出力形式（同じ順序で、翻訳不要なフィールドは空文字のまま）:
[
  {{
    "id": "addon-id",
    "descriptionJa": "翻訳済みまたは空文字",
    "descriptionKo": "번역된 텍스트 또는 빈 문자열",
    "keywordsJa": ["キーワード1", "キーワード2"],
    "keywordsKo": ["키워드1", "키워드2"]
  }}
]

JSON 配列のみを返してください。"""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# JSON 抽出（マークダウンコードブロック対応）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def extract_json_array(text: str) -> list:
    """レスポンステキストから JSON 配列を抽出する。"""
    # ```json ... ``` ブロックがあれば中身を取り出す
    import re
    m = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", text, re.DOTALL)
    if m:
        text = m.group(1)
    else:
        # 最初の [ から最後の ] までを取り出す
        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1:
            text = text[start:end+1]
    return json.loads(text)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 原子的書き込み
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def atomic_write(path: str, db: dict) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, path)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# メイン
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Claude API で description / keywords を自動翻訳する"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="翻訳内容を表示するがファイルには書き込まない",
    )
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("[ERROR] ANTHROPIC_API_KEY 環境変数が設定されていません。", file=sys.stderr)
        print("  export ANTHROPIC_API_KEY='sk-ant-...'", file=sys.stderr)
        sys.exit(1)

    # ── 1. データ読み込み ──────────────────────────────────
    print(f"データを読み込み中: {SRC_PATH}")
    with open(SRC_PATH, encoding="utf-8") as f:
        db = json.load(f)

    addons = db["addons"]

    # ── 2. 翻訳対象を抽出 ─────────────────────────────────
    targets = []
    for addon in addons:
        needs_desc = not addon.get("descriptionJa", "").strip()
        needs_kw   = addon.get("keywordsJa") == addon.get("keywordsEn") and bool(addon.get("keywordsEn"))
        if needs_desc or needs_kw:
            targets.append({
                "id":            addon["id"],
                "needs_desc":    needs_desc,
                "needs_kw":      needs_kw,
                "descriptionEn": addon.get("descriptionEn") or addon.get("description", ""),
                "keywordsEn":    addon.get("keywordsEn", []),
            })

    if not targets:
        print("翻訳対象エントリはありません。")
        return

    desc_count = sum(1 for t in targets if t["needs_desc"])
    kw_count   = sum(1 for t in targets if t["needs_kw"])
    print(f"  翻訳対象: {len(targets)} 件")
    print(f"    description 翻訳: {desc_count} 件")
    print(f"    keywords 翻訳:    {kw_count} 件")

    if args.dry_run:
        print("\n[DRY-RUN] 翻訳対象エントリ一覧:")
        for t in targets:
            flags = []
            if t["needs_desc"]: flags.append("desc")
            if t["needs_kw"]:   flags.append("kw")
            print(f"  - {t['id']}  [{', '.join(flags)}]")
        print(f"\n[DRY-RUN] ファイルは変更しません。")
        return

    # ── 3. バッチ翻訳 ─────────────────────────────────────
    translation_map: dict[str, dict] = {}
    total_batches = (len(targets) + BATCH_SIZE - 1) // BATCH_SIZE

    for i in range(0, len(targets), BATCH_SIZE):
        batch = targets[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        print(f"\nバッチ {batch_num}/{total_batches} を翻訳中... ({len(batch)} 件)", flush=True)

        prompt = build_prompt(batch)
        response_text = call_claude(api_key, prompt)

        try:
            results = extract_json_array(response_text)
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON パース失敗: {e}", file=sys.stderr)
            print("レスポンス:", response_text[:500], file=sys.stderr)
            sys.exit(1)

        for result in results:
            translation_map[result["id"]] = result
            print(f"  ✓ {result['id']}")

        # レート制限対策（バッチ間に少し待機）
        if batch_num < total_batches:
            time.sleep(1)

    # ── 4. データ更新 ─────────────────────────────────────
    updated_desc = 0
    updated_kw   = 0

    for addon in addons:
        tr = translation_map.get(addon["id"])
        if not tr:
            continue

        if addon.get("descriptionJa", "") == "" and tr.get("descriptionJa"):
            addon["descriptionJa"] = tr["descriptionJa"]
            addon["descriptionKo"] = tr.get("descriptionKo", "")
            updated_desc += 1

        if addon.get("keywordsJa") == addon.get("keywordsEn") and tr.get("keywordsJa"):
            addon["keywordsJa"] = tr["keywordsJa"]
            addon["keywordsKo"] = tr.get("keywordsKo", [])
            addon["keywords"]   = tr["keywordsJa"]  # 検索プライマリも更新
            updated_kw += 1

    # ── 5. 書き込み ───────────────────────────────────────
    print(f"\nファイルに書き込み中...")
    atomic_write(SRC_PATH, db)
    print(f"  書き込み完了: {SRC_PATH}")
    atomic_write(DOCS_PATH, db)
    print(f"  書き込み完了: {DOCS_PATH}")

    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  完了
    description 翻訳: {updated_desc} 件
    keywords 翻訳:    {updated_kw} 件
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

次のステップ:
  git diff src/ui/data/addons_data.json  # 差分確認
  # 内容を確認後コミット
""")


if __name__ == "__main__":
    main()

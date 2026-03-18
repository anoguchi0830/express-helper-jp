#!/usr/bin/env python3
"""
Adobe Express アドオンカタログ自動同期スクリプト。

使い方:
  1. https://new.express.adobe.com/add-ons をブラウザで開く
  2. DevTools > Network > /v2/auth/addons リクエストを選択
     → Headers > Authorization の値をコピー
  3. python3 scripts/fetch_addons.py --token "Bearer eyJ..."
  4. python3 scripts/translate_keywords.py
  5. 新規エントリの category / nameJa / descriptionJa などを手動補完
  6. git add / git commit

フラグ:
  --token   Authorization ヘッダー値（必須）。"Bearer " プレフィックスは任意。
  --dry-run ファイル書き込みなしで確認のみ
"""
import argparse
import base64
import json
import os
import re
import sys
import unicodedata
from datetime import date
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 定数
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
API_BASE = "https://ffc-addon.adobe.io/v2/auth/addons"
API_PARAMS = "pageSize=25&orderBy=ADDON_NAME&supportedDevices=desktop"
PAGE_SIZE = 25

SRC_PATH = "src/ui/data/addons_data.json"
DOCS_PATH = "docs/addons_data.json"

DEFAULT_CATEGORY = "utility"
DEFAULT_CATEGORY_JA = "ユーティリティ"
MARKETPLACE_URL_TEMPLATE = "https://new.express.adobe.com/add-ons?addOnId={}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# slugify
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def slugify(name: str, fallback: str) -> str:
    """
    English name → URL-safe slug.
    Non-ASCII characters (e.g. Japanese) will cause an empty slug → fallback.
    """
    normalized = unicodedata.normalize("NFKD", name)
    ascii_str = normalized.encode("ascii", "ignore").decode("ascii")
    lower = ascii_str.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", lower).strip("-")
    return slug if slug else fallback


def unique_slug(base: str, existing_ids: set) -> str:
    """base が既存 id と衝突する場合、-2, -3, ... を付けて一意にする。"""
    if base not in existing_ids:
        return base
    i = 2
    while f"{base}-{i}" in existing_ids:
        i += 1
    return f"{base}-{i}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# API フェッチ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def extract_client_id(token: str) -> str | None:
    """JWT から client_id を抽出して x-api-key に使う。"""
    try:
        parts = token.replace("Bearer ", "").split(".")
        if len(parts) < 2:
            return None
        # Base64url パディング補完
        payload_b64 = parts[1] + "=" * (-len(parts[1]) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        return payload.get("client_id")
    except Exception:
        return None


def fetch_page(token: str, page_index: int) -> dict:
    url = f"{API_BASE}?pageIndex={page_index}&{API_PARAMS}"
    headers = {
        "Authorization": token,
        "Accept": "*/*",
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        ),
    }
    client_id = extract_client_id(token)
    if client_id:
        headers["x-api-key"] = client_id
    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        print(f"\n[ERROR] HTTP {e.code}: {e.reason}", file=sys.stderr)
        if e.code == 401:
            print("       トークンが無効または期限切れです。再取得してください。", file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(f"\n[ERROR] ネットワークエラー: {e.reason}", file=sys.stderr)
        sys.exit(1)


def fetch_all_addons(token: str) -> list[dict]:
    """全ページを取得して items リストを返す。"""
    print("ページ 1 を取得中...", end="", flush=True)
    first = fetch_page(token, 0)

    total = first["pagination"]["totalSize"]
    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
    items = list(first.get("items", []))
    print(f" 合計 {total} 件 / {total_pages} ページ")

    for page in range(1, total_pages):
        print(f"  ページ {page + 1}/{total_pages} 取得中...", end="\r", flush=True)
        data = fetch_page(token, page)
        items.extend(data.get("items", []))

    print(f"  全 {len(items)} 件取得完了。              ")
    return items


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ローカルデータの読み込み
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def extract_addon_id(marketplace_url: str) -> str | None:
    """marketplaceUrl から addOnId を抽出する。"""
    if not marketplace_url:
        return None
    m = re.search(r"addOnId=([^&]+)", marketplace_url)
    return m.group(1) if m else None


def load_local(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_local_index(db: dict) -> dict[str, dict]:
    """addOnId → エントリ の辞書を返す。"""
    index = {}
    for addon in db.get("addons", []):
        aid = extract_addon_id(addon.get("marketplaceUrl", ""))
        if aid:
            index[aid] = addon
    return index


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 新規エントリ生成
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def make_entry(item: dict, existing_ids: set) -> dict:
    """API の 1 item から addons_data.json エントリを生成する。"""
    addon_id = item.get("addonId", "")
    metadata = item.get("addon", {}).get("localizedMetadata", {})

    name_en = metadata.get("name", "").strip()
    description = metadata.get("description", "").strip()
    keywords_en = [kw.strip() for kw in (metadata.get("keywords") or []) if kw.strip()]

    slug_base = slugify(name_en, fallback=addon_id)
    slug = unique_slug(slug_base, existing_ids)
    existing_ids.add(slug)

    return {
        "id": slug,
        "addOnId": addon_id,
        "nameEn": name_en,
        "nameJa": "",
        "nameKo": "",
        "category": DEFAULT_CATEGORY,
        "categoryJa": DEFAULT_CATEGORY_JA,
        "description": description,
        "descriptionEn": description,
        "descriptionJa": "",
        "descriptionKo": "",
        "keywords": list(keywords_en),
        "keywordsEn": list(keywords_en),
        # keywordsJa == keywordsEn にすることで translate_keywords.py が処理対象と判定する
        "keywordsJa": list(keywords_en),
        "keywordsKo": list(keywords_en),
        "featured": False,
        "marketplaceUrl": MARKETPLACE_URL_TEMPLATE.format(addon_id),
    }


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
        description="Adobe Express アドオンカタログを API から同期する"
    )
    parser.add_argument(
        "--token",
        required=True,
        help='Authorization ヘッダー値（例: "Bearer eyJ..."）',
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="ファイル書き込みなしで差分確認のみ",
    )
    args = parser.parse_args()

    # "Bearer " プレフィックスがなければ自動付与
    token = args.token.strip()
    if not token.startswith("Bearer "):
        token = "Bearer " + token

    # ── 1. ローカルデータ読み込み ──────────────────────────
    print(f"ローカルデータを読み込み中: {SRC_PATH}")
    db = load_local(SRC_PATH)
    local_index = build_local_index(db)
    existing_ids = {addon["id"] for addon in db.get("addons", [])}
    print(f"  ローカル: {len(db['addons'])} 件（addOnId 付き: {len(local_index)} 件）")

    # ── 2. API 全件取得 ────────────────────────────────────
    print("\nAPI からアドオン一覧を取得中...")
    api_items = fetch_all_addons(token)

    # PUBLIC のみフィルター
    public_items = [it for it in api_items if it.get("visibility") == "PUBLIC"]
    print(f"  PUBLIC フィルター後: {len(public_items)} 件（全 {len(api_items)} 件中）")

    # API の addOnId セット
    api_ids = {it["addonId"] for it in public_items if it.get("addonId")}

    # ── 3. 差分計算 ────────────────────────────────────────
    new_ids = api_ids - set(local_index.keys())
    removed_ids = set(local_index.keys()) - api_ids

    print(f"\n--- 差分サマリー ---")
    print(f"  新規: {len(new_ids)} 件")
    print(f"  削除済み（ローカルのみ / 警告のみ）: {len(removed_ids)} 件")

    if removed_ids:
        print("\n[WARNING] 以下の addOnId はローカルにあるが API に存在しません:")
        for aid in sorted(removed_ids):
            local_entry = local_index[aid]
            print(f"  - {aid}  ({local_entry.get('nameEn', '')})")
        print("  → 削除は自動では行いません。必要なら手動で対応してください。")

    if not new_ids:
        print("\n新規エントリはありません。終了します。")
        return

    # ── 4. 新規エントリ生成 ────────────────────────────────
    print(f"\n新規エントリを生成中...")
    new_items_by_id = {it["addonId"]: it for it in public_items if it.get("addonId") in new_ids}

    new_entries = []
    for api_id in sorted(new_ids):
        item = new_items_by_id[api_id]
        entry = make_entry(item, existing_ids)
        new_entries.append(entry)
        print(f"  + {entry['id']}  ({entry['nameEn']})")

    # ── 5. dry-run なら終了 ────────────────────────────────
    if args.dry_run:
        print(f"\n[DRY-RUN] ファイルは変更しません。{len(new_entries)} 件が追加される予定です。")
        return

    # ── 6. データ更新・書き込み ────────────────────────────
    db["addons"].extend(new_entries)

    # metadata 更新
    if "metadata" not in db:
        db["metadata"] = {}
    db["metadata"]["totalCount"] = len(db["addons"])
    db["metadata"]["lastUpdated"] = date.today().isoformat()

    print(f"\nファイルに書き込み中...")
    atomic_write(SRC_PATH, db)
    print(f"  書き込み完了: {SRC_PATH}")
    atomic_write(DOCS_PATH, db)
    print(f"  書き込み完了: {DOCS_PATH}")

    # ── 7. 完了サマリー ────────────────────────────────────
    total_after = len(db["addons"])
    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  完了: {len(new_entries)} 件追加（合計 {total_after} 件）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

次のステップ:
  1. python3 scripts/translate_keywords.py
       → keywordsJa / keywordsKo を辞書翻訳

  2. 新規エントリを手動補完
       → category / nameJa / descriptionJa など

  3. git diff src/ui/data/addons_data.json で差分確認

  4. git add src/ui/data/addons_data.json docs/addons_data.json
     git commit -m "chore: sync addon catalog ({len(new_entries)} new)"
""")


if __name__ == "__main__":
    main()

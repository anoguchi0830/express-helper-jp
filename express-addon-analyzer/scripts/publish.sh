#!/usr/bin/env bash
# 開発コピー index.html を公開用リポジトリへ同期して push する。
# 使い方: scripts/publish.sh [--dry-run] [コミットメッセージ]
set -euo pipefail

SRC="$(cd "$(dirname "$0")/.." && pwd)/index.html"
DEST_DIR="${PUBLISH_DIR:-/Volumes/Laxar/Projects/addon-analyzer}"
DRY=0
[ "${1:-}" = "--dry-run" ] && { DRY=1; shift; }
MSG="${1:-index.html を更新}"

[ -f "$SRC" ] || { echo "index.html が見つかりません: $SRC" >&2; exit 1; }
git -C "$DEST_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "公開用リポジトリがありません: $DEST_DIR" >&2; exit 1; }
git -C "$DEST_DIR" remote get-url origin | grep -q 'addon-analyzer' || { echo "origin が addon-analyzer ではありません" >&2; exit 1; }

# プライバシー保証（外部送信なし）を壊す変更を公開前に止める
if grep -nE "fetch\(|XMLHttpRequest|sendBeacon|WebSocket|<script[^>]+src=|<link[^>]+href=|https?://" "$SRC"; then
  echo "中止: 外部通信・外部読み込みの疑いがある記述があります（上記）。README のプライバシー説明と矛盾します。" >&2
  exit 1
fi

cd "$DEST_DIR"
[ -z "$(git status --porcelain | grep -v ' index.html$' || true)" ] || { echo "公開用リポジトリに index.html 以外の未コミット変更があります" >&2; git status --short >&2; exit 1; }
git pull --ff-only -q

cp "$SRC" "$DEST_DIR/index.html"
if git diff --quiet -- index.html; then echo "変更なし（公開版と同一）"; exit 0; fi

git diff --stat -- index.html
if [ "$DRY" = 1 ]; then git checkout -q -- index.html; echo "[dry-run] 反映せず元に戻しました"; exit 0; fi

git add index.html
git commit -q -m "$MSG"
git push -q origin main
echo "公開しました: https://analyzer.notechlabs.com （反映まで数分）"

#!/usr/bin/env python3
"""Open an X compose window for the first post of a Gemini-generated thread,
then copy the following posts to the clipboard one by one.

Usage: copy the Gemini `xpost` output, then run
    ./venv/bin/python scripts/xpost_open.py

Nothing is posted automatically; the final "Post" click is always manual.
"""
import re
import subprocess
import sys
import urllib.parse

MAX_WEIGHT = 280
URL_WEIGHT = 23
SEPARATOR_RE = re.compile(r"^\s*[─━\-—]{3,}\s*$")
LABEL_RE = re.compile(r"^\s*【(?:Hook|\d+/\d+)】\s*$")
URL_RE = re.compile(r"https?://\S+")
# Code point ranges that count as weight 1 on X (everything else is 2).
LIGHT_RANGES = ((0, 4351), (8192, 8205), (8208, 8223), (8242, 8247))


def _char_weight(ch):
    cp = ord(ch)
    return 1 if any(lo <= cp <= hi for lo, hi in LIGHT_RANGES) else 2


def weighted_length(text):
    """Return X's weighted length (URLs count as 23)."""
    total = 0
    pos = 0
    for m in URL_RE.finditer(text):
        total += sum(_char_weight(c) for c in text[pos:m.start()]) + URL_WEIGHT
        pos = m.end()
    total += sum(_char_weight(c) for c in text[pos:])
    return total


def parse_posts(raw):
    """Split Gemini output into posts.

    - Blocks are separated by rule lines; text before the first rule is dropped
      when at least one rule exists.
    - A leading label line (【Hook】/【n/N】) is removed from each block.
    """
    lines = raw.splitlines()
    blocks, current, seen_rule = [], [], False
    for line in lines:
        if SEPARATOR_RE.match(line):
            if seen_rule:
                blocks.append(current)
            seen_rule = True
            current = []
        else:
            current.append(line)
    if seen_rule:
        blocks.append(current)
    else:
        blocks = [lines]

    posts = []
    for block in blocks:
        while block and not block[0].strip():
            block = block[1:]
        if block and LABEL_RE.match(block[0]):
            block = block[1:]
        # Terminal copy pads lines with indentation / trailing spaces; drop them.
        text = "\n".join(line.strip() for line in block).strip()
        if text:
            posts.append(text)
    return posts


def intent_url(text):
    return "https://x.com/intent/post?text=" + urllib.parse.quote(text, safe="")


def read_clipboard():
    return subprocess.run(["pbpaste"], capture_output=True, text=True, check=True).stdout


def write_clipboard(text):
    subprocess.run(["pbcopy"], input=text, text=True, check=True)


def main():
    raw = read_clipboard()
    if not raw.strip():
        print("[ERROR] クリップボードが空です。Gemini の出力をコピーしてから実行してください。")
        return 1
    posts = parse_posts(raw)
    if not posts:
        print("[ERROR] 投稿文を検出できませんでした。")
        return 1

    print(f"{len(posts)} 件のポストを検出しました。")
    for i, p in enumerate(posts, 1):
        w = weighted_length(p)
        flag = "  [警告] 280 超過" if w > MAX_WEIGHT else ""
        print(f"  {i}/{len(posts)}: {w} 文字{flag}")

    subprocess.run(["open", intent_url(posts[0])], check=True)
    print("1つ目の投稿画面を開きました。内容を確認して「ポスト」を押してください。")

    for i, p in enumerate(posts[1:], 2):
        try:
            input(f"\n[Enter] で {i}/{len(posts)} をクリップボードへコピー (Ctrl+C で中断)")
        except (KeyboardInterrupt, EOFError):
            print("\n中断しました。")
            return 0
        write_clipboard(p)
        print(f"{i}/{len(posts)} をコピーしました。スレッドに「ポストを追加」して貼り付けてください。")
    print("\n完了。")
    return 0


if __name__ == "__main__":
    sys.exit(main())

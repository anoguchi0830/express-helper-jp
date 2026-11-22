import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import xpost_open as x  # noqa: E402

SEP = "──────"
SAMPLE = f"""本日追加された 16 件のアドオンをもとに作成しました。
{SEP}
【Hook】
本日 Adobe Express に 16 件のアドオン追加！🧵👇
{SEP}
1/6 🤖AI生成・画像編集
🔸AI Image - 画像をAI生成
{SEP}
2/6 📊データ連携
🔸Bulk QR Code - QRコード一括作成
{SEP}
3/6 📅計画
🔸Sequent - ガントチャート作成
{SEP}
4/6 🎨シェイプ
🔸Blobs - ブロブ生成
{SEP}
5/6 ✨アニメ
🔸Sliding Letters - 文字アニメ
{SEP}
【6/6】
🔗 Addon Explorer で試す
https://t.co/zvAFTsZRGI

#AdobeExpress #アドオン

※ 紹介内容は説明文をもとに作成。
"""


class ParseTest(unittest.TestCase):
    def test_sample_splits_into_seven(self):
        posts = x.parse_posts(SAMPLE)
        self.assertEqual(len(posts), 7)
        self.assertTrue(posts[0].startswith("本日 Adobe Express"))
        self.assertNotIn("【Hook】", posts[0])
        self.assertTrue(posts[1].startswith("1/6"))
        self.assertNotIn("【6/6】", posts[6])
        self.assertTrue(posts[6].endswith("作成。"))
        self.assertFalse(any("作成しました" in p for p in posts))

    def test_single_post_without_rule(self):
        self.assertEqual(x.parse_posts("こんにちは\n#tag"), ["こんにちは\n#tag"])

    def test_strips_terminal_padding(self):
        raw = f"{SEP}\n1/2 title      \n  🔸item one          \n  🔸item two   \n{SEP}\nlast  \n"
        posts = x.parse_posts(raw)
        self.assertEqual(posts, ["1/2 title\n🔸item one\n🔸item two", "last"])

    def test_empty(self):
        self.assertEqual(x.parse_posts("   \n"), [])


class LengthTest(unittest.TestCase):
    def test_ascii_and_japanese(self):
        self.assertEqual(x.weighted_length("abc"), 3)
        self.assertEqual(x.weighted_length("あい"), 4)

    def test_url_counts_23(self):
        self.assertEqual(x.weighted_length("https://example.com/very/long/path?q=1"), 23)
        self.assertEqual(x.weighted_length("a https://t.co/x"), 2 + 23)

    def test_over_limit_detected(self):
        self.assertGreater(x.weighted_length("あ" * 141), x.MAX_WEIGHT)
        self.assertLessEqual(x.weighted_length("あ" * 140), x.MAX_WEIGHT)


class UrlTest(unittest.TestCase):
    def test_encoding(self):
        u = x.intent_url("a&b #c\n日本")
        self.assertTrue(u.startswith("https://x.com/intent/post?text="))
        self.assertNotIn(" ", u)
        self.assertNotIn("#", u.split("text=")[1])
        self.assertNotIn("&", u.split("text=")[1])


if __name__ == "__main__":
    unittest.main()

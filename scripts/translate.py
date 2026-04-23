#!/usr/bin/env python3
"""
addons_data.json の descriptionJa/Ko と keywordsJa/Ko を翻訳する。

モード:
  デフォルト  Claude API で description + keywords を翻訳
  --dict     静的辞書でキーワードのみ翻訳（API 不要）

使い方:
  python3 scripts/translate.py                 # API モード（全件）
  python3 scripts/translate.py --dry-run       # 翻訳対象を確認のみ
  python3 scripts/translate.py --dict          # 辞書モード（API 不要）
  python3 scripts/translate.py --dict --dry-run

  export ANTHROPIC_API_KEY="sk-ant-..."  # API モードに必要
"""
import json
import os
import re
import sys
import time
import argparse
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# パス定数
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SRC_PATH   = "src/ui/data/addons_data.json"
DOCS_PATH  = "docs/addons_data.json"
API_URL    = "https://api.anthropic.com/v1/messages"
MODEL      = "claude-haiku-4-5"
BATCH_SIZE = 20


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 静的辞書（--dict モード用）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHRASE_JA = {
    "qr code": "QRコード", "qr codes": "QRコード",
    "bar code": "バーコード", "barcode": "バーコード",
    "text to speech": "テキスト読み上げ", "text-to-speech": "テキスト読み上げ",
    "speech to text": "音声テキスト変換", "speech-to-text": "音声テキスト変換",
    "tts": "テキスト読み上げ",
    "background removal": "背景除去", "background remove": "背景除去",
    "background remover": "背景除去ツール",
    "image generator": "画像生成", "image generation": "画像生成",
    "ai image": "AI画像", "ai images": "AI画像",
    "ai art": "AIアート", "ai design": "AIデザイン",
    "ai video": "AI動画", "ai audio": "AIオーディオ",
    "ai music": "AI音楽", "ai voice": "AI音声",
    "ai avatar": "AIアバター", "ai animation": "AIアニメーション",
    "ai background": "AI背景", "ai photo": "AI写真",
    "ai generate": "AI生成", "ai generated": "AI生成",
    "ai generation": "AI生成", "ai generative": "AI生成",
    "ai icon": "AIアイコン", "ai logo": "AIロゴ",
    "ai text": "AIテキスト", "ai writing": "AI文章生成",
    "ai caption": "AIキャプション", "ai captions": "AIキャプション",
    "ai face": "AI顔", "ai headshot": "AIヘッドショット",
    "ai sticker": "AIステッカー", "ai emoji": "AI絵文字",
    "ai comic": "AIコミック", "ai drawing": "AI描画",
    "ai enhance": "AI高画質化", "ai upscale": "AIアップスケール",
    "ai dubbing": "AI吹き替え", "ai subtitle": "AI字幕",
    "ai translate": "AI翻訳", "ai translation": "AI翻訳",
    "ai assistant": "AIアシスタント", "ai tool": "AIツール",
    "ai tools": "AIツール", "ai model": "AIモデル",
    "ai content": "AIコンテンツ", "ai creator": "AIクリエイター",
    "artificial intelligence": "人工知能",
    "machine learning": "機械学習",
    "deep learning": "ディープラーニング",
    "generative ai": "生成AI",
    "stable diffusion": "Stable Diffusion",
    "stock photo": "ストック写真", "stock photos": "ストック写真",
    "stock image": "ストック画像", "stock images": "ストック画像",
    "icon pack": "アイコンパック", "icon set": "アイコンセット",
    "icon library": "アイコンライブラリ",
    "photo editing": "写真編集", "photo editor": "写真エディター",
    "photo filter": "写真フィルター",
    "image editing": "画像編集", "image editor": "画像エディター",
    "video editing": "動画編集", "video editor": "動画エディター",
    "video generator": "動画生成ツール",
    "audio editing": "音声編集", "audio editor": "音声エディター",
    "color picker": "カラーピッカー", "color palette": "カラーパレット",
    "color scheme": "カラースキーム", "colour scheme": "カラースキーム",
    "color contrast": "色コントラスト", "colour contrast": "色コントラスト",
    "font pairing": "フォントペアリング", "font library": "フォントライブラリ",
    "font generator": "フォント生成", "custom font": "カスタムフォント",
    "google font": "Googleフォント", "google fonts": "Googleフォント",
    "text effect": "テキストエフェクト", "text effects": "テキストエフェクト",
    "text style": "テキストスタイル", "text styles": "テキストスタイル",
    "text art": "テキストアート", "word art": "ワードアート",
    "gradient text": "グラデーションテキスト",
    "neon text": "ネオンテキスト", "neon effect": "ネオンエフェクト",
    "curved text": "曲線テキスト", "3d text": "3Dテキスト",
    "social media": "ソーシャルメディア",
    "social post": "ソーシャル投稿",
    "brand kit": "ブランドキット", "brand identity": "ブランドアイデンティティ",
    "brand guidelines": "ブランドガイドライン", "brand assets": "ブランドアセット",
    "brand management": "ブランド管理",
    "asset management": "アセット管理", "digital asset": "デジタルアセット",
    "project management": "プロジェクト管理", "task management": "タスク管理",
    "content creation": "コンテンツ制作", "content creator": "コンテンツクリエイター",
    "photo studio": "フォトスタジオ", "design studio": "デザインスタジオ",
    "design tool": "デザインツール", "design tools": "デザインツール",
    "design template": "デザインテンプレート", "design templates": "デザインテンプレート",
    "design asset": "デザインアセット", "design assets": "デザインアセット",
    "design element": "デザイン要素", "design elements": "デザイン要素",
    "graphic design": "グラフィックデザイン", "graphic designer": "グラフィックデザイナー",
    "illustration pack": "イラストパック",
    "vector art": "ベクターアート", "vector graphics": "ベクターグラフィック",
    "vector illustration": "ベクターイラスト",
    "sticker pack": "ステッカーパック", "sticker maker": "ステッカーメーカー",
    "emoji pack": "絵文字パック",
    "color blind": "色覚異常", "colour blind": "色覚異常",
    "color blindness": "色覚異常", "colour blindness": "色覚異常",
    "screen reader": "スクリーンリーダー",
    "wcag": "WCAG", "wcag compliance": "WCAGコンプライアンス",
    "accessibility checker": "アクセシビリティチェッカー",
    "cloud storage": "クラウドストレージ",
    "google drive": "Google ドライブ",
    "one drive": "OneDrive", "onedrive": "OneDrive",
    "adobe express": "Adobe Express",
    "adobe acrobat": "Adobe Acrobat",
    "product photo": "商品写真", "product photography": "商品撮影",
    "product mockup": "商品モックアップ",
    "email marketing": "メールマーケティング",
    "email template": "メールテンプレート",
    "qr code generator": "QRコードジェネレーター",
    "word cloud": "ワードクラウド", "word clouds": "ワードクラウド",
    "mind map": "マインドマップ", "flow chart": "フローチャート",
    "infographic": "インフォグラフィック", "infographics": "インフォグラフィック",
    "pie chart": "円グラフ", "bar chart": "棒グラフ", "line chart": "折れ線グラフ",
    "data visualization": "データ可視化",
    "virtual background": "バーチャル背景",
    "green screen": "グリーンスクリーン",
    "pixel art": "ピクセルアート", "pixel arts": "ピクセルアート",
    "8-bit art": "8ビットアート",
    "lip sync": "リップシンク",
    "face swap": "顔交換", "face swapping": "顔交換",
    "avatar creator": "アバタークリエイター",
    "korean": "韓国語", "japanese": "日本語", "chinese": "中国語",
    "multilingual": "多言語", "translation": "翻訳",
    "business card": "名刺", "business cards": "名刺",
    "greeting card": "グリーティングカード",
    "social sharing": "ソーシャル共有",
    "adobe express add-on": "Adobe Expressアドオン",
    "add-on": "アドオン", "add on": "アドオン", "add-ons": "アドオン",
    "pdf export": "PDFエクスポート", "pdf creator": "PDF作成",
    "label maker": "ラベルメーカー",
    "photo booth": "フォトブース", "photo collage": "フォトコラージュ",
    "photo frame": "フォトフレーム",
    "map maker": "マップメーカー",
    "wix": "Wix", "shopify": "Shopify", "canva": "Canva",
    "music library": "音楽ライブラリ", "royalty free music": "ロイヤリティフリー音楽",
    "sound effect": "サウンドエフェクト", "sound effects": "サウンドエフェクト",
    "voiceover": "ナレーション", "voice over": "ナレーション",
    "text generator": "テキスト生成", "image upscaler": "画像アップスケーラー",
    "background generator": "背景生成",
    "logo maker": "ロゴメーカー", "logo creator": "ロゴクリエイター",
    "logo generator": "ロゴジェネレーター",
    "meme generator": "ミームジェネレーター", "meme maker": "ミームメーカー",
    "gif maker": "GIFメーカー", "gif creator": "GIFクリエイター",
    "pattern maker": "パターンメーカー",
    "mockup generator": "モックアップジェネレーター",
    "resume builder": "履歴書ビルダー",
    "form builder": "フォームビルダー",
    "chart maker": "チャートメーカー",
    "calendar maker": "カレンダーメーカー",
    "e-commerce": "Eコマース", "ecommerce": "Eコマース",
    "print on demand": "プリントオンデマンド",
    "3d model": "3Dモデル", "3d models": "3Dモデル",
    "3d shape": "3D形状", "3d shapes": "3D形状",
    "3d icon": "3Dアイコン", "3d icons": "3Dアイコン",
    "3d effects": "3Dエフェクト",
    "photo background": "写真背景",
    "remove background": "背景除去",
    "cutout": "切り抜き", "cut out": "切り抜き",
}

PHRASE_KO = {
    "qr code": "QR코드", "qr codes": "QR코드",
    "bar code": "바코드", "barcode": "바코드",
    "text to speech": "텍스트 음성 변환", "text-to-speech": "텍스트 음성 변환",
    "speech to text": "음성 텍스트 변환", "speech-to-text": "음성 텍스트 변환",
    "tts": "TTS",
    "background removal": "배경 제거", "background remove": "배경 제거",
    "background remover": "배경 제거 도구",
    "image generator": "이미지 생성", "image generation": "이미지 생성",
    "ai image": "AI 이미지", "ai images": "AI 이미지",
    "ai art": "AI 아트", "ai design": "AI 디자인",
    "ai video": "AI 동영상", "ai audio": "AI 오디오",
    "ai music": "AI 음악", "ai voice": "AI 음성",
    "ai avatar": "AI 아바타", "ai animation": "AI 애니메이션",
    "ai background": "AI 배경", "ai photo": "AI 사진",
    "ai generate": "AI 생성", "ai generated": "AI 생성",
    "ai generation": "AI 생성", "ai generative": "AI 생성형",
    "ai icon": "AI 아이콘", "ai logo": "AI 로고",
    "ai text": "AI 텍스트", "ai writing": "AI 글쓰기",
    "ai caption": "AI 캡션", "ai captions": "AI 캡션",
    "ai face": "AI 얼굴", "ai headshot": "AI 증명사진",
    "ai sticker": "AI 스티커", "ai emoji": "AI 이모지",
    "ai comic": "AI 만화", "ai drawing": "AI 그림",
    "ai enhance": "AI 화질 향상", "ai upscale": "AI 업스케일",
    "ai dubbing": "AI 더빙", "ai subtitle": "AI 자막",
    "ai translate": "AI 번역", "ai translation": "AI 번역",
    "ai assistant": "AI 어시스턴트", "ai tool": "AI 도구",
    "ai tools": "AI 도구", "ai model": "AI 모델",
    "ai content": "AI 콘텐츠", "ai creator": "AI 크리에이터",
    "artificial intelligence": "인공지능",
    "machine learning": "머신러닝",
    "deep learning": "딥러닝",
    "generative ai": "생성형 AI",
    "stable diffusion": "Stable Diffusion",
    "stock photo": "스톡 사진", "stock photos": "스톡 사진",
    "stock image": "스톡 이미지", "stock images": "스톡 이미지",
    "icon pack": "아이콘 팩", "icon set": "아이콘 세트",
    "icon library": "아이콘 라이브러리",
    "photo editing": "사진 편집", "photo editor": "사진 편집기",
    "photo filter": "사진 필터",
    "image editing": "이미지 편집", "image editor": "이미지 편집기",
    "video editing": "동영상 편집", "video editor": "동영상 편집기",
    "video generator": "동영상 생성 도구",
    "audio editing": "오디오 편집", "audio editor": "오디오 편집기",
    "color picker": "색상 선택기", "color palette": "색상 팔레트",
    "color scheme": "색상 구성표", "colour scheme": "색상 구성표",
    "color contrast": "색상 대비", "colour contrast": "색상 대비",
    "font pairing": "폰트 페어링", "font library": "폰트 라이브러리",
    "font generator": "폰트 생성기", "custom font": "맞춤 폰트",
    "google font": "Google 폰트", "google fonts": "Google 폰트",
    "text effect": "텍스트 효과", "text effects": "텍스트 효과",
    "text style": "텍스트 스타일", "text styles": "텍스트 스타일",
    "text art": "텍스트 아트", "word art": "워드 아트",
    "gradient text": "그라데이션 텍스트",
    "neon text": "네온 텍스트", "neon effect": "네온 효과",
    "curved text": "곡선 텍스트", "3d text": "3D 텍스트",
    "social media": "소셜 미디어",
    "social post": "소셜 게시물",
    "brand kit": "브랜드 키트", "brand identity": "브랜드 아이덴티티",
    "brand guidelines": "브랜드 가이드라인", "brand assets": "브랜드 에셋",
    "brand management": "브랜드 관리",
    "asset management": "에셋 관리", "digital asset": "디지털 에셋",
    "project management": "프로젝트 관리", "task management": "업무 관리",
    "content creation": "콘텐츠 제작", "content creator": "콘텐츠 크리에이터",
    "photo studio": "포토 스튜디오", "design studio": "디자인 스튜디오",
    "design tool": "디자인 도구", "design tools": "디자인 도구",
    "design template": "디자인 템플릿", "design templates": "디자인 템플릿",
    "design asset": "디자인 에셋", "design assets": "디자인 에셋",
    "design element": "디자인 요소", "design elements": "디자인 요소",
    "graphic design": "그래픽 디자인", "graphic designer": "그래픽 디자이너",
    "illustration pack": "일러스트 팩",
    "vector art": "벡터 아트", "vector graphics": "벡터 그래픽",
    "vector illustration": "벡터 일러스트",
    "sticker pack": "스티커 팩", "sticker maker": "스티커 메이커",
    "emoji pack": "이모지 팩",
    "color blind": "색맹", "colour blind": "색맹",
    "color blindness": "색맹", "colour blindness": "색맹",
    "screen reader": "스크린 리더",
    "wcag": "WCAG", "wcag compliance": "WCAG 준수",
    "accessibility checker": "접근성 검사기",
    "cloud storage": "클라우드 스토리지",
    "google drive": "Google 드라이브",
    "one drive": "OneDrive", "onedrive": "OneDrive",
    "adobe express": "Adobe Express",
    "adobe acrobat": "Adobe Acrobat",
    "product photo": "상품 사진", "product photography": "상품 촬영",
    "product mockup": "상품 목업",
    "email marketing": "이메일 마케팅",
    "email template": "이메일 템플릿",
    "qr code generator": "QR코드 생성기",
    "word cloud": "워드 클라우드", "word clouds": "워드 클라우드",
    "mind map": "마인드맵", "flow chart": "플로우차트",
    "infographic": "인포그래픽", "infographics": "인포그래픽",
    "pie chart": "원형 차트", "bar chart": "막대 차트", "line chart": "선형 차트",
    "data visualization": "데이터 시각화",
    "virtual background": "가상 배경",
    "green screen": "그린 스크린",
    "pixel art": "픽셀 아트", "pixel arts": "픽셀 아트",
    "8-bit art": "8비트 아트",
    "lip sync": "립싱크",
    "face swap": "얼굴 교체", "face swapping": "얼굴 교체",
    "avatar creator": "아바타 크리에이터",
    "korean": "한국어", "japanese": "일본어", "chinese": "중국어",
    "multilingual": "다국어", "translation": "번역",
    "business card": "명함", "business cards": "명함",
    "greeting card": "인사 카드",
    "social sharing": "소셜 공유",
    "adobe express add-on": "Adobe Express 애드온",
    "add-on": "애드온", "add on": "애드온", "add-ons": "애드온",
    "pdf export": "PDF 내보내기", "pdf creator": "PDF 제작",
    "label maker": "라벨 메이커",
    "photo booth": "포토부스", "photo collage": "사진 콜라주",
    "photo frame": "사진 프레임",
    "map maker": "지도 제작",
    "wix": "Wix", "shopify": "Shopify", "canva": "Canva",
    "music library": "음악 라이브러리", "royalty free music": "로열티 프리 음악",
    "sound effect": "사운드 이펙트", "sound effects": "사운드 이펙트",
    "voiceover": "나레이션", "voice over": "나레이션",
    "text generator": "텍스트 생성기", "image upscaler": "이미지 업스케일러",
    "background generator": "배경 생성기",
    "logo maker": "로고 메이커", "logo creator": "로고 크리에이터",
    "logo generator": "로고 생성기",
    "meme generator": "밈 생성기", "meme maker": "밈 메이커",
    "gif maker": "GIF 메이커", "gif creator": "GIF 크리에이터",
    "pattern maker": "패턴 메이커",
    "mockup generator": "목업 생성기",
    "resume builder": "이력서 빌더",
    "form builder": "폼 빌더",
    "chart maker": "차트 메이커",
    "calendar maker": "캘린더 메이커",
    "e-commerce": "전자상거래", "ecommerce": "전자상거래",
    "print on demand": "주문형 인쇄",
    "3d model": "3D 모델", "3d models": "3D 모델",
    "3d shape": "3D 도형", "3d shapes": "3D 도형",
    "3d icon": "3D 아이콘", "3d icons": "3D 아이콘",
    "3d effects": "3D 효과",
    "photo background": "사진 배경",
    "remove background": "배경 제거",
    "cutout": "누끼", "cut out": "누끼",
}

WORD_JA = {
    "ai": "AI", "image": "画像", "images": "画像",
    "text": "テキスト", "video": "動画", "videos": "動画",
    "design": "デザイン", "generator": "ジェネレーター",
    "photo": "写真", "photos": "写真",
    "art": "アート", "qr": "QR", "code": "コード",
    "music": "音楽", "voice": "音声",
    "icon": "アイコン", "icons": "アイコン",
    "logo": "ロゴ", "logos": "ロゴ",
    "effect": "エフェクト", "effects": "エフェクト",
    "audio": "オーディオ", "maker": "メーカー",
    "sound": "サウンド", "speech": "スピーチ",
    "gen": "生成", "content": "コンテンツ",
    "avatar": "アバター", "free": "無料",
    "color": "カラー", "colour": "カラー",
    "pixel": "ピクセル", "pixels": "ピクセル",
    "media": "メディア", "generate": "生成",
    "animation": "アニメーション", "animated": "アニメーション",
    "adobe": "Adobe", "stock": "ストック",
    "emoji": "絵文字", "emojis": "絵文字",
    "express": "Express",
    "editor": "エディター", "editing": "編集",
    "tool": "ツール", "tools": "ツール",
    "svg": "SVG", "background": "背景",
    "pdf": "PDF", "generation": "生成",
    "custom": "カスタム", "brand": "ブランド",
    "barcode": "バーコード", "calendar": "カレンダー",
    "mask": "マスク", "character": "キャラクター",
    "asset": "アセット", "assets": "アセット",
    "product": "製品", "creative": "クリエイティブ",
    "business": "ビジネス", "social": "ソーシャル",
    "email": "メール", "creator": "クリエイター",
    "branding": "ブランディング", "digital": "デジタル",
    "mockup": "モックアップ", "mockups": "モックアップ",
    "visual": "ビジュアル", "export": "エクスポート",
    "pattern": "パターン", "patterns": "パターン",
    "illustration": "イラスト", "illustrations": "イラスト",
    "sticker": "ステッカー", "stickers": "ステッカー",
    "meme": "ミーム", "memes": "ミーム",
    "print": "印刷", "filter": "フィルター", "filters": "フィルター",
    "style": "スタイル", "styles": "スタイル",
    "portrait": "ポートレート", "generative": "生成AI",
    "3d": "3D", "png": "PNG", "gif": "GIF", "jpg": "JPEG",
    "accessibility": "アクセシビリティ",
    "template": "テンプレート", "templates": "テンプレート",
    "marketing": "マーケティング",
    "creation": "制作", "create": "作成", "creating": "作成",
    "edit": "編集", "grid": "グリッド",
    "chart": "チャート", "charts": "チャート",
    "map": "マップ", "maps": "マップ",
    "table": "テーブル", "tables": "テーブル",
    "data": "データ", "contrast": "コントラスト",
    "instagram": "Instagram", "facebook": "Facebook",
    "twitter": "Twitter", "tiktok": "TikTok",
    "linkedin": "LinkedIn", "youtube": "YouTube",
    "pinterest": "Pinterest", "spotify": "Spotify",
    "soundcloud": "SoundCloud", "dropbox": "Dropbox",
    "builder": "ビルダー", "studio": "スタジオ",
    "virtual": "バーチャル", "vector": "ベクター", "vectors": "ベクター",
    "translate": "翻訳", "anime": "アニメ",
    "app": "アプリ", "apps": "アプリ",
    "game": "ゲーム", "games": "ゲーム",
    "shape": "形状", "shapes": "形状",
    "frame": "フレーム", "frames": "フレーム",
    "border": "ボーダー", "borders": "ボーダー",
    "font": "フォント", "fonts": "フォント",
    "typeface": "書体",
    "typography": "タイポグラフィ",
    "render": "レンダリング", "rendering": "レンダリング",
    "import": "インポート", "resize": "リサイズ",
    "enhance": "高画質化", "upscale": "アップスケール",
    "compress": "圧縮", "convert": "変換",
    "crop": "トリミング", "rotate": "回転",
    "flip": "反転", "blur": "ぼかし",
    "sharpen": "シャープ", "brightness": "明度",
    "saturation": "彩度", "hue": "色相",
    "transparent": "透明", "opacity": "不透明度",
    "layer": "レイヤー", "layers": "レイヤー",
    "gradient": "グラデーション", "gradients": "グラデーション",
    "texture": "テクスチャ", "textures": "テクスチャ",
    "overlay": "オーバーレイ",
    "collage": "コラージュ",
    "banner": "バナー", "banners": "バナー",
    "poster": "ポスター", "posters": "ポスター",
    "flyer": "フライヤー", "flyers": "フライヤー",
    "brochure": "パンフレット",
    "presentation": "プレゼンテーション",
    "slide": "スライド", "slides": "スライド",
    "infographic": "インフォグラフィック",
    "newsletter": "ニュースレター",
    "thumbnail": "サムネイル", "thumbnails": "サムネイル",
    "watermark": "透かし",
    "caption": "キャプション", "captions": "キャプション",
    "subtitle": "字幕", "subtitles": "字幕",
    "transcript": "文字起こし",
    "record": "録音", "recording": "録音",
    "playback": "再生",
    "stream": "ストリーム", "streaming": "ストリーミング",
    "podcast": "ポッドキャスト",
    "dubbing": "吹き替え",
    "language": "言語", "languages": "言語",
    "international": "インターナショナル",
    "localization": "ローカライゼーション",
    "survey": "アンケート", "form": "フォーム",
    "quiz": "クイズ", "feedback": "フィードバック",
    "workflow": "ワークフロー",
    "approval": "承認", "review": "レビュー",
    "collaboration": "コラボレーション",
    "team": "チーム", "workspace": "ワークスペース",
    "organization": "組織",
    "integration": "統合", "connect": "接続",
    "sync": "同期", "upload": "アップロード",
    "download": "ダウンロード",
    "share": "共有", "sharing": "共有",
    "publish": "公開", "publishing": "出版",
    "printing": "印刷",
    "label": "ラベル", "labels": "ラベル",
    "tag": "タグ", "tags": "タグ",
    "category": "カテゴリ",
    "search": "検索", "discover": "発見",
    "explore": "探索",
    "library": "ライブラリ",
    "collection": "コレクション",
    "gallery": "ギャラリー",
    "portfolio": "ポートフォリオ",
    "showcase": "ショーケース",
    "premium": "プレミアム",
    "pro": "プロ", "plus": "プラス",
    "basic": "ベーシック", "standard": "スタンダード",
    "enterprise": "エンタープライズ",
    "a11y": "アクセシビリティ",
    "wcag": "WCAG", "aria": "ARIA",
    "responsive": "レスポンシブ",
    "mobile": "モバイル", "desktop": "デスクトップ",
    "web": "ウェブ", "website": "ウェブサイト",
    "ads": "広告", "ad": "広告", "advertising": "広告",
    "campaign": "キャンペーン",
    "analytics": "アナリティクス",
    "seo": "SEO",
    "conversion": "コンバージョン",
    "engagement": "エンゲージメント",
    "viral": "バイラル",
    "trending": "トレンド",
    "hashtag": "ハッシュタグ", "hashtags": "ハッシュタグ",
    "post": "投稿", "posts": "投稿",
    "story": "ストーリー", "stories": "ストーリー",
    "reel": "リール", "reels": "リール",
    "feed": "フィード",
    "profile": "プロフィール",
    "headshot": "ヘッドショット",
    "selfie": "セルフィー",
    "manga": "マンガ",
    "comic": "コミック", "cartoon": "カートゥーン",
    "sketch": "スケッチ", "drawing": "イラスト",
    "painting": "絵画", "artwork": "アートワーク",
    "abstract": "アブストラクト",
    "realistic": "リアリスティック",
    "vintage": "ヴィンテージ", "retro": "レトロ",
    "minimal": "ミニマル", "minimalist": "ミニマリスト",
    "flat": "フラット", "material": "マテリアル",
    "geometry": "ジオメトリ", "geometric": "ジオメトリック",
    "perspective": "透視図",
    "isometric": "アイソメトリック",
    "hand drawn": "手描き", "handdrawn": "手描き",
    "watercolor": "水彩", "watercolour": "水彩",
    "pencil": "鉛筆", "ink": "インク",
    "bokeh": "ボケ",
    "lut": "LUT", "preset": "プリセット", "presets": "プリセット",
    "remove": "除去", "remover": "除去ツール",
    "object": "オブジェクト", "objects": "オブジェクト",
    "tts": "テキスト読み上げ",
    "hanbok": "韓服",
    "clothes": "衣服",
    "fashion": "ファッション",
    "outfit": "コーディネート",
    "hairstyle": "ヘアスタイル",
    "beauty": "ビューティ",
    "makeup": "メイクアップ",
    "skin": "スキン",
    "face": "顔",
    "body": "ボディ",
    "nature": "自然",
    "animal": "動物", "animals": "動物",
    "food": "食べ物", "restaurant": "レストラン",
    "travel": "旅行",
    "architecture": "建築",
    "real estate": "不動産",
    "interior": "インテリア",
    "furniture": "家具",
    "education": "教育",
    "school": "学校",
    "children": "子ども",
    "kids": "キッズ",
    "family": "家族",
    "holiday": "ホリデー",
    "christmas": "クリスマス",
    "birthday": "誕生日",
    "wedding": "ウェディング",
    "event": "イベント", "events": "イベント",
    "invitation": "招待状", "invitations": "招待状",
    "certificate": "証明書", "certificates": "証明書",
    "award": "アワード", "badge": "バッジ", "badges": "バッジ",
    "stamp": "スタンプ", "stamps": "スタンプ",
    "signature": "署名",
    "monogram": "モノグラム",
    "doodle": "落書き", "doodles": "落書き",
    "clipart": "クリップアート",
    "element": "要素", "elements": "要素",
    "decoration": "デコレーション", "decorations": "デコレーション",
    "ornament": "オーナメント", "ornaments": "オーナメント",
    "divider": "区切り",
    "line": "ライン", "lines": "ライン",
    "dot": "ドット", "dots": "ドット",
    "circle": "サークル", "circles": "サークル",
    "triangle": "三角形",
    "square": "四角形",
    "star": "スター", "stars": "スター",
    "heart": "ハート", "hearts": "ハート",
    "arrow": "矢印", "arrows": "矢印",
    "check": "チェック",
    "cross": "クロス",
    "hd": "HD", "4k": "4K", "fhd": "FHD",
    "resolution": "解像度",
    "widescreen": "ワイドスクリーン",
    "device": "デバイス", "devices": "デバイス",
    "phone": "スマートフォン", "smartphone": "スマートフォン",
    "tablet": "タブレット", "laptop": "ラップトップ",
    "t-shirt": "Tシャツ", "tshirt": "Tシャツ",
    "cup": "カップ", "mug": "マグカップ",
    "bag": "バッグ", "tote": "トートバッグ",
    "packaging": "パッケージ",
    "box": "ボックス", "bottle": "ボトル",
    "book": "本", "books": "本",
    "magazine": "雑誌", "newspaper": "新聞",
    "report": "レポート",
    "document": "ドキュメント", "documents": "ドキュメント",
    "contract": "契約書",
    "invoice": "請求書",
    "receipt": "レシート",
    "schedule": "スケジュール",
    "plan": "プラン", "planning": "プランニング",
    "strategy": "戦略",
    "growth": "成長",
    "sales": "セールス",
    "profit": "利益",
    "graph": "グラフ",
    "diagram": "ダイアグラム",
    "timeline": "タイムライン",
    "roadmap": "ロードマップ",
    "brainstorm": "ブレインストーミング",
    "idea": "アイデア", "ideas": "アイデア",
    "inspiration": "インスピレーション",
    "wireframe": "ワイヤーフレーム",
    "prototype": "プロトタイプ",
    "ux": "UX", "ui": "UI",
    "interface": "インターフェース",
    "dashboard": "ダッシュボード",
    "component": "コンポーネント", "components": "コンポーネント",
    "kit": "キット",
    "plugin": "プラグイン", "plugins": "プラグイン",
    "extension": "エクステンション",
    "addon": "アドオン",
    "api": "API", "sdk": "SDK",
    "open source": "オープンソース",
    "commercial": "商用",
    "license": "ライセンス",
    "copyright": "著作権",
    "royalty": "ロイヤリティ",
    "community": "コミュニティ",
    "forum": "フォーラム",
    "support": "サポート",
    "tutorial": "チュートリアル",
    "guide": "ガイド",
    "documentation": "ドキュメント",
    "help": "ヘルプ",
}

WORD_KO = {
    "ai": "AI", "image": "이미지", "images": "이미지",
    "text": "텍스트", "video": "동영상", "videos": "동영상",
    "design": "디자인", "generator": "생성기",
    "photo": "사진", "photos": "사진",
    "art": "아트", "qr": "QR", "code": "코드",
    "music": "음악", "voice": "음성",
    "icon": "아이콘", "icons": "아이콘",
    "logo": "로고", "logos": "로고",
    "effect": "효과", "effects": "효과",
    "audio": "오디오", "maker": "메이커",
    "sound": "사운드", "speech": "음성",
    "gen": "생성", "content": "콘텐츠",
    "avatar": "아바타", "free": "무료",
    "color": "색상", "colour": "색상",
    "pixel": "픽셀", "pixels": "픽셀",
    "media": "미디어", "generate": "생성",
    "animation": "애니메이션", "animated": "애니메이션",
    "adobe": "Adobe", "stock": "스톡",
    "emoji": "이모지", "emojis": "이모지",
    "express": "Express",
    "editor": "편집기", "editing": "편집",
    "tool": "도구", "tools": "도구",
    "svg": "SVG", "background": "배경",
    "pdf": "PDF", "generation": "생성",
    "custom": "커스텀", "brand": "브랜드",
    "barcode": "바코드", "calendar": "캘린더",
    "mask": "마스크", "character": "캐릭터",
    "asset": "에셋", "assets": "에셋",
    "product": "제품", "creative": "크리에이티브",
    "business": "비즈니스", "social": "소셜",
    "email": "이메일", "creator": "크리에이터",
    "branding": "브랜딩", "digital": "디지털",
    "mockup": "목업", "mockups": "목업",
    "visual": "비주얼", "export": "내보내기",
    "pattern": "패턴", "patterns": "패턴",
    "illustration": "일러스트", "illustrations": "일러스트",
    "sticker": "스티커", "stickers": "스티커",
    "meme": "밈", "memes": "밈",
    "print": "인쇄", "filter": "필터", "filters": "필터",
    "style": "스타일", "styles": "스타일",
    "portrait": "인물사진", "generative": "생성형",
    "3d": "3D", "png": "PNG", "gif": "GIF", "jpg": "JPEG",
    "accessibility": "접근성",
    "template": "템플릿", "templates": "템플릿",
    "marketing": "마케팅",
    "creation": "제작", "create": "만들기", "creating": "만들기",
    "edit": "편집", "grid": "그리드",
    "chart": "차트", "charts": "차트",
    "map": "지도", "maps": "지도",
    "table": "표", "tables": "표",
    "data": "데이터", "contrast": "대비",
    "instagram": "Instagram", "facebook": "Facebook",
    "twitter": "Twitter", "tiktok": "TikTok",
    "linkedin": "LinkedIn", "youtube": "YouTube",
    "pinterest": "Pinterest", "spotify": "Spotify",
    "soundcloud": "SoundCloud", "dropbox": "Dropbox",
    "builder": "빌더", "studio": "스튜디오",
    "virtual": "가상", "vector": "벡터", "vectors": "벡터",
    "translate": "번역", "anime": "애니메",
    "app": "앱", "apps": "앱",
    "game": "게임", "games": "게임",
    "shape": "도형", "shapes": "도형",
    "frame": "프레임", "frames": "프레임",
    "border": "테두리", "borders": "테두리",
    "font": "폰트", "fonts": "폰트",
    "typeface": "서체",
    "typography": "타이포그래피",
    "render": "렌더링", "rendering": "렌더링",
    "import": "가져오기", "resize": "크기 조정",
    "enhance": "화질 향상", "upscale": "업스케일",
    "compress": "압축", "convert": "변환",
    "crop": "자르기", "rotate": "회전",
    "flip": "반전", "blur": "흐림",
    "sharpen": "선명화", "brightness": "밝기",
    "saturation": "채도", "hue": "색조",
    "transparent": "투명", "opacity": "불투명도",
    "layer": "레이어", "layers": "레이어",
    "gradient": "그라데이션", "gradients": "그라데이션",
    "texture": "텍스처", "textures": "텍스처",
    "overlay": "오버레이",
    "collage": "콜라주",
    "banner": "배너", "banners": "배너",
    "poster": "포스터", "posters": "포스터",
    "flyer": "전단지", "flyers": "전단지",
    "brochure": "브로셔",
    "presentation": "프레젠테이션",
    "slide": "슬라이드", "slides": "슬라이드",
    "infographic": "인포그래픽",
    "newsletter": "뉴스레터",
    "thumbnail": "썸네일", "thumbnails": "썸네일",
    "watermark": "워터마크",
    "caption": "캡션", "captions": "캡션",
    "subtitle": "자막", "subtitles": "자막",
    "transcript": "텍스트 변환",
    "record": "녹음", "recording": "녹음",
    "playback": "재생",
    "stream": "스트림", "streaming": "스트리밍",
    "podcast": "팟캐스트",
    "dubbing": "더빙",
    "language": "언어", "languages": "언어",
    "international": "국제",
    "localization": "현지화",
    "survey": "설문", "form": "양식",
    "quiz": "퀴즈", "feedback": "피드백",
    "workflow": "워크플로",
    "approval": "승인", "review": "검토",
    "collaboration": "협업",
    "team": "팀", "workspace": "워크스페이스",
    "organization": "조직",
    "integration": "통합", "connect": "연결",
    "sync": "동기화", "upload": "업로드",
    "download": "다운로드",
    "share": "공유", "sharing": "공유",
    "publish": "게시", "publishing": "출판",
    "printing": "인쇄",
    "label": "라벨", "labels": "라벨",
    "tag": "태그", "tags": "태그",
    "category": "카테고리",
    "search": "검색", "discover": "탐색",
    "explore": "탐색",
    "library": "라이브러리",
    "collection": "컬렉션",
    "gallery": "갤러리",
    "portfolio": "포트폴리오",
    "showcase": "쇼케이스",
    "premium": "프리미엄",
    "pro": "프로", "plus": "플러스",
    "basic": "베이직", "standard": "스탠다드",
    "enterprise": "엔터프라이즈",
    "a11y": "접근성",
    "wcag": "WCAG", "aria": "ARIA",
    "responsive": "반응형",
    "mobile": "모바일", "desktop": "데스크톱",
    "web": "웹", "website": "웹사이트",
    "ads": "광고", "ad": "광고", "advertising": "광고",
    "campaign": "캠페인",
    "analytics": "분석",
    "seo": "SEO",
    "hashtag": "해시태그", "hashtags": "해시태그",
    "post": "게시물", "posts": "게시물",
    "story": "스토리", "stories": "스토리",
    "reel": "릴", "reels": "릴",
    "feed": "피드",
    "profile": "프로필",
    "headshot": "증명사진",
    "selfie": "셀피",
    "manga": "만화",
    "comic": "만화", "cartoon": "카툰",
    "sketch": "스케치", "drawing": "그림",
    "painting": "그림", "artwork": "아트워크",
    "abstract": "추상",
    "realistic": "사실적",
    "vintage": "빈티지", "retro": "레트로",
    "minimal": "미니멀", "minimalist": "미니멀리스트",
    "flat": "플랫", "material": "머티리얼",
    "geometry": "기하학", "geometric": "기하학적",
    "perspective": "원근법",
    "isometric": "아이소메트릭",
    "watercolor": "수채화", "watercolour": "수채화",
    "pencil": "연필", "ink": "잉크",
    "bokeh": "보케",
    "lut": "LUT", "preset": "프리셋", "presets": "프리셋",
    "remove": "제거", "remover": "제거 도구",
    "object": "객체", "objects": "객체",
    "tts": "TTS",
    "hanbok": "한복",
    "clothes": "의류",
    "fashion": "패션",
    "outfit": "코디",
    "hairstyle": "헤어스타일",
    "beauty": "뷰티",
    "makeup": "메이크업",
    "skin": "피부",
    "face": "얼굴",
    "body": "바디",
    "nature": "자연",
    "animal": "동물", "animals": "동물",
    "food": "음식", "restaurant": "레스토랑",
    "travel": "여행",
    "architecture": "건축",
    "real estate": "부동산",
    "interior": "인테리어",
    "furniture": "가구",
    "education": "교육",
    "school": "학교",
    "children": "어린이",
    "kids": "키즈",
    "family": "가족",
    "holiday": "휴일",
    "christmas": "크리스마스",
    "birthday": "생일",
    "wedding": "결혼식",
    "event": "이벤트", "events": "이벤트",
    "invitation": "초대장", "invitations": "초대장",
    "certificate": "인증서", "certificates": "인증서",
    "award": "어워드", "badge": "배지", "badges": "배지",
    "stamp": "스탬프", "stamps": "스탬프",
    "signature": "서명",
    "monogram": "모노그램",
    "doodle": "낙서", "doodles": "낙서",
    "clipart": "클립아트",
    "element": "요소", "elements": "요소",
    "decoration": "장식", "decorations": "장식",
    "ornament": "장식품", "ornaments": "장식품",
    "divider": "구분선",
    "line": "선", "lines": "선",
    "dot": "점", "dots": "점",
    "circle": "원", "circles": "원",
    "triangle": "삼각형",
    "square": "사각형",
    "star": "별", "stars": "별",
    "heart": "하트", "hearts": "하트",
    "arrow": "화살표", "arrows": "화살표",
    "hd": "HD", "4k": "4K", "fhd": "FHD",
    "resolution": "해상도",
    "phone": "스마트폰", "smartphone": "스마트폰",
    "tablet": "태블릿", "laptop": "노트북",
    "t-shirt": "티셔츠", "tshirt": "티셔츠",
    "cup": "컵", "mug": "머그컵",
    "bag": "가방", "tote": "토트백",
    "packaging": "포장재",
    "box": "상자", "bottle": "병",
    "book": "책", "books": "책",
    "magazine": "잡지", "newspaper": "신문",
    "report": "보고서",
    "document": "문서", "documents": "문서",
    "invoice": "청구서",
    "receipt": "영수증",
    "schedule": "일정",
    "plan": "플랜", "planning": "계획",
    "strategy": "전략",
    "sales": "영업",
    "graph": "그래프",
    "diagram": "다이어그램",
    "timeline": "타임라인",
    "roadmap": "로드맵",
    "brainstorm": "브레인스토밍",
    "idea": "아이디어", "ideas": "아이디어",
    "inspiration": "영감",
    "wireframe": "와이어프레임",
    "prototype": "프로토타입",
    "ux": "UX", "ui": "UI",
    "interface": "인터페이스",
    "dashboard": "대시보드",
    "component": "컴포넌트", "components": "컴포넌트",
    "kit": "키트",
    "plugin": "플러그인", "plugins": "플러그인",
    "extension": "확장 프로그램",
    "addon": "애드온",
    "api": "API", "sdk": "SDK",
    "open source": "오픈소스",
    "commercial": "상업용",
    "license": "라이선스",
    "copyright": "저작권",
    "royalty": "로열티",
    "community": "커뮤니티",
    "support": "지원",
    "tutorial": "튜토리얼",
    "guide": "가이드",
    "documentation": "문서",
    "help": "도움말",
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 辞書ベース翻訳（--dict モード）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
_KEEP_UPPERCASE = {'AI', 'QR', 'PDF', 'SVG', 'PNG', 'GIF', 'JPG',
                   'HD', '4K', 'API', 'SDK', 'SEO', 'UI', 'UX',
                   'WCAG', 'ARIA', 'TTS', 'DAM', 'LUT', 'FHD',
                   '3D', '8K', 'VR', 'AR', 'NFT'}

def _translate_one(kw_raw: str, phrase_dict: dict, word_dict: dict) -> str:
    kw = kw_raw.strip().lower()
    if not kw:
        return kw_raw
    if kw in phrase_dict:
        return phrase_dict[kw]
    if kw in word_dict:
        return word_dict[kw]
    for phrase in sorted(phrase_dict.keys(), key=len, reverse=True):
        if phrase in kw and len(phrase) > 3:
            return phrase_dict[phrase]
    parts = re.split(r'[\s\-_/]+', kw)
    translated = []
    for part in parts:
        if part in word_dict:
            translated.append(word_dict[part])
        elif part.upper() in _KEEP_UPPERCASE:
            translated.append(part.upper())
        elif re.match(r'^\d', part):
            translated.append(part)
        else:
            return kw_raw.strip()
    return ' '.join(translated)

def translate_keywords_dict(kws: list, phrase_dict: dict, word_dict: dict) -> list:
    return [_translate_one(kw, phrase_dict, word_dict) for kw in kws]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Claude API（デフォルトモード）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SYSTEM_PROMPT = """Adobe Express のアドオン（プラグイン）情報を日本語と韓国語に翻訳します。

ルール:
- アプリ名・ブランド名・サービス名（Adobe Express, Shopify, TikTok, WCAG 等）はそのまま残す
- descriptionJa/Ko は自然で簡潔な翻訳にする（機械翻訳っぽくしない）
- keywords は短いキーワード単位で翻訳する（1語〜3語程度）
- 出力は必ず JSON 配列のみ（説明文や前置きは不要）
"""

def _build_prompt(entries: list) -> str:
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

def _call_claude(api_key: str, prompt: str) -> str:
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

def _extract_json_array(text: str) -> list:
    m = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", text, re.DOTALL)
    if m:
        text = m.group(1)
    else:
        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1:
            text = text[start:end+1]
    return json.loads(text)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ファイル書き込み
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
        description="addons_data.json の description / keywords を翻訳する"
    )
    parser.add_argument(
        "--dict",
        action="store_true",
        help="静的辞書でキーワードのみ翻訳（ANTHROPIC_API_KEY 不要）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="翻訳対象を表示するがファイルには書き込まない",
    )
    args = parser.parse_args()

    # ── API モードのキー確認（辞書モード以外） ──────────────
    api_key = ""
    if not args.dict:
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            print("[ERROR] ANTHROPIC_API_KEY 環境変数が設定されていません。", file=sys.stderr)
            print("  export ANTHROPIC_API_KEY='sk-ant-...'", file=sys.stderr)
            print("  辞書モードは --dict フラグで実行できます（API 不要）。", file=sys.stderr)
            sys.exit(1)

    print(f"データを読み込み中: {SRC_PATH}")
    with open(SRC_PATH, encoding="utf-8") as f:
        db = json.load(f)
    addons = db["addons"]

    # ── 辞書モード ─────────────────────────────────────
    if args.dict:
        targets = [
            a for a in addons
            if a.get("keywordsJa") == a.get("keywordsEn") and a.get("keywordsEn")
        ]
        print(f"翻訳対象（キーワードのみ）: {len(targets)} 件")

        if args.dry_run:
            for a in targets:
                print(f"  - {a['id']}")
            print("\n[DRY-RUN] ファイルは変更しません。")
            return

        updated = 0
        for addon in addons:
            if addon.get("keywordsJa") != addon.get("keywordsEn"):
                continue
            kws_en = addon.get("keywordsEn", [])
            if not kws_en:
                continue
            addon["keywordsJa"] = translate_keywords_dict(kws_en, PHRASE_JA, WORD_JA)
            addon["keywordsKo"] = translate_keywords_dict(kws_en, PHRASE_KO, WORD_KO)
            addon["keywords"]   = addon["keywordsJa"]
            updated += 1

        print(f"\nファイルに書き込み中...")
        atomic_write(SRC_PATH, db)
        print(f"  書き込み完了: {SRC_PATH}")
        atomic_write(DOCS_PATH, db)
        print(f"  書き込み完了: {DOCS_PATH}")
        print(f"\n更新済みエントリ: {updated} 件")
        return

    # ── API モード ─────────────────────────────────────
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

    translation_map: dict = {}
    total_batches = (len(targets) + BATCH_SIZE - 1) // BATCH_SIZE

    for i in range(0, len(targets), BATCH_SIZE):
        batch = targets[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        print(f"\nバッチ {batch_num}/{total_batches} を翻訳中... ({len(batch)} 件)", flush=True)

        prompt = _build_prompt(batch)
        response_text = _call_claude(api_key, prompt)

        try:
            results = _extract_json_array(response_text)
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON パース失敗: {e}", file=sys.stderr)
            print("レスポンス:", response_text[:500], file=sys.stderr)
            sys.exit(1)

        for result in results:
            translation_map[result["id"]] = result
            print(f"  ✓ {result['id']}")

        if batch_num < total_batches:
            time.sleep(1)

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
            addon["keywords"]   = tr["keywordsJa"]
            updated_kw += 1

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

# 多言語対応 Add-on データサンプル

このファイルは、addons_data.json を多言語対応に拡張する際の参考サンプルです。

## データ構造

各Add-onは以下のフィールドを持つ必要があります：

```json
{
  "id": "unique-addon-id",
  
  "nameEn": "English Name",
  "nameJa": "日本語名",
  "nameKo": "한국어 이름",
  
  "category": "category-id",
  "categoryEn": "Category Name",
  "categoryJa": "カテゴリ名",
  "categoryKo": "카테고리명",
  
  "descriptionEn": "English description...",
  "descriptionJa": "日本語の説明...",
  "descriptionKo": "한국어 설명...",
  
  "keywordsEn": ["keyword1", "keyword2"],
  "keywordsJa": ["キーワード1", "キーワード2"],
  "keywordsKo": ["키워드1", "키워드2"],
  
  "useCasesEn": ["Use case 1", "Use case 2"],
  "useCasesJa": ["用途1", "用途2"],
  "useCasesKo": ["사용 사례 1", "사용 사례 2"],
  
  "featured": true,
  "rating": 4.5,
  "userCount": "10K+"
}
```

## サンプル: Dropbox

```json
{
  "id": "dropbox",
  "nameEn": "Dropbox",
  "nameJa": "Dropbox",
  "nameKo": "Dropbox",
  "category": "storage",
  "categoryEn": "Storage Integration",
  "categoryJa": "ストレージ連携",
  "categoryKo": "스토리지 연동",
  "descriptionEn": "Add files directly from Dropbox or save your designs. Seamless cloud storage integration for access anywhere. Perfect for team collaboration and automatic backups.",
  "descriptionJa": "Dropboxからファイルを直接追加したり、作成したデザインを保存できます。クラウドストレージとシームレスに連携し、どこからでもアクセス可能。チームでのファイル共有やバックアップに最適です。",
  "descriptionKo": "Dropbox에서 직접 파일을 추가하거나 디자인을 저장하세요. 어디서나 액세스할 수 있는 원활한 클라우드 스토리지 통합. 팀 협업 및 자동 백업에 완벽합니다.",
  "keywordsEn": ["Dropbox", "storage", "cloud", "files", "save", "share", "backup", "sync", "team", "collaboration"],
  "keywordsJa": ["Dropbox", "ストレージ", "クラウド", "ファイル", "保存", "共有", "バックアップ", "同期", "チーム", "コラボレーション"],
  "keywordsKo": ["Dropbox", "스토리지", "클라우드", "파일", "저장", "공유", "백업", "동기화", "팀", "협업"],
  "useCasesEn": ["Team file sharing", "Design backups", "Multi-device access"],
  "useCasesJa": ["チームでファイル共有", "デザインのバックアップ", "複数デバイスでの作業"],
  "useCasesKo": ["팀 파일 공유", "디자인 백업", "다중 기기 액세스"],
  "featured": true,
  "rating": 4.8,
  "userCount": "50K+"
}
```

## サンプル: Soundstripe

```json
{
  "id": "soundstripe",
  "nameEn": "Soundstripe",
  "nameJa": "Soundstripe",
  "nameKo": "Soundstripe",
  "category": "audio",
  "categoryEn": "Music & Audio",
  "categoryJa": "音楽・オーディオ",
  "categoryKo": "음악 및 오디오",
  "descriptionEn": "Royalty-free high-quality music library. Easily add perfect music to videos and presentations.",
  "descriptionJa": "ロイヤリティフリーの高品質音楽ライブラリ。動画やプレゼンに最適な音楽を簡単に追加。",
  "descriptionKo": "로열티 프리 고품질 음악 라이브러리. 비디오 및 프레젠테이션에 완벽한 음악을 쉽게 추가하세요.",
  "keywordsEn": ["music", "BGM", "royalty-free", "sound", "video", "audio", "soundtrack"],
  "keywordsJa": ["音楽", "BGM", "ロイヤリティフリー", "サウンド", "動画", "オーディオ", "サウンドトラック"],
  "keywordsKo": ["음악", "배경음악", "로열티프리", "사운드", "비디오", "오디오", "사운드트랙"],
  "useCasesEn": ["Video production", "Presentations", "YouTube content"],
  "useCasesJa": ["動画制作", "プレゼンテーション", "YouTube動画"],
  "useCasesKo": ["비디오 제작", "프레젠테이션", "YouTube 콘텐츠"],
  "featured": true,
  "rating": 4.5,
  "userCount": "10K+"
}
```

## サンプル: Accessify

```json
{
  "id": "accessify",
  "nameEn": "Accessify",
  "nameJa": "アクセシビリティチェッカー",
  "nameKo": "접근성 검사기",
  "category": "accessibility",
  "categoryEn": "Accessibility",
  "categoryJa": "アクセシビリティ",
  "categoryKo": "접근성",
  "descriptionEn": "WCAG compliance check, color contrast analysis, and accessible color suggestions. Winner of Adobe Fund for Design.",
  "descriptionJa": "WCAGコンプライアンスチェック、色のコントラスト比分析、アクセシブルな色の提案機能。Adobe Fund for Design受賞。",
  "descriptionKo": "WCAG 규정 준수 검사, 색상 대비 분석 및 접근 가능한 색상 제안. Adobe Fund for Design 수상작.",
  "keywordsEn": ["accessibility", "WCAG", "color-blind", "contrast", "compliance", "inclusive"],
  "keywordsJa": ["アクセシビリティ", "WCAG", "色盲", "コントラスト", "準拠", "インクルーシブ"],
  "keywordsKo": ["접근성", "WCAG", "색맹", "대비", "규정준수", "포용적"],
  "useCasesEn": ["Web design", "Public sector", "Educational institutions"],
  "useCasesJa": ["Webデザイン", "公共機関", "教育機関"],
  "useCasesKo": ["웹 디자인", "공공 부문", "교육 기관"],
  "featured": true,
  "rating": 4.6,
  "userCount": "8K+"
}
```

## カテゴリ翻訳リスト

```json
{
  "design-assets": {
    "en": "Design Assets",
    "ja": "デザイン素材",
    "ko": "디자인 소재"
  },
  "accessibility": {
    "en": "Accessibility",
    "ja": "アクセシビリティ",
    "ko": "접근성"
  },
  "ai": {
    "en": "AI & Audio/Video",
    "ja": "AI・音声/動画",
    "ko": "AI 및 오디오/비디오"
  },
  "storage": {
    "en": "Storage Integration",
    "ja": "ストレージ連携",
    "ko": "스토리지 연동"
  },
  "marketing": {
    "en": "Social & Marketing",
    "ja": "SNS・マーケティング",
    "ko": "소셜 및 마케팅"
  },
  "utility": {
    "en": "Utilities",
    "ja": "ユーティリティ",
    "ko": "유틸리티"
  },
  "audio": {
    "en": "Music & Audio",
    "ja": "音楽・オーディオ",
    "ko": "음악 및 오디오"
  },
  "text": {
    "en": "Text Effects",
    "ja": "テキスト効果",
    "ko": "텍스트 효과"
  },
  "brand": {
    "en": "Brand & Asset Management",
    "ja": "ブランド・アセット管理",
    "ko": "브랜드 및 자산 관리"
  }
}
```

## 翻訳時のガイドライン

### 英語（English）
- 簡潔で明確な表現
- 技術用語は業界標準を使用
- 文末は句点不要

### 日本語
- 丁寧語を使用（です・ます調）
- カタカナ表記は一般的なものを採用
- 読みやすさ重視

### 韓国語（한국어）
- 존댓말（丁寧語）使用
- 技術用語は英語そのままか音訳
- 自然な韓国語表現を心がける

## 翻訳作業の優先順位

1. **高優先度**: name, description, keywords
2. **中優先度**: category, useCases
3. **低優先度**: その他のメタデータ

## 注意事項

- すべてのAdd-onに3言語すべてのフィールドが必要
- 欠落言語がある場合、英語がフォールバックとして使用される
- キーワードは検索精度に直結するため、各言語で充実させる
- 文化的な文脈を考慮した翻訳を心がける

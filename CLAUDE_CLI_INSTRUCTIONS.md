# Express Helper JP - Claude CLI 開発指示書

## プロジェクト概要

**プロダクト名**: Express Helper (多言語対応)  
**目的**: Adobe Expressのアドオンを多言語で検索できるツール  
**対応言語**: 
- 🇬🇧 英語（English）- 必須（Adobe審査要件）
- 🇯🇵 日本語（日本語）- 必須（主要ターゲット市場）
- 🇰🇷 韓国語（한국어）- サポート対象
**技術スタック**: React + JavaScript (Adobe Express Add-on SDK) + i18n  
**開発期間**: 5〜7日

---

## 前提条件

### 完了済み
- ✅ プロジェクト作成完了（`express-helper-jp`）
- ✅ React + JavaScript テンプレート選択完了
- ✅ ローカル起動確認済み（https://localhost:5241）
- ✅ データ準備完了（52個のAdd-onデータ）
- ✅ プロトタイプ作成完了（動作確認済み）

### 利用可能なリソース
- `addons_data.json` - 52個のAdd-on構造化データ
- `AddonSearchPortal.jsx` - React プロトタイプコード
- `wireframe_design.md` - UI/UX設計書
- `addon-search-preview.html` - ブラウザプレビュー版

---

## プロジェクト構造

```
express-helper-jp/
├── src/
│   ├── ui/                          # UIコード（iframe内で実行）
│   │   ├── index.html               # HTMLエントリーポイント
│   │   ├── index.jsx                # Reactエントリーポイント
│   │   ├── components/              # 作成するコンポーネント
│   │   │   ├── SearchBar.jsx       # 検索バー
│   │   │   ├── AddonCard.jsx       # Add-onカード
│   │   │   ├── AddonListItem.jsx   # リストアイテム
│   │   │   ├── CategoryList.jsx    # カテゴリ一覧
│   │   │   ├── AddonModal.jsx      # 詳細モーダル
│   │   │   └── LanguageSwitcher.jsx # 言語切り替え
│   │   ├── data/
│   │   │   └── addons_data.json    # ← コピーが必要
│   │   ├── locales/                 # 多言語対応ファイル
│   │   │   ├── en.json             # 英語翻訳
│   │   │   ├── ja.json             # 日本語翻訳
│   │   │   └── ko.json             # 韓国語翻訳
│   │   ├── utils/
│   │   │   └── i18n.js             # 多言語化ヘルパー
│   │   └── styles/
│   │       └── styles.css           # 共通スタイル
│   └── sandbox/
│       └── code.js                  # Document Sandbox（今回は未使用）
├── manifest.json                    # Add-on設定ファイル（多言語対応）
├── package.json
└── README.md
```

---

## 開発タスク（優先順位順）

### Phase 0: 多言語対応（i18n）セットアップ

#### Task 0.1: 翻訳ファイル作成

**src/ui/locales/en.json**（英語 - 審査必須）
```json
{
  "app": {
    "title": "Express Helper",
    "subtitle": "Search Adobe Express add-ons in your language"
  },
  "search": {
    "placeholder": "Search (e.g., QR code, music, icons)",
    "resultsCount": "{{count}} results for \"{{query}}\"",
    "noResults": "No add-ons found. Please try different keywords."
  },
  "sections": {
    "featured": "Featured Add-ons",
    "categories": "Browse by Category",
    "recent": "Recently Added"
  },
  "categories": {
    "design-assets": "Design Assets",
    "accessibility": "Accessibility",
    "ai": "AI & Audio/Video",
    "storage": "Storage",
    "marketing": "Social & Marketing",
    "utility": "Utilities",
    "audio": "Music & Audio",
    "text": "Text Effects",
    "brand": "Brand & Asset Management"
  },
  "addon": {
    "rating": "Rating",
    "users": "users",
    "category": "Category",
    "description": "Description",
    "keywords": "Related Keywords",
    "useCases": "Use Cases",
    "openInMarketplace": "Open in Marketplace →",
    "viewDetails": "Details"
  },
  "actions": {
    "close": "✕ Close"
  }
}
```

**src/ui/locales/ja.json**（日本語 - メインターゲット）
```json
{
  "app": {
    "title": "Express Helper",
    "subtitle": "Adobe Expressのアドオンを日本語で検索"
  },
  "search": {
    "placeholder": "検索 (例: QRコード、音楽、アイコン)",
    "resultsCount": "\"{{query}}\" の検索結果 ({{count}}件)",
    "noResults": "該当するアドオンが見つかりませんでした。別のキーワードで検索してみてください。"
  },
  "sections": {
    "featured": "人気のアドオン",
    "categories": "カテゴリから探す",
    "recent": "最近追加されたアドオン"
  },
  "categories": {
    "design-assets": "デザイン素材",
    "accessibility": "アクセシビリティ",
    "ai": "AI・音声/動画",
    "storage": "ストレージ連携",
    "marketing": "SNS・マーケティング",
    "utility": "ユーティリティ",
    "audio": "音楽・オーディオ",
    "text": "テキスト効果",
    "brand": "ブランド・アセット管理"
  },
  "addon": {
    "rating": "評価",
    "users": "ユーザー",
    "category": "カテゴリ",
    "description": "説明",
    "keywords": "関連キーワード",
    "useCases": "こんな時に便利",
    "openInMarketplace": "Marketplaceで開く →",
    "viewDetails": "詳細"
  },
  "actions": {
    "close": "✕ 閉じる"
  }
}
```

**src/ui/locales/ko.json**（韓国語）
```json
{
  "app": {
    "title": "Express Helper",
    "subtitle": "Adobe Express 애드온을 한국어로 검색"
  },
  "search": {
    "placeholder": "검색 (예: QR코드, 음악, 아이콘)",
    "resultsCount": "\"{{query}}\" 검색 결과 ({{count}}개)",
    "noResults": "해당 애드온을 찾을 수 없습니다. 다른 키워드로 검색해보세요."
  },
  "sections": {
    "featured": "인기 애드온",
    "categories": "카테고리별 탐색",
    "recent": "최근 추가됨"
  },
  "categories": {
    "design-assets": "디자인 소재",
    "accessibility": "접근성",
    "ai": "AI 및 오디오/비디오",
    "storage": "스토리지 연동",
    "marketing": "소셜 및 마케팅",
    "utility": "유틸리티",
    "audio": "음악 및 오디오",
    "text": "텍스트 효과",
    "brand": "브랜드 및 자산 관리"
  },
  "addon": {
    "rating": "평점",
    "users": "사용자",
    "category": "카테고리",
    "description": "설명",
    "keywords": "관련 키워드",
    "useCases": "이럴 때 유용합니다",
    "openInMarketplace": "마켓플레이스에서 열기 →",
    "viewDetails": "상세정보"
  },
  "actions": {
    "close": "✕ 닫기"
  }
}
```

#### Task 0.2: i18nヘルパー作成

**src/ui/utils/i18n.js**
```javascript
import en from '../locales/en.json';
import ja from '../locales/ja.json';
import ko from '../locales/ko.json';

const translations = { en, ja, ko };

// ブラウザ言語を検出
export const detectLanguage = () => {
  const browserLang = navigator.language.split('-')[0]; // 'ja-JP' -> 'ja'
  return ['en', 'ja', 'ko'].includes(browserLang) ? browserLang : 'en';
};

// 翻訳関数
export const t = (key, locale, params = {}) => {
  const keys = key.split('.');
  let value = translations[locale];
  
  for (const k of keys) {
    value = value?.[k];
  }
  
  if (!value) return key;
  
  // パラメータ置換 {{count}} など
  return Object.keys(params).reduce((str, param) => {
    return str.replace(new RegExp(`{{${param}}}`, 'g'), params[param]);
  }, value);
};

// Add-onデータの多言語対応フィールド取得
export const getLocalizedField = (addon, field, locale) => {
  const fieldMap = {
    en: `${field}En`,
    ja: `${field}Ja`,
    ko: `${field}Ko`
  };
  
  return addon[fieldMap[locale]] || addon[fieldMap['en']] || addon[field];
};
```

#### Task 0.3: データ構造の拡張

**addons_data.json に多言語フィールドを追加**:
```json
{
  "id": "dropbox",
  "nameEn": "Dropbox",
  "nameJa": "Dropbox",
  "nameKo": "Dropbox",
  "category": "storage",
  "categoryEn": "Storage",
  "categoryJa": "ストレージ連携",
  "categoryKo": "스토리지 연동",
  "descriptionEn": "Add files directly from Dropbox or save your designs. Seamless cloud storage integration for access anywhere.",
  "descriptionJa": "Dropboxからファイルを直接追加したり、作成したデザインを保存できます。クラウドストレージとシームレスに連携し、どこからでもアクセス可能。",
  "descriptionKo": "Dropbox에서 직접 파일을 추가하거나 디자인을 저장하세요. 어디서나 액세스할 수 있는 원활한 클라우드 스토리지 통합.",
  "keywordsEn": ["Dropbox", "storage", "cloud", "files", "save", "share", "backup", "sync"],
  "keywordsJa": ["Dropbox", "ストレージ", "クラウド", "ファイル", "保存", "共有", "バックアップ", "同期"],
  "keywordsKo": ["Dropbox", "스토리지", "클라우드", "파일", "저장", "공유", "백업", "동기화"],
  "useCasesEn": ["Team file sharing", "Design backups", "Multi-device access"],
  "useCasesJa": ["チームでファイル共有", "デザインのバックアップ", "複数デバイスでの作業"],
  "useCasesKo": ["팀 파일 공유", "디자인 백업", "다중 기기 액세스"],
  "featured": true,
  "rating": 4.8,
  "userCount": "50K+"
}
```

**注意**: すべての52個のAdd-onに対して、En/Ja/Koフィールドを追加する必要があります。

#### Task 0.4: 言語切り替えコンポーネント作成

**src/ui/components/LanguageSwitcher.jsx**
```jsx
import React from 'react';

export default function LanguageSwitcher({ currentLocale, onLocaleChange }) {
  const languages = [
    { code: 'en', label: 'English', flag: '🇬🇧' },
    { code: 'ja', label: '日本語', flag: '🇯🇵' },
    { code: 'ko', label: '한국어', flag: '🇰🇷' }
  ];

  return (
    <div className="language-switcher">
      {languages.map(lang => (
        <button
          key={lang.code}
          className={`lang-btn ${currentLocale === lang.code ? 'active' : ''}`}
          onClick={() => onLocaleChange(lang.code)}
        >
          <span className="flag">{lang.flag}</span>
          <span className="label">{lang.label}</span>
        </button>
      ))}
    </div>
  );
}
```

**スタイル追加（styles.css）**:
```css
.language-switcher {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  background: #F5F7FA;
  border-bottom: 1px solid #E0E0E0;
}

.lang-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border: 1px solid #E0E0E0;
  background: #FFFFFF;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.lang-btn:hover {
  background: #F5F7FA;
}

.lang-btn.active {
  background: #0066FF;
  color: #FFFFFF;
  border-color: #0066FF;
}

.lang-btn .flag {
  font-size: 16px;
}
```

---

### Phase 1: データ統合とコンポーネント分割

#### Task 1.1: データファイル配置
```bash
# 実行コマンド
mkdir -p src/ui/data
cp /path/to/addons_data.json src/ui/data/
```

**確認ポイント**:
- `src/ui/data/addons_data.json` が存在すること
- JSONが正しくパースできること

#### Task 1.2: コンポーネント分割

既存の `AddonSearchPortal.jsx` を以下のコンポーネントに分割：

**src/ui/components/SearchBar.jsx**
```jsx
// 検索バーコンポーネント
// Props: value, onChange
// 機能: リアルタイム検索入力
```

**src/ui/components/AddonCard.jsx**
```jsx
// グリッド表示用カードコンポーネント
// Props: addon, onClick
// 機能: アイコン、名前、カテゴリ、評価表示
```

**src/ui/components/AddonListItem.jsx**
```jsx
// 検索結果リスト表示用コンポーネント
// Props: addon, onClick
// 機能: 詳細情報、ボタン表示
```

**src/ui/components/CategoryList.jsx**
```jsx
// カテゴリ一覧コンポーネント
// Props: categories, onCategoryClick
// 機能: カテゴリ別フィルタリング
```

**src/ui/components/AddonModal.jsx**
```jsx
// 詳細モーダルコンポーネント
// Props: addon, onClose
// 機能: 詳細情報表示、外部リンク
```

#### Task 1.3: メインコンポーネント作成

**src/ui/index.jsx**
```jsx
import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import addonsData from './data/addons_data.json';
import SearchBar from './components/SearchBar';
import AddonCard from './components/AddonCard';
import AddonListItem from './components/AddonListItem';
import CategoryList from './components/CategoryList';
import AddonModal from './components/AddonModal';
import LanguageSwitcher from './components/LanguageSwitcher';
import { detectLanguage, t, getLocalizedField } from './utils/i18n';
import './styles/styles.css';

function App() {
  const [locale, setLocale] = useState(detectLanguage());
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedAddon, setSelectedAddon] = useState(null);
  const [view, setView] = useState('home'); // 'home' | 'search' | 'category'

  // LocalStorageに言語設定を保存
  useEffect(() => {
    localStorage.setItem('preferredLocale', locale);
  }, [locale]);

  // 検索ロジック（多言語対応）
  const searchAddons = (query) => {
    if (!query.trim()) return [];
    
    const lowerQuery = query.toLowerCase();
    
    return addonsData.addons.filter(addon => {
      const name = getLocalizedField(addon, 'name', locale).toLowerCase();
      const description = getLocalizedField(addon, 'description', locale).toLowerCase();
      const keywords = addon[`keywords${locale.charAt(0).toUpperCase() + locale.slice(1)}`] || addon.keywordsEn;
      const category = getLocalizedField(addon, 'category', locale).toLowerCase();
      
      return (
        name.includes(lowerQuery) ||
        description.includes(lowerQuery) ||
        keywords.some(kw => kw.toLowerCase().includes(lowerQuery)) ||
        category.includes(lowerQuery)
      );
    });
  };

  const handleSearch = (query) => {
    setSearchQuery(query);
    setView(query.trim() ? 'search' : 'home');
  };

  const searchResults = searchAddons(searchQuery);
  const featuredAddons = addonsData.addons.filter(a => a.featured);

  return (
    <div className="app-container">
      {/* ヘッダー */}
      <header className="header">
        <h1>{t('app.title', locale)}</h1>
        <p className="subtitle">{t('app.subtitle', locale)}</p>
      </header>

      {/* 言語切り替え */}
      <LanguageSwitcher 
        currentLocale={locale} 
        onLocaleChange={setLocale} 
      />

      {/* 検索バー */}
      <SearchBar 
        value={searchQuery} 
        onChange={handleSearch}
        placeholder={t('search.placeholder', locale)}
      />

      {/* ホーム画面 */}
      {view === 'home' && (
        <>
          <section className="section">
            <h2>{t('sections.featured', locale)} 🔥</h2>
            <div className="grid">
              {featuredAddons.map(addon => (
                <AddonCard
                  key={addon.id}
                  addon={addon}
                  locale={locale}
                  onClick={() => setSelectedAddon(addon)}
                />
              ))}
            </div>
          </section>

          <section className="section">
            <h2>{t('sections.categories', locale)} 📁</h2>
            <CategoryList
              categories={addonsData.metadata.categories}
              locale={locale}
              onCategoryClick={(cat) => console.log(cat)}
            />
          </section>
        </>
      )}

      {/* 検索結果画面 */}
      {view === 'search' && (
        <section className="section">
          <h2>
            {t('search.resultsCount', locale, { 
              query: searchQuery, 
              count: searchResults.length 
            })}
          </h2>
          {searchResults.length > 0 ? (
            <div className="results-list">
              {searchResults.map(addon => (
                <AddonListItem
                  key={addon.id}
                  addon={addon}
                  locale={locale}
                  onClick={() => setSelectedAddon(addon)}
                />
              ))}
            </div>
          ) : (
            <p className="no-results">
              {t('search.noResults', locale)}
            </p>
          )}
        </section>
      )}

      {/* 詳細モーダル */}
      {selectedAddon && (
        <AddonModal
          addon={selectedAddon}
          locale={locale}
          onClose={() => setSelectedAddon(null)}
        />
      )}
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
```

---

### Phase 2: スタイリング

#### Task 2.1: 共通スタイル作成

**src/ui/styles/styles.css**
```css
/* リセット */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* フォント */
body {
  font-family: 'Noto Sans JP', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  color: #1E1E1E;
  background: #FFFFFF;
}

/* レイアウト */
.app-container {
  max-width: 400px;
  margin: 0 auto;
  min-height: 100vh;
}

/* ヘッダー */
.header {
  padding: 16px;
  background: #0066FF;
  color: #FFFFFF;
  text-align: center;
}

.header h1 {
  font-size: 20px;
  font-weight: bold;
}

/* グリッド */
.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

/* セクション */
.section {
  padding: 16px;
}

.section h2 {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 16px;
}

/* 検索結果なし */
.no-results {
  text-align: center;
  color: #666;
  padding: 32px 16px;
  line-height: 1.6;
}

/* リザルトリスト */
.results-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
```

#### Task 2.2: コンポーネント別スタイル

各コンポーネントファイル内に `styled-components` またはインラインスタイルを使用。
プロトタイプの `addon-search-preview.html` 内のスタイルを参考にすること。

---

### Phase 3: 機能実装

#### Task 3.1: 検索機能強化

**検索対象**:
- `nameJa` (Add-on名)
- `keywords` (キーワード配列)
- `description` (説明文)
- `categoryJa` (カテゴリ名)

**検索ロジック**:
```javascript
const searchAddons = (query) => {
  if (!query.trim()) return [];
  
  const lowerQuery = query.toLowerCase();
  
  return addonsData.addons.filter(addon => {
    return (
      addon.nameJa.toLowerCase().includes(lowerQuery) ||
      addon.keywords.some(kw => kw.toLowerCase().includes(lowerQuery)) ||
      addon.description.toLowerCase().includes(lowerQuery) ||
      addon.categoryJa.toLowerCase().includes(lowerQuery)
    );
  });
};
```

#### Task 3.2: カテゴリフィルタ実装

**機能**:
- カテゴリクリックで該当Add-onのみ表示
- 「すべて」で全Add-on表示に戻る

**実装例**:
```javascript
const [selectedCategory, setSelectedCategory] = useState(null);

const filteredAddons = selectedCategory
  ? addonsData.addons.filter(a => a.category === selectedCategory)
  : addonsData.addons;
```

#### Task 3.3: ソート機能

**ソートオプション**:
- 人気順（rating降順）
- 名前順（nameJa昇順）
- ユーザー数順（userCount降順）

---

### Phase 4: UI/UX改善

#### Task 4.1: ローディング状態

検索中やデータ読み込み中の表示:
```jsx
{isLoading && <div className="loading">読み込み中...</div>}
```

#### Task 4.2: アニメーション

**対象**:
- カードホバー時の浮き上がり効果
- モーダルのフェードイン/アウト
- 検索結果のスライドイン

**CSS例**:
```css
.addon-card {
  transition: all 0.2s ease;
}

.addon-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
```

#### Task 4.3: レスポンシブ対応

Adobe Express Add-onパネル幅: 320px〜400px

```css
@media (max-width: 320px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
```

---

### Phase 5: 外部リンク統合

#### Task 5.1: Marketplace リンク

**実装**:
```jsx
<button onClick={() => {
  window.open('https://express.adobe.com/add-ons/' + addon.id, '_blank');
}}>
  Marketplaceで開く →
</button>
```

**注意**:
- 実際のMarketplace URLは未確定
- プレースホルダーとして実装
- 後で実URLに置き換え

---

## 重要な実装ルール

### 0. 多言語対応（i18n）の必須要件

**言語優先順位**:
1. 英語（en）- Adobe審査で必須
2. 日本語（ja）- 主要ターゲット市場
3. 韓国語（ko）- サポート言語

**実装原則**:
- すべてのUI文字列は翻訳ファイル（locales/）から取得
- ハードコードされた文字列を使用しない
- Add-onデータはEn/Ja/Koフィールドを持つ
- ブラウザ言語を自動検出、ユーザー選択を優先
- 言語設定はLocalStorageに保存

**翻訳対象**:
```javascript
// ✅ 正しい
<h1>{t('app.title', locale)}</h1>
<p>{getLocalizedField(addon, 'description', locale)}</p>

// ❌ 間違い
<h1>Express Helper JP</h1>
<p>{addon.descriptionJa}</p>
```

### 1. Adobe Express Add-on SDK の使用

**不要**: Document Sandboxとの通信（今回は読み取り専用ツール）

**使用するSDK機能**:
```javascript
// 基本的にはSDK機能は最小限でOK
// UIのみで完結
```

### 2. データの扱い

**静的データ**:
- `addons_data.json` から直接インポート
- 状態管理は React Hooks（useState）のみ

**外部API不使用**:
- すべてローカルデータで完結
- 将来的な拡張: ユーザー統計APIなど

### 3. パフォーマンス

**最適化ポイント**:
- 検索は即座に実行（debounce不要、データ量が少ない）
- 画像は使用しない（絵文字アイコンのみ）
- コンポーネントの再レンダリング最小化

---

## テスト項目

### 多言語機能テスト

- [ ] ブラウザ言語に応じて自動的に言語が設定される
- [ ] 言語切り替えボタンで3言語間を切り替え可能
- [ ] 選択した言語がLocalStorageに保存される
- [ ] リロード後も選択言語が維持される
- [ ] すべてのUI要素が選択言語で表示される
- [ ] Add-on名・説明・キーワードが選択言語で表示される

### 機能テスト（各言語で実施）

- [ ] 検索バーに入力するとリアルタイムで結果更新
- [ ] 検索結果が0件の場合、適切なメッセージ表示
- [ ] Add-onカードクリックで詳細モーダル表示
- [ ] モーダル外クリックまたは×ボタンで閉じる
- [ ] カテゴリクリックでフィルタリング
- [ ] 「Marketplaceで開く」ボタンで外部リンク

### 言語別検索テスト

**英語（en）**:
- [ ] "QR code" → vCard Generator, Barcode Designer
- [ ] "music" → Soundstripe, Muzaic
- [ ] "AI" → Gen Voice, HeyGen Avatars

**日本語（ja）**:
- [ ] "QRコード" → vCard生成、バーコードデザイナー
- [ ] "音楽" → Soundstripe、Muzaic
- [ ] "AI" → AI音声生成、HeyGen Avatars

**韓国語（ko）**:
- [ ] "QR코드" → vCard Generator, Barcode Designer
- [ ] "음악" → Soundstripe, Muzaic
- [ ] "AI" → Gen Voice, HeyGen Avatars

### UI/UXテスト

- [ ] 320px幅で正しく表示
- [ ] 400px幅で正しく表示
- [ ] ホバー効果が動作
- [ ] アニメーションがスムーズ
- [ ] 日本語フォントが正しく表示

### 検索テスト

以下のキーワードで検索し、期待する結果が表示されること:
- [ ] "QRコード" → vCard生成、バーコードデザイナー
- [ ] "音楽" → Soundstripe、Muzaic
- [ ] "AI" → Gen Voice、HeyGen Avatars、AI Audio Cleaner
- [ ] "ストレージ" → Dropbox、Google Drive、OneDrive
- [ ] "アイコン" → Streamline Icons、Iconiverse

---

## 開発時の注意点

### 1. ファイル保存時の自動リロード

開発サーバーは自動でリロードします。
変更を確認するにはブラウザをリフレッシュ。

### 2. エラーハンドリング

**必須**:
```javascript
// データ読み込みエラー
try {
  const data = await import('./data/addons_data.json');
} catch (error) {
  console.error('データ読み込みエラー:', error);
}
```

### 3. コンソールログ

開発中は積極的に `console.log()` を使用:
```javascript
console.log('検索クエリ:', searchQuery);
console.log('検索結果:', searchResults);
```

---

## マイルストーン

### Day 0（追加）- 多言語対応準備
- [ ] 翻訳ファイル作成（en.json, ja.json, ko.json）
- [ ] i18nヘルパー実装
- [ ] LanguageSwitcherコンポーネント作成
- [ ] addons_data.jsonに多言語フィールド追加

### Day 1
- [ ] データファイル配置
- [ ] コンポーネント分割
- [ ] 基本UI表示（多言語対応）

### Day 2
- [ ] 検索機能実装（多言語検索）
- [ ] カテゴリ機能実装
- [ ] モーダル実装

### Day 3
- [ ] スタイリング完成
- [ ] アニメーション追加
- [ ] レスポンシブ対応
- [ ] 言語切り替え動作確認

### Day 4
- [ ] 全機能テスト（3言語すべて）
- [ ] 翻訳品質チェック
- [ ] バグ修正
- [ ] パフォーマンス最適化

### Day 5
- [ ] 最終確認（各言語）
- [ ] manifest.json多言語設定
- [ ] ドキュメント作成（英語・日本語）
- [ ] 審査準備

---

## リファレンス

### 既存のコード

**参照すべきファイル**:
1. `addon-search-preview.html` - 完全なプロトタイプ（単一ファイル）
2. `AddonSearchPortal.jsx` - Reactコンポーネント版
3. `wireframe_design.md` - UI/UX設計書
4. `addons_data.json` - データ構造

### Adobe Express Add-on ドキュメント

- SDK Reference: https://developer.adobe.com/express/add-ons/docs/references/
- UI Components: https://developer.adobe.com/express/add-ons/docs/guides/
- Best Practices: https://developer.adobe.com/express/add-ons/docs/guides/develop/

---

## 完了条件

以下がすべて動作すること:

### 多言語対応
1. ✅ 英語・日本語・韓国語の3言語に完全対応
2. ✅ 言語切り替えが即座に反映される
3. ✅ ブラウザ言語を自動検出
4. ✅ manifest.jsonに3言語の説明文が記載

### 基本機能
5. ✅ 検索バーに各言語でリアルタイム検索
6. ✅ 人気のAdd-onがグリッド表示
7. ✅ カテゴリ一覧表示（各言語）
8. ✅ カードクリックで詳細モーダル表示
9. ✅ モーダル内に関連キーワード表示（各言語）
10. ✅ 「Marketplaceで開く」ボタン（各言語）

### UI/UX
11. ✅ 320px〜400px幅で正しく表示
12. ✅ アニメーションがスムーズ
13. ✅ エラーなく動作
14. ✅ 言語切り替えUIが見やすい

---

## 次のステップ（このファイル完了後）

1. **Manifest.json更新**
   - アイコン設定
   - 説明文追加
   - バージョン設定

2. **審査用素材作成**
   - アイコン画像（512x512）
   - スクリーンショット5枚
   - 使い方ガイド

3. **Marketplace申請**
   - Developer Consoleでアップロード
   - メタデータ入力
   - 審査送信

---

## Claude CLI への指示

このプロジェクトを開発する際は:

1. **Phase 0（多言語対応）を最優先で実装**すること
2. **既存のプロトタイプコードを最大限活用**すること
3. **コンポーネント分割を優先**し、再利用性を高めること
4. **データ構造（addons_data.json）に多言語フィールドを追加**すること
5. **すべてのUI文字列を翻訳ファイルから取得**すること
6. **英語・日本語・韓国語の3言語すべてで動作確認**すること
7. **段階的に実装**し、各段階で動作確認すること

### 多言語対応の重要ポイント

- **英語は必須**: Adobe審査で英語対応が必要
- **日本語がメイン**: 主要ターゲット市場
- **韓国語もサポート**: アジア市場拡大のため
- **ハードコード禁止**: すべての文字列は翻訳ファイルから
- **データも多言語化**: Add-onの名前・説明・キーワードすべて

質問や不明点があれば、このファイルを参照してください。

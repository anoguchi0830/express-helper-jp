# express-helper-jp

Adobe Express 向けの日本語アドオン発見ポータル（Web Add-on）。
日本ユーザーが Adobe Express のアドオンを日本語で検索・発見できる Panel UI を提供する。

## 開発コマンド

```bash
npm run start    # 開発サーバー起動（ホットリロード付き）
npm run build    # プロダクションビルド → dist/
npm run clean    # ビルド成果物を削除
npm run package  # Adobe Add-on としてパッケージ化（配布用）
```

## アーキテクチャ

Adobe Add-on は **2つの独立したランタイム** で動く。セキュリティ上の制約でランタイム間は直接参照できず、SDK 経由のメッセージパッシングで通信する。

```
Adobe Express
├── UI Runtime       → src/ui/index.jsx   （React, DOM操作）
└── Sandbox Runtime  → src/sandbox/code.js（Express ドキュメントAPI）
```

### UI Runtime（`src/ui/`）
- React 18 + CSS-in-JS（`styles` オブジェクト）+ 一部 `styles/styles.css` で実装
- Adobe Add-on SDK を CDN から読み込み（`addOnUISdk.ready` を待ってから React をマウント）
- コンポーネントは `src/ui/components/` に分割済み
  - `AddonCard`, `AddonListItem`, `AddonModal`, `CategoryList`, `LanguageSwitcher`, `SearchBar`
- `index.jsx` は App コンポーネント + Toast + `ADDONS` 定数を担当
- ビュー状態: `'home'` / `'search'`（`view` state で切り替え）
- 言語: EN / JA / KO（`detectLanguage()` で自動検出、`LanguageSwitcher` で手動切替）

### Sandbox Runtime（`src/sandbox/code.js`）
- Express の Document API を操作する
- `runtime.exposeApi()` で UI 側に関数を公開する
- 現在は `createRectangle()` のみ実装（テンプレート由来）

## 重要ファイル

| ファイル | 役割 |
|----------|------|
| `src/ui/index.jsx` | UI メイン（App + Toast + `ADDONS` 定数） |
| `src/ui/data/addons_data.json` | アドオンマスターデータ（424件、表示419件） |
| `src/ui/components/AddonCard.jsx` | ホーム画面グリッドカード |
| `src/ui/components/AddonListItem.jsx` | リスト行（詳細ボタン + IDコピーボタン） |
| `src/ui/components/AddonModal.jsx` | 詳細モーダル（fade/slide、Escape で閉じる） |
| `src/ui/components/CategoryList.jsx` | カテゴリ一覧 |
| `src/ui/components/LanguageSwitcher.jsx` | EN/JA/KO 切替 |
| `src/ui/components/SearchBar.jsx` | 検索バー |
| `src/ui/utils/i18n.js` | 翻訳ヘルパー（t, getLocalizedField, detectLanguage） |
| `src/ui/utils/constants.js` | `CATEGORY_ICONS` マップ |
| `src/ui/styles/styles.css` | パネルレイアウト + アニメーション定義 |
| `src/ui/locales/en.json` / `ja.json` / `ko.json` | 多言語テキスト |
| `src/sandbox/code.js` | Sandbox API（テンプレートのまま） |
| `manifest.json` | Add-on メタデータ（testId, entryPoints） |
| `webpack.config.js` | ビルド設定（2エントリーポイント: index + code） |

## データ構造

### addons_data.json のスキーマ

```json
{
  "id": "addon-id",
  "addOnId": "marketplace-addon-id",
  "nameEn": "English Name",
  "nameJa": "日本語名",
  "nameKo": "한국어 이름",
  "category": "category-key",
  "categoryJa": "カテゴリ名",
  "description": "英語説明文",
  "descriptionJa": "日本語説明文（手動翻訳）",
  "descriptionKo": "한국어 설명（手動翻訳）",
  "keywords": ["keyword1", "keyword2"],
  "keywordsJa": ["キーワード1", "キーワード2"],
  "keywordsKo": ["키워드1", "키워드2"],
  "featured": true,
  "marketplaceUrl": "https://new.express.adobe.com/add-ons?addOnId=xxxxx",
  "rating": 4.5,
  "userCount": "10K+"
}
```

- `marketplaceUrl` 形式: `https://new.express.adobe.com/add-ons?addOnId=<addOnId>`
- `addOnId` なし（空文字）のエントリは `ADDONS` 定数でフィルター除外される（5件）

### カテゴリ一覧（23カテゴリ）

| id | 概要 |
|----|------|
| accessibility | アクセシビリティ |
| advertising | 広告 |
| ai | AI |
| ai-audio | AI音声 |
| ai-video | AI動画 |
| audio | オーディオ |
| audio-social | 音声SNS |
| brand | ブランド |
| dam | デジタルアセット管理 |
| design | デザイン |
| design-assets | デザイン素材 |
| design-text | テキストデザイン |
| enterprise-dam | エンタープライズDAM |
| form | フォーム |
| i18n | 国際化 |
| marketing | マーケティング |
| project-mgmt | プロジェクト管理 |
| publishing | パブリッシング |
| social | SNS |
| social-ai | SNS×AI |
| storage | ストレージ連携 |
| typography | タイポグラフィ |
| utility | ユーティリティ |

## プロジェクト固有スキル

### i18n ヘルパー（`src/ui/utils/i18n.js`）
- `t(key, locale)` — ロケールキーから翻訳文字列を取得
- `getLocalizedField(addon, 'name', locale)` — `nameJa/En/Ko` の優先取得
- `getLocalizedCategory(category, locale)` — カテゴリキーの翻訳
- `detectLanguage()` — ブラウザ言語の自動検出

### ADDONS フィルター定数（`index.jsx` モジュールレベル）

```javascript
const ADDONS = addonsData.addons.filter(a => a.marketplaceUrl);
```

検索・カテゴリ・全件・ホームのすべてで `ADDONS` を使用（`addonsData.addons` は直接使わない）。

### addOnId の抽出

```javascript
const match = (addon.marketplaceUrl || '').match(/addOnId=([^&]+)/);
const addOnId = match ? match[1] : null;
```

### クリップボードコピー（execCommand フォールバック必須）

`navigator.clipboard.writeText()` が sandbox でブロックされるため、必ず `document.execCommand('copy')` フォールバックを実装する。

### Hover エフェクト

CSS `:hover` は inline style に効かないため、`onMouseEnter` / `onMouseLeave` + `useState` で制御する。

### Border の inline style

CSS transition のため `border` shorthand ではなく `borderWidth` / `borderStyle` / `borderColor` longhand を使う。

## 禁止事項

| # | 禁止 | 理由 |
|---|------|------|
| 1 | `manifest.json` の `testId` を変更 | アドオン ID が壊れる |
| 2 | `window.open()` で外部URL を開く | COOP ヘッダーでブロックされる |
| 3 | `navigator.clipboard.writeText()` のみ使用 | sandbox でブロック（`execCommand` フォールバック必須） |
| 4 | `addonsData.addons` を直接参照 | `addOnId` なしエントリが混入する（`ADDONS` 定数を使う） |
| 5 | `descriptionJa` / `descriptionKo` の自動翻訳 | ユーザーが手動翻訳する方針 |
| 6 | 外部 CSS ファイルを新たに追加 | CSS-in-JS（`styles` オブジェクト）が方針 |
| 7 | `claude -p` をスクリプト内から実行 | ネストされた Claude セッションはエラー |
| 8 | `border` shorthand を inline style に使用 | CSS transition が機能しない（longhand 必須） |
| 9 | `testId` を URL に使用 | `testId` ≠ `addOnId`（URL に使えるのは `addOnId` のみ） |

## 既知の技術的負債

- **未使用ファイル**: `src/ui/components/App.jsx` / `App.css` / `src/ui/utils/marketplace.js` がテンプレート由来で残存
- **`code.js` の未活用**: Sandbox API は `createRectangle()` のみ（テンプレートのまま）
- **翻訳未完**: `descriptionJa` / `descriptionKo` は新規382件が未翻訳（手動翻訳を待つ）

## 技術的負債解消ネクストアクション

### フェーズ A: クリーンアップ（完了）
- [x] `src/ui/components/App.jsx` を削除（テンプレート由来、未使用）
- [x] `src/ui/components/App.css` を削除（同上）
- [x] `src/ui/utils/marketplace.js` を削除（未使用）

### フェーズ B: 申請準備
- [ ] `manifest.json` に多言語メタデータ追加（name/description EN/JA/KO）
- [ ] アイコン画像 512×512px を作成 → `src/ui/icons/` に配置
- [ ] スクリーンショット 5 枚（日本語 UI）→ `src/ui/screenshots/` に配置

### フェーズ C: データ補完
- [ ] 残り5件（`text-gradient-pro`, `undraw`, `tiktok-music`, `mockuuups`, `vcard-generator`）の `marketplaceUrl` を調査・入力
  - Adobe Marketplace で名前検索 → `addOnId` 取得 → `https://new.express.adobe.com/add-ons?addOnId=xxxxx`

### フェーズ D: 申請
- [ ] Adobe Developer Console でレビュー申請

## スタイリング方針

- CSS-in-JS（`const styles = {}` オブジェクト）+ `src/ui/styles/styles.css`（レイアウト・アニメーション）
- 新規スタイルは原則 CSS-in-JS に追加する（外部 CSS ファイルを増やさない）
- カラーパレット: プライマリ `#0066FF`、背景 `#F5F7FA`、テキスト `#1E1E1E`、サブ `#666`
- フォント: `"Noto Sans JP", sans-serif`
- 幅は最大 400px（パネル UI 想定）

## Webpack ビルドの注意点

- `experiments.outputModule: true` で ES Module 出力
- `add-on-sdk-document-sandbox` と `express-document-sdk` は external（バンドルしない）
- Adobe SDK は CDN から読み込む（`https://new.express.adobe.com/static/add-on-sdk/sdk.js`）
- ビルド成果物は `dist/` に出力（`index.html`, `index.js`, `code.js`）

## Adobe Add-on の制約

- UI Runtime から直接 Express Document API は呼べない（Sandbox 経由のみ）
- `manifest.json` の `testId` は変更しない
- Add-on は Adobe Express のパネル内（幅約 400px）で動作する

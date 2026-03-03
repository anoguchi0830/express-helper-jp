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
- React 18 + CSS-in-JS（`styles` オブジェクト）で実装
- Adobe Add-on SDK を CDN から読み込み（`addOnUISdk.ready` を待ってから React をマウント）
- コンポーネントはすべて `index.jsx` に集約されている（モノリシック構成）
  - `AddonSearchPortal`（メイン）、`AddonCard`、`AddonListItem`、`AddonModal`
- ビュー状態: `'home'` / `'search'`（`view` state で切り替え）

### Sandbox Runtime（`src/sandbox/code.js`）
- Express の Document API を操作する
- `runtime.exposeApi()` で UI 側に関数を公開する
- 現在は `createRectangle()` のみ実装（テンプレート由来）

## 重要ファイル

| ファイル | 役割 |
|----------|------|
| `src/ui/index.jsx` | UI 全体（コンポーネント + スタイル定義） |
| `src/ui/data/addons_data.json` | アドオンマスターデータ（45件） |
| `src/sandbox/code.js` | Sandbox API（Express ドキュメント操作） |
| `manifest.json` | Add-on メタデータ（testId, entryPoints） |
| `webpack.config.js` | ビルド設定（2エントリーポイント: index + code） |

## データ構造

### addons_data.json のスキーマ

```json
{
  "id": "addon-id",
  "nameEn": "English Name",
  "nameJa": "日本語名",
  "category": "category-key",
  "categoryJa": "カテゴリ名",
  "description": "日本語説明文",
  "keywords": ["キーワード1", "キーワード2"],
  "featured": true,
  "marketplaceUrl": "https://...",
  "rating": 4.5,
  "userCount": "10K+"
}
```

### カテゴリ一覧（8カテゴリ）

| id | 日本語名 |
|----|----------|
| design-assets | デザイン素材 |
| accessibility | アクセシビリティ |
| ai | AI・音声/動画 |
| storage | ストレージ連携 |
| marketing | SNS・マーケティング |
| utility | ユーティリティ |
| audio | 音楽・オーディオ |
| text | テキスト効果 |

## 既知の技術的負債

- **データ二重管理**: `addons_data.json` が存在するが、`index.jsx` 内にも `sampleAddons` がハードコードされており、JSON ファイルは未使用
- **モノリシック構成**: UI コンポーネントがすべて `index.jsx` 1ファイルに集約（572行）
- **未使用ファイル**: `src/ui/components/App.jsx` / `App.css` はテンプレート由来で未使用
- **`code.js` の未活用**: Sandbox API は `createRectangle()` のみ（テンプレートのまま）

## スタイリング方針

- CSS-in-JS（`const styles = {}` オブジェクト）を使用
- 外部 CSS ファイルなし
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

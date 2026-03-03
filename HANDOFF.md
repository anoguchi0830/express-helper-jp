# Express Helper JP — 引き継ぎドキュメント

最終更新: 2026-03-03
ビルド状態: ✅ `webpack compiled successfully`

---

## 現在の実装状態

Phase 0〜7 すべて完了・動作確認済み。Adobe Express パネルとして動作する多言語アドオン検索ポータル。

### 完了済み機能一覧

- **多言語対応**: EN / JA / KO の3言語、ブラウザ言語自動検出 + LocalStorage 保存
- **検索**: 関連度スコアリング（名前3pt / KW・カテゴリ2pt / 説明1pt）
- **ホーム画面**: 人気アドオン グリッド6件 + カテゴリ一覧 + 全件表示ボタン
- **カテゴリ絞り込み**: 23カテゴリ、件数表示
- **ソート**: デフォルト順 / 名前 A↑ / 名前 Z↓（2回クリックでトグル）
- **0件時サジェスト**: 言語別おすすめキーワード（クリックで即検索）
- **詳細モーダル**: フェード+スライドアニメーション、Escape キー / 外側クリックで閉じる
- **「Expressで探す」ボタン**: Marketplace URL をクリップボードにコピー + トースト通知（実機動作確認済み）
- **パネルレイアウト**: ヘッダー固定 + コンテンツスクロール
- **SDK ローディング**: `addOnUISdk.ready` 待機中はスピナー表示

---

## ファイル構成

```
express-helper-jp/
├── src/
│   ├── manifest.json               ← Add-on メタデータ（testId 変更不可）
│   ├── ui/
│   │   ├── index.jsx               ← メインアプリ（App, AddonList, SortBar, NoResults, Toast）
│   │   ├── styles/styles.css       ← パネルレイアウト + アニメーション
│   │   ├── data/addons_data.json   ← 43件のアドオンデータ（38件は marketplaceUrl 設定済み）
│   │   ├── locales/
│   │   │   ├── en.json
│   │   │   ├── ja.json
│   │   │   └── ko.json
│   │   ├── components/
│   │   │   ├── AddonCard.jsx       ← ホームグリッドカード
│   │   │   ├── AddonListItem.jsx   ← リスト行（詳細ボタン + 「Expressで探す」ボタン）
│   │   │   ├── AddonModal.jsx      ← 詳細モーダル
│   │   │   ├── CategoryList.jsx    ← カテゴリ一覧
│   │   │   ├── LanguageSwitcher.jsx
│   │   │   └── SearchBar.jsx
│   │   └── utils/
│   │       ├── i18n.js             ← detectLanguage, t, getLocalizedField
│   │       ├── constants.js        ← CATEGORY_ICONS
│   │       └── marketplace.js      ← 使用中（getMarketplaceUrl() を export）
│   └── sandbox/code.js             ← 未使用（テンプレートのまま）
├── CLAUDE_CLI_INSTRUCTIONS.md
└── HANDOFF.md                      ← このファイル
```

---

## データ仕様

### addons_data.json スキーマ

```json
{
  "id": "addon-id",
  "nameEn": "English Name",
  "nameJa": "日本語名",
  "nameKo": "한국어 이름",
  "category": "category-key",
  "descriptionEn": "...",
  "descriptionJa": "...",
  "descriptionKo": "...",
  "keywordsEn": ["keyword1"],
  "keywordsJa": ["キーワード1"],
  "keywordsKo": ["키워드1"],
  "featured": true,
  "marketplaceUrl": ""
}
```

- `rating` / `userCount` は全件削除済み（ダミーデータだったため）
- 合計 **43件**（`barcode-designer` 削除済み）
- `marketplaceUrl` は38件に `https://new.express.adobe.com/add-ons?addOnId=xxxxx` 形式の URL を設定済み
- 未設定（空文字）は5件: `text-gradient-pro`, `undraw`, `tiktok-music`, `mockuuups`, `vcard-generator`
  → `getMarketplaceUrl()` が name 検索 URL にフォールバック

---

## 重要な技術的制約（実機確認済み）

### 外部 URL を開く手段がない

| 方法 | 結果 | 理由 |
|------|------|------|
| `window.open()` | ❌ ブロック | Adobe Express の COOP ヘッダー（ERR_BLOCKED_BY_RESPONSE） |
| `addOnUISdk.app.openBrowserUrl()` | ❌ 存在しない | CDN 版 SDK に未実装 |
| `addOnUISdk.app.ui.openEditorPanel("addOns", { type:"search", ... })` | ❌ パネルが開かない | URL は変わるが UI に変化なし（実機確認） |

### クリップボード

- `navigator.clipboard.writeText()` → sandbox 内で Permission Error（`allow-clipboard-write` は manifest で許可不可）
- **`document.execCommand('copy')` → 動作する**（ユーザー操作起点であれば sandbox 内でも有効）
- 実装は2段階 try-catch：Clipboard API → 失敗したら execCommand フォールバック

### manifest.json で許可される sandbox 値

```
allow-popups | allow-presentation | allow-downloads | allow-popups-to-escape-sandbox
```

`allow-clipboard-write` は**許可されていない**（試みてビルドエラーを確認済み）。

---

## 「Expressで探す」ボタンの実装（現在の正解）

```javascript
// index.jsx の App コンポーネント内
const openInExpress = async (addon) => {
  const url = getMarketplaceUrl(addon);  // Marketplace URL 全体をコピー

  let copied = false;
  try {
    await navigator.clipboard.writeText(url);
    copied = true;
  } catch {
    try {
      const ta = document.createElement('textarea');
      ta.value = url;
      ta.style.cssText = 'position:fixed;opacity:0;pointer-events:none';
      document.body.appendChild(ta);
      ta.focus(); ta.select();
      copied = document.execCommand('copy');
      document.body.removeChild(ta);
    } catch (e) { console.error('Copy failed:', e); }
  }

  if (copied) {
    setToast(t('addon.urlCopied', locale));
    if (toastTimerRef.current) clearTimeout(toastTimerRef.current);
    toastTimerRef.current = setTimeout(() => setToast(null), 3500);
  }
};
```

**UX フロー**: ボタン押下 → Marketplace URL がクリップボードにコピー → トーストが3.5秒表示（「URLをコピーしました — ブラウザに貼り付けて開いてください」）

### state 管理（App コンポーネント）

```javascript
const [toast, setToast] = useState(null);     // トーストメッセージ（null = 非表示）
const toastTimerRef = useRef(null);           // タイマー参照（多重クリック時のリセット用）
```

---

## コンポーネント間のデータフロー

```
App（index.jsx）
├── openInExpress(addon) — クリップボードコピー + トースト
│
├── panel-top（固定ヘッダー）
│   ├── LanguageSwitcher（locale, setLocale）
│   └── SearchBar（value, onChange）
│
├── panel-content（スクロール領域）
│   ├── [home] AddonCard（addon, locale, onClick）
│   ├── [home] CategoryList（categories, locale, onCategoryClick）
│   ├── [search|category|all] SortBar + AddonList
│   │   └── AddonListItem（addon, locale, onClick, openInExpress）
│   └── NoResults（locale, onSuggestClick）
│
├── AddonModal（addon, locale, onClose, openInExpress）
└── Toast（position:fixed, bottom:16px — toast state が非 null のとき表示）
```

---

## ロケールキー（addon セクション）

| キー | EN | JA | KO |
|------|----|----|-----|
| `addon.openInExpress` | `Copy Marketplace Link` | `MarketplaceのURLをコピー` | `Marketplace URL 복사` |
| `addon.urlCopied` | `URL copied — paste in your browser to open` | `URLをコピーしました — ブラウザに貼り付けて開いてください` | `URL 복사됨 — 브라우저에 붙여넣어 여세요` |
| `addon.viewDetails` | `Details` | `詳細` | `상세정보` |
| `addon.category` | `Category` | `カテゴリ` | `카테고리` |
| `addon.description` | `Description` | `説明` | `설명` |
| `addon.keywords` | `Related Keywords` | `関連キーワード` | `관련 키워드` |

---

## add-on-detail.json（プロジェクトルート）

Adobe Marketplace API の全カタログレスポンスを保存したファイル。

- 形式: JSON Lines（NDJSON）— 1行 = 1バッチ、合計 18行 × 約23件 = **419件**
- 構造:
  ```json
  {
    "addonId": "wjkl4l48l",
    "addon": {
      "localizedMetadata": {
        "name": "Express Helper JP",
        "summary": "...",
        "description": "...",
        "keywords": ["..."]
      }
    },
    "publisher": { ... }
  }
  ```
- 用途: `addOnId` を使って38件の `marketplaceUrl` を設定するのに使用済み
- 将来活用: 「全アドオン一覧」機能のベースデータとして使える

### testId ≠ addOnId（重要な技術的知見）

- `manifest.json` の `testId`（例: `w52l6j58g`）は開発・テスト用 ID
- Marketplace の `addOnId`（例: `wjkl4l48l`）は公開後に付与される別 ID
- URL に使えるのは `addOnId` のみ（`https://new.express.adobe.com/add-ons?addOnId=xxxxx`）
- `testId` で URL を作っても機能しない

---

## manifest.json の現在の設定

```json
{
  "testId": "w52l6j58g",
  "name": "Express Helper Jp",
  "version": "1.0.0",
  "manifestVersion": 2,
  "requirements": { "apps": [{ "name": "Express", "apiVersion": 1 }] },
  "entryPoints": [{
    "type": "panel",
    "id": "panel1",
    "main": "index.html",
    "documentSandbox": "code.js",
    "permissions": {
      "sandbox": ["allow-downloads"]
    }
  }]
}
```

---

## 未実施の残タスク

### Marketplace 申請準備
- [ ] `manifest.json` に多言語メタデータ追加（name / description を EN/JA/KO で）
- [ ] アドオンアイコン画像（512×512 px PNG）作成・設定
- [ ] スクリーンショット 5 枚（審査提出用）
- [ ] `manifest.json` の `apiVersion` / `manifestVersion` 最終確認

### データ充実
- [ ] `addons_data.json` の残り5件に `marketplaceUrl` を入力（`text-gradient-pro`, `undraw`, `tiktok-music`, `mockuuups`, `vcard-generator`）

### 品質確認
- [ ] 3言語すべてで全機能を動作確認
- [ ] 320px 幅での表示確認

### Marketplace 申請
- [ ] `npm run package` でパッケージ作成
- [ ] Developer Console でアップロード・審査送信

---

## 開発コマンド

```bash
npm run start    # 開発サーバー（https://localhost:5241）
npm run build    # プロダクションビルド → dist/
npm run package  # .zip パッケージ作成（審査提出用）
```

---

## カラーパレット

| 用途 | カラー |
|------|--------|
| プライマリ | `#0066FF` |
| プライマリ（暗） | `#0044CC` |
| 薄い青背景 | `#EEF4FF` |
| ボーダー（薄い青） | `#B3CCFF` |
| 背景 | `#FFFFFF` |
| サブ背景 | `#F5F7FA` |
| ボーダー | `#E0E0E0` |
| テキスト（主） | `#1E1E1E` |
| テキスト（副） | `#666` |
| テキスト（補助） | `#999` |

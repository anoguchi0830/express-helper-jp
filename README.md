# Addon Explorer — Adobe Express アドオン発見ポータル

Adobe Express 向けのアドオンを日本語・韓国語・英語で検索・発見できる Web Add-on パネルです。

## 機能

### 多言語検索
- 日本語・韓国語・英語でアドオンを検索できます
- 関連度スコアリングにより、最も関連性の高い結果が上位に表示されます
- 検索結果が 0 件の場合は、おすすめキーワードをサジェストします

### カテゴリ閲覧
23 カテゴリからアドオンを絞り込めます（AI、デザイン、SNS、ストレージなど）。

### アドオン一覧・詳細
- グリッドカードでおすすめアドオンをホーム表示
- リスト形式で全 419 件を閲覧
- 詳細モーダルで説明・評価・ユーザー数を確認

### 言語切替
EN / JA / KO を手動で切り替え可能。ブラウザ言語を自動検出して初期表示言語を設定します。

### Adobe Express で開く
各アドオンの検索用 ID をクリップボードにコピーし、Adobe Express のアドオン検索に貼り付けることで直接アクセスできます。

### 並び替え
デフォルト順・名前昇順・名前降順でリストを並び替えできます。

## 検索の仕組み

クライアントサイドのみで完結する関連度スコアリング検索です。外部 API への問い合わせは行いません。

入力クエリに対して、各アドオンに以下の基準でスコアを付与し、スコア降順に結果を表示します。

| 一致箇所 | スコア |
|----------|--------|
| アドオン名 | +3 |
| キーワード | +2 |
| カテゴリ名 | +2 |
| 説明文 | +1 |

スコア 0 のアドオンは除外されます。言語設定に応じて対応するフィールド（`nameJa`、`keywordsJa`、`descriptionJa` など）を参照します。

## データ

- 収録件数: **419 件**（Adobe Express Marketplace 公式カタログより）
- 対応言語: 名前・説明・キーワードを EN / JA / KO で収録
- カテゴリ数: 23 カテゴリ

## 技術スタック

| 項目 | 内容 |
|------|------|
| ランタイム | Adobe Express Web Add-on (Manifest V2) |
| UI | React 18 + Spectrum Web Components (Express テーマ) |
| ビルド | Webpack 5 + Babel |
| 多言語 | カスタム i18n ヘルパー（EN / JA / KO） |

## 開発・ビルド

```bash
npm install
npm run start    # 開発サーバー起動（https://localhost:5241）
npm run build    # プロダクションビルド → dist/
npm run package  # Add-on パッケージ化（.zip）
```

---

# Addon Explorer — Adobe Express Add-on Discovery Portal

A Web Add-on panel for discovering Adobe Express add-ons in Japanese, Korean, and English.

## Features

### Multilingual Search
- Search add-ons in Japanese, Korean, or English
- Relevance scoring surfaces the most relevant results first
- Suggested keywords are shown when no results are found

### Category Browsing
Browse add-ons by 23 categories (AI, Design, Social, Storage, and more).

### Add-on List & Details
- Featured add-ons displayed as grid cards on the home screen
- Full list of 419 add-ons in list view
- Detail modal showing description, rating, and user count

### Language Switching
Toggle between EN / JA / KO manually. The initial language is auto-detected from browser settings.

### Open in Adobe Express
Copy an add-on's search ID to the clipboard and paste it into Adobe Express's add-on search for direct access.

### Sorting
Sort the list by default order, name A-Z, or name Z-A.

## How Search Works

Search is processed entirely client-side with no external API calls.

Each add-on is scored against the input query using the following criteria:

| Match field | Score |
|-------------|-------|
| Add-on name | +3 |
| Keywords | +2 |
| Category name | +2 |
| Description | +1 |

Add-ons with a score of 0 are excluded. Results are sorted by score descending. The search reads locale-specific fields (`nameJa`, `keywordsJa`, `descriptionJa`, etc.) based on the active language setting.

## Data

- **419 add-ons** sourced from the official Adobe Express Marketplace catalog
- Name, description, and keywords available in EN / JA / KO
- 23 categories

## Tech Stack

| Item | Details |
|------|---------|
| Runtime | Adobe Express Web Add-on (Manifest V2) |
| UI | React 18 + Spectrum Web Components (Express theme) |
| Build | Webpack 5 + Babel |
| i18n | Custom i18n helper (EN / JA / KO) |

## Development

```bash
npm install
npm run start    # Dev server (https://localhost:5241)
npm run build    # Production build → dist/
npm run package  # Package as .zip for distribution
```

---

# Addon Explorer — Adobe Express 애드온 탐색 포털

Adobe Express 애드온을 한국어·일본어·영어로 검색하고 발견할 수 있는 Web Add-on 패널입니다.

## 기능

### 다국어 검색
- 한국어·일본어·영어로 애드온을 검색할 수 있습니다
- 관련도 스코어링으로 가장 관련성 높은 결과를 상위에 표시합니다
- 검색 결과가 0건인 경우 추천 키워드를 제안합니다

### 카테고리 탐색
23개 카테고리에서 애드온을 필터링할 수 있습니다 (AI, 디자인, SNS, 스토리지 등).

### 애드온 목록 및 상세보기
- 홈 화면에서 추천 애드온을 그리드 카드로 표시
- 전체 419개 애드온을 리스트 형식으로 열람
- 상세 모달에서 설명·평점·사용자 수 확인

### 언어 전환
EN / JA / KO를 수동으로 전환 가능. 브라우저 언어를 자동 감지하여 초기 표시 언어를 설정합니다.

### Adobe Express에서 열기
각 애드온의 검색용 ID를 클립보드에 복사하여 Adobe Express 애드온 검색에 붙여넣으면 직접 접근할 수 있습니다.

### 정렬
기본 순서·이름 오름차순·이름 내림차순으로 목록을 정렬할 수 있습니다.

## 검색 방식

검색은 모두 클라이언트 사이드에서 처리됩니다 (외부 API 호출 없음).

입력 쿼리에 대해 각 애드온에 다음 기준으로 점수를 부여하고, 점수 내림차순으로 결과를 표시합니다.

| 일치 항목 | 점수 |
|-----------|------|
| 애드온 이름 | +3 |
| 키워드 | +2 |
| 카테고리명 | +2 |
| 설명문 | +1 |

점수 0인 애드온은 제외됩니다. 언어 설정에 따라 해당 필드(`nameKo`、`keywordsKo`、`descriptionKo` 등)를 참조합니다.

## 데이터

- 수록 건수: **419개** (Adobe Express Marketplace 공식 카탈로그 기반)
- 이름·설명·키워드를 EN / JA / KO로 수록
- 카테고리 수: 23개

## 기술 스택

| 항목 | 내용 |
|------|------|
| 런타임 | Adobe Express Web Add-on (Manifest V2) |
| UI | React 18 + Spectrum Web Components (Express 테마) |
| 빌드 | Webpack 5 + Babel |
| 다국어 | 커스텀 i18n 헬퍼 (EN / JA / KO) |

## 개발·빌드

```bash
npm install
npm run start    # 개발 서버 시작 (https://localhost:5241)
npm run build    # 프로덕션 빌드 → dist/
npm run package  # 배포용 패키지(.zip) 생성
```

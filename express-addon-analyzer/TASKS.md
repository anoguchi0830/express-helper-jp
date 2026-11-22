# TASKS

## 完了
- [x] サンプル CSV の構造調査（注釈行・週次・年またぎ分割行）
- [x] 要件確認: 形態=ローカル Web ダッシュボード / 機能=推移・複数アドオン比較・利用率/離脱・CSV 蓄積
- [x] `index.html` 初版（CSV ドロップ取込、カード、推移グラフ、比較テーブル、localStorage 蓄積、統合 CSV 書き出し）
- [x] 複数アドオンの色分け重ね表示（凡例で表示/非表示）
- [x] 実データ確認後の修正
  - [x] 重ね表示時のカードを表示中アドオンの合計にする
  - [x] 前 4 週比の ±5% 未満を中立表示、前 4 週が 0 のときは「–」
  - [x] 4 週移動平均は 4 週分たまってから描画
  - [x] 年またぎの分割行を次の土曜へ寄せて合算（取込時 + 保存データの migrate）
- [x] X 軸切替（日付 / 公開からの週数）
- [x] スケール切替（線形 / 対数 / 正規化）
- [x] グラフ設定のリセットボタン
- [x] 日本語 / 英語の表示切替（`I18N` 辞書 + `tr()`。選択は localStorage `addon-analyzer-lang` に保存、初期値はブラウザ言語）

## 未着手
- [ ] カード 6 枚目の折り返しを解消（5 枚にする or 3×2 固定）
- [ ] アドオン名のリネーム・非表示・削除（CSV ごとに名前が変わると別アドオン扱いになる）
- [ ] Invocations の週次推移を Installs と並べて見られるビュー（再利用度の確認）
- [ ] 実データ 3 本での最終確認（ダミー CSV でのみ全モード検証済み）
- [ ] 年またぎ行の「前方に寄せる」解釈が正しいか確認（Adobe 側の仕様 or 他の年の CSV で検証）

## 公開（2026-11-22 完了）
- [x] 静的ページとして公開: https://analyzer.notechlabs.com（GitHub Pages + Cloudflare DNS `analyzer` CNAME / DNS only、HTTPS 強制済み）
- [x] 公開用リポジトリ: `anoguchi0830/addon-analyzer`（public。ローカルは `/Volumes/Laxar/Projects/addon-analyzer`。`index.html` / `CNAME` / `README.md` のみ）
- 更新手順: `scripts/publish.sh [--dry-run] [コミットメッセージ]`（公開用リポジトリへコピー → commit → push、数分で反映。外部通信系の記述が混入していたら中止する）
- [x] 公開版への同期スクリプト `scripts/publish.sh`（dry-run とガードは検証済み、実 push は初回更新時に確認）
- [ ] 反応を見て Adobe Express アドオン化を判断（パネル幅 400px 向けレイアウト、`manifest.json` 新規作成。`testId` は一度決めたら変更不可）

## 昇格提案
- 実データ CSV の扱い（リポジトリに含めない）は `.gitignore` に `*.csv` を入れて明文化するか検討（承認待ち）

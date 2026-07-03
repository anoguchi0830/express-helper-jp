#!/usr/bin/env node
/**
 * extract_today_addons.cjs
 *
 * 本日 docs/addons_data.json に追加されたアドオンエントリを JSON で stdout に出力する。
 *
 * 抽出ロジック:
 *   1. 本日（ローカル日付）の docs/addons_data.json へのコミットを git log で取得
 *   2. コミットがあれば、最古の本日コミットの親時点のデータと
 *      現在のワーキングツリー版を addOnId（無ければ id）の集合差分で比較
 *   3. 親が無い / git show 失敗 / 本日コミットなし の場合は
 *      isNew === true のエントリにフォールバック（stderr に注記）
 *
 * 出力（stdout、JSON のみ）:
 *   { "source": "git-diff" | "isNew-fallback", "date": "YYYY-MM-DD",
 *     "count": N, "addons": [ { nameEn, nameJa, descriptionJa, description,
 *                               category, categoryJa, addOnId } ] }
 *
 * 人間向けメッセージはすべて stderr に出す。エラー時は非ゼロ exit。
 */

'use strict';

const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const REPO_ROOT = path.resolve(__dirname, '..');
const DATA_PATH = 'docs/addons_data.json';

// ローカル日付を YYYY-MM-DD で返す
function todayLocal() {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

// git コマンドを実行して stdout（文字列）を返す。失敗時は例外
function git(args) {
  return execFileSync('git', args, {
    cwd: REPO_ROOT,
    encoding: 'utf8',
    maxBuffer: 64 * 1024 * 1024,
  });
}

// エントリの識別キー（addOnId 優先、無ければ id）
function entryKey(addon) {
  return addon.addOnId || addon.id || null;
}

// 出力用に必要フィールドだけ抜き出す
function pickFields(addon) {
  return {
    nameEn: addon.nameEn || '',
    nameJa: addon.nameJa || '',
    descriptionJa: addon.descriptionJa || '',
    description: addon.description || '',
    category: addon.category || '',
    categoryJa: addon.categoryJa || '',
    addOnId: addon.addOnId || '',
  };
}

function main() {
  const date = todayLocal();

  // 現在のワーキングツリー版を読み込む
  let current;
  try {
    current = JSON.parse(fs.readFileSync(path.join(REPO_ROOT, DATA_PATH), 'utf8'));
  } catch (err) {
    process.stderr.write(`エラー: ${DATA_PATH} の読み込み/パースに失敗しました: ${err.message}\n`);
    process.exit(1);
  }
  const currentAddons = Array.isArray(current.addons) ? current.addons : null;
  if (!currentAddons) {
    process.stderr.write(`エラー: ${DATA_PATH} に addons 配列がありません\n`);
    process.exit(1);
  }

  // 本日のコミット群を取得（新しい順）
  let todayCommits = [];
  try {
    const out = git(['log', `--since=${date} 00:00:00`, '--format=%H', '--', DATA_PATH]);
    todayCommits = out.split('\n').filter(Boolean);
  } catch (err) {
    process.stderr.write(`警告: git log の実行に失敗しました（${err.message}）。isNew フォールバックを使用します\n`);
  }

  let result = null;

  if (todayCommits.length > 0) {
    // 最古の本日コミットの親時点のデータと比較
    const oldest = todayCommits[todayCommits.length - 1];
    try {
      const baseRaw = git(['show', `${oldest}^:${DATA_PATH}`]);
      const base = JSON.parse(baseRaw);
      const baseKeys = new Set(
        (Array.isArray(base.addons) ? base.addons : []).map(entryKey).filter(Boolean)
      );
      const added = currentAddons.filter((a) => {
        const key = entryKey(a);
        return key && !baseKeys.has(key);
      });
      result = { source: 'git-diff', addons: added };
      process.stderr.write(
        `本日のコミット ${todayCommits.length} 件を検出。親 ${oldest.slice(0, 7)}^ との差分で ${added.length} 件を抽出しました\n`
      );
    } catch (err) {
      process.stderr.write(
        `注記: 親コミット時点のデータ取得に失敗しました（初回コミット、または git show エラー: ${err.message}）。isNew フォールバックを使用します\n`
      );
    }
  } else {
    process.stderr.write('注記: 本日の docs/addons_data.json へのコミットはありません。isNew フォールバックを使用します\n');
  }

  if (!result) {
    // フォールバック: isNew === true のエントリ
    const added = currentAddons.filter((a) => a.isNew === true);
    result = { source: 'isNew-fallback', addons: added };
  }

  const output = {
    source: result.source,
    date,
    count: result.addons.length,
    addons: result.addons.map(pickFields),
  };

  process.stdout.write(JSON.stringify(output, null, 2) + '\n');
}

main();

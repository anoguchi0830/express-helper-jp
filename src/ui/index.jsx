import React, { useState, useEffect, useRef } from 'react';
import ReactDOM from 'react-dom/client';
import addOnUISdk from 'https://new.express.adobe.com/static/add-on-sdk/sdk.js';
import { Theme } from '@swc-react/theme';
import '@spectrum-web-components/theme/express/theme-light.js';
import '@spectrum-web-components/theme/express/scale-medium.js';
import '@spectrum-web-components/theme/scale-medium.js';
import '@spectrum-web-components/theme/theme-light.js';
import { Button } from '@swc-react/button';
import { ActionButton } from '@swc-react/action-button';
import { ActionGroup } from '@swc-react/action-group';

import LanguageSwitcher from './components/LanguageSwitcher';
import SearchBar from './components/SearchBar';
import AddonCard from './components/AddonCard';
import AddonListItem from './components/AddonListItem';
import CategoryList from './components/CategoryList';
import AddonModal from './components/AddonModal';
import { detectLanguage, t, getLocalizedField, getLocalizedCategory } from './utils/i18n';
import { CATEGORY_ICONS } from './utils/constants';

import './styles/styles.css';

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 検索ロジック（関連度スコアリング付き）
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

// スコア: 名前一致 3pt / キーワード 2pt / カテゴリ 2pt / 説明 1pt
function scoreAddon(addon, lowerQuery, locale) {
  const localeSuffix = locale.charAt(0).toUpperCase() + locale.slice(1);
  const name = (getLocalizedField(addon, 'name', locale) || '').toLowerCase();
  const desc = (getLocalizedField(addon, 'description', locale) || '').toLowerCase();
  const kws  = addon[`keywords${localeSuffix}`] || addon.keywordsEn || addon.keywords || [];
  const cat  = getLocalizedCategory(addon.category, locale).toLowerCase();

  let score = 0;
  if (name.includes(lowerQuery))                        score += 3;
  if (kws.some(kw => kw.toLowerCase().includes(lowerQuery))) score += 2;
  if (cat.includes(lowerQuery))                         score += 2;
  if (desc.includes(lowerQuery))                        score += 1;
  return score;
}

function searchAddons(addons, query, locale) {
  if (!query.trim()) return [];
  const lowerQuery = query.toLowerCase();

  return addons
    .map(addon => ({ addon, score: scoreAddon(addon, lowerQuery, locale) }))
    .filter(({ score }) => score > 0)
    .sort((a, b) => b.score - a.score)   // 関連度降順
    .map(({ addon }) => addon);
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// ソートロジック
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

const SORT_OPTIONS = [
  { id: 'default', labelKey: 'sort.default' },
  { id: 'name',    labelKey: 'sort.name'    }
];

function sortAddons(addons, sortId, locale) {
  const arr = [...addons];
  if (sortId === 'name' || sortId === 'name-desc') {
    const dir = sortId === 'name' ? 1 : -1;
    return arr.sort((a, b) => {
      const na = getLocalizedField(a, 'name', locale) || '';
      const nb = getLocalizedField(b, 'name', locale) || '';
      return na.localeCompare(nb, locale) * dir;
    });
  }
  return arr;
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 言語別おすすめキーワード（0件時サジェスト）
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

const SUGGESTED_KEYWORDS = {
  en: ['QR code', 'AI', 'icons', 'music', 'storage', 'brand'],
  ja: ['QRコード', 'AI', 'アイコン', '音楽', 'ストレージ', 'ブランド'],
  ko: ['QR코드', 'AI', '아이콘', '음악', '스토리지', '브랜드']
};

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// サブコンポーネント
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

function SortBar({ sortId, onSortChange, locale }) {
  const nameActive = sortId === 'name' || sortId === 'name-desc';

  const handleNameClick = () => {
    if (sortId === 'name') onSortChange('name-desc');
    else if (sortId === 'name-desc') onSortChange('name');
    else onSortChange('name');
  };

  return (
    <ActionGroup style={{ marginBottom: '12px' }}>
      <ActionButton
        emphasized
        selected={sortId === 'default'}
        onClick={() => onSortChange('default')}
      >
        {t('sort.default', locale)}
      </ActionButton>
      <ActionButton
        emphasized
        selected={nameActive}
        onClick={handleNameClick}
      >
        {t('sort.name', locale)}{sortId === 'name' ? ' ↑' : sortId === 'name-desc' ? ' ↓' : ''}
      </ActionButton>
    </ActionGroup>
  );
}

function NoResults({ locale, onSuggestClick }) {
  const keywords = SUGGESTED_KEYWORDS[locale] || SUGGESTED_KEYWORDS.en;

  return (
    <div style={uiStyles.noResults}>
      <p style={uiStyles.noResultsText}>{t('search.noResults', locale)}</p>
      <p style={uiStyles.suggestLabel}>{t('browse.suggestedKeywords', locale)}</p>
      <div style={uiStyles.suggestTags}>
        {keywords.map(kw => (
          <ActionButton
            key={kw}
            onClick={() => onSuggestClick(kw)}
          >
            {kw}
          </ActionButton>
        ))}
      </div>
    </div>
  );
}

// リスト表示（stagger animation wrapper 付き）
function AddonList({ addons, locale, onSelect, openInExpress }) {
  return (
    <div style={uiStyles.list}>
      {addons.map((addon, i) => (
        <div
          key={addon.id}
          className="result-item"
          style={{ animationDelay: `${Math.min(i * 30, 300)}ms` }}
        >
          <AddonListItem addon={addon} locale={locale} onClick={() => onSelect(addon)} openInExpress={openInExpress} />
        </div>
      ))}
    </div>
  );
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// メインアプリ
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

function App({ addonsData }) {
  const ADDONS = addonsData.addons.filter(a => a.marketplaceUrl);
  const [locale, setLocale]                 = useState(detectLanguage());
  const [searchQuery, setSearchQuery]       = useState('');
  const [selectedAddon, setSelectedAddon]   = useState(null);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [view, setView]                     = useState('home'); // 'home'|'search'|'category'|'all'
  const [sortId, setSortId]                 = useState('default');
  const [toast, setToast]                   = useState(null);
  const toastTimerRef                       = useRef(null);
  const contentRef                          = useRef(null);

  useEffect(() => {
    localStorage.setItem('preferredLocale', locale);
  }, [locale]);

  // ビュー切り替え時にコンテンツ領域を先頭へ
  useEffect(() => {
    contentRef.current?.scrollTo({ top: 0, behavior: 'instant' });
  }, [view]);

  // 検索ハンドラ
  const handleSearch = (query) => {
    setSearchQuery(query);
    setSelectedCategory(null);
    setSortId('default');
    setView(query.trim() ? 'search' : 'home');
  };

  // カテゴリクリック
  const handleCategoryClick = (categoryId) => {
    setSelectedCategory(categoryId);
    setSearchQuery('');
    setSortId('default');
    setView('category');
  };

  // ホームへ戻る
  const handleBackToHome = () => {
    setView('home');
    setSelectedCategory(null);
    setSearchQuery('');
    setSortId('default');
  };

  // 全アドオン一覧へ
  const handleViewAll = () => {
    setSearchQuery('');
    setSelectedCategory(null);
    setSortId('default');
    setView('all');
  };

  // 0件サジェストからの検索
  const handleSuggestClick = (kw) => {
    setSearchQuery(kw);
    setSortId('default');
    setView('search');
  };

  // addOnId をクリップボードにコピーしてトースト表示
  const openInExpress = async (addon) => {
    const match = (addon.marketplaceUrl || '').match(/addOnId=([^&]+)/);
    const addOnId = match ? match[1] : null;
    if (!addOnId) return;

    let copied = false;
    try {
      await navigator.clipboard.writeText(addOnId);
      copied = true;
    } catch {
      try {
        const ta = document.createElement('textarea');
        ta.value = addOnId;
        ta.style.cssText = 'position:fixed;opacity:0;pointer-events:none';
        document.body.appendChild(ta);
        ta.focus();
        ta.select();
        copied = document.execCommand('copy');
        document.body.removeChild(ta);
      } catch (e) {
        console.error('Copy failed:', e);
      }
    }
    if (copied) {
      if (toastTimerRef.current) clearTimeout(toastTimerRef.current);
      setToast(t('addon.idCopied', locale));
      toastTimerRef.current = setTimeout(() => setToast(null), 3500);
    }
  };

  // 派生データ
  const searchResults   = sortAddons(searchAddons(ADDONS, searchQuery, locale), sortId === 'default' ? 'default' : sortId, locale);
  const featuredAddons  = ADDONS.filter(a => a.featured);
  const allAddons       = sortAddons(ADDONS, sortId, locale);
  const categoryAddons  = sortAddons(
    selectedCategory ? ADDONS.filter(a => a.category === selectedCategory) : [],
    sortId, locale
  );

  const categories = Object.keys(addonsData.metadata.categories)
    .map(id => ({ id, count: ADDONS.filter(a => a.category === id).length }))
    .filter(c => c.count > 0);

  return (
    <div className="panel-container">
      {/* ━━ 固定ヘッダーエリア ━━ */}
      <div className="panel-top">
        <header style={styles.header}>
          <h1 style={styles.title}>🔍 {t('app.title', locale)}</h1>
          <p style={styles.subtitle}>{t('app.subtitle', locale)}</p>
        </header>
        <LanguageSwitcher currentLocale={locale} onLocaleChange={setLocale} />
        <SearchBar
          value={searchQuery}
          onChange={handleSearch}
          placeholder={t('search.placeholder', locale)}
        />
      </div>

      {/* ━━ スクロール可能なコンテンツエリア ━━ */}
      <div className="panel-content" ref={contentRef}>

      {/* ━━ ホーム画面 ━━ */}
      {view === 'home' && (
        <div className="section-animate">
          {/* 人気アドオン */}
          <section style={styles.section}>
            <div style={styles.sectionHeader}>
              <h2 style={styles.sectionTitle}>🔥 {t('sections.featured', locale)}</h2>
            </div>
            <div style={styles.grid} className="addon-grid">
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

          {/* 全アドオン一覧へのリンク */}
          <div style={styles.viewAllWrap}>
            <Button variant="secondary" treatment="outline" onClick={handleViewAll}>
              {t('browse.viewAll', locale, { count: ADDONS.length })} →
            </Button>
          </div>

          {/* カテゴリ一覧 */}
          <CategoryList
            categories={categories}
            locale={locale}
            onCategoryClick={handleCategoryClick}
          />
        </div>
      )}

      {/* ━━ 検索結果画面 ━━ */}
      {view === 'search' && (
        <section style={styles.section} className="section-animate">
          <h2 style={styles.sectionTitle}>
            {t('search.resultsCount', locale, { query: searchQuery, count: searchResults.length })}
          </h2>

          {searchResults.length > 0 ? (
            <>
              <SortBar sortId={sortId} onSortChange={setSortId} locale={locale} />
              <AddonList addons={searchResults} locale={locale} onSelect={setSelectedAddon} openInExpress={openInExpress} />
            </>
          ) : (
            <NoResults locale={locale} onSuggestClick={handleSuggestClick} />
          )}
        </section>
      )}

      {/* ━━ カテゴリ絞り込み画面 ━━ */}
      {view === 'category' && (
        <section style={styles.section} className="section-animate">
          <div style={{ marginBottom: '12px' }}>
            <Button variant="secondary" treatment="outline" onClick={handleBackToHome}>← Back</Button>
          </div>
          <h2 style={styles.sectionTitle}>
            {CATEGORY_ICONS[selectedCategory] || '📦'} {getLocalizedCategory(selectedCategory, locale)}
            <span style={styles.count}> ({categoryAddons.length})</span>
          </h2>
          {categoryAddons.length > 1 && (
            <SortBar sortId={sortId} onSortChange={setSortId} locale={locale} />
          )}
          <AddonList addons={categoryAddons} locale={locale} onSelect={setSelectedAddon} openInExpress={openInExpress} />
        </section>
      )}

      {/* ━━ 全アドオン一覧画面 ━━ */}
      {view === 'all' && (
        <section style={styles.section} className="section-animate">
          <div style={{ marginBottom: '12px' }}>
            <Button variant="secondary" treatment="outline" onClick={handleBackToHome}>← Back</Button>
          </div>
          <h2 style={styles.sectionTitle}>
            📋 {t('browse.allAddons', locale)}
            <span style={styles.count}> ({allAddons.length})</span>
          </h2>
          <SortBar sortId={sortId} onSortChange={setSortId} locale={locale} />
          <AddonList addons={allAddons} locale={locale} onSelect={setSelectedAddon} openInExpress={openInExpress} />
        </section>
      )}

      </div>{/* /panel-content */}

      {/* 詳細モーダル（パネル外レイヤー） */}
      {selectedAddon && (
        <AddonModal
          addon={selectedAddon}
          locale={locale}
          onClose={() => setSelectedAddon(null)}
          openInExpress={openInExpress}
        />
      )}

      {toast && (
        <div style={uiStyles.toast}>{toast}</div>
      )}
    </div>
  );
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// スタイル定義
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

const styles = {
  header: {
    padding: '16px',
    background: 'linear-gradient(135deg, #5258E4 0%, #3B3DB4 100%)',
    color: '#FFFFFF',
    textAlign: 'center'
  },
  title:    { margin: 0, fontSize: '20px', fontWeight: 'bold' },
  subtitle: { margin: '4px 0 0', fontSize: '12px', opacity: 0.85 },
  section:  { padding: '16px' },
  sectionHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '12px'
  },
  sectionTitle: {
    fontSize: '16px',
    fontWeight: 'bold',
    color: 'var(--spectrum-gray-900, #1E1E1E)'
  },
  count: {
    fontSize: '14px',
    fontWeight: 'normal',
    color: 'var(--spectrum-gray-700, #666)'
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '10px'
  },
  viewAllWrap: {
    padding: '0 16px 8px',
    textAlign: 'right'
  }
};

// サブコンポーネント用スタイル
const uiStyles = {
  list: { display: 'flex', flexDirection: 'column', gap: '12px' },
  noResults: {
    textAlign: 'center',
    padding: '28px 16px'
  },
  noResultsText: {
    color: 'var(--spectrum-gray-700, #666)',
    lineHeight: '1.6',
    fontSize: '14px',
    marginBottom: '20px'
  },
  suggestLabel: {
    fontSize: '12px',
    color: 'var(--spectrum-gray-600, #999)',
    marginBottom: '10px'
  },
  suggestTags: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '8px',
    justifyContent: 'center'
  },
  toast: {
    position: 'fixed',
    bottom: '16px',
    left: '50%',
    transform: 'translateX(-50%)',
    backgroundColor: 'rgba(30,30,30,0.92)',
    color: '#FFFFFF',
    padding: '10px 16px',
    borderRadius: '8px',
    fontSize: '12px',
    lineHeight: '1.5',
    textAlign: 'center',
    maxWidth: '320px',
    width: 'calc(100% - 32px)',
    zIndex: 2000,
    pointerEvents: 'none'
  }
};

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// ローディング画面 + AppWrapper
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

function LoadingScreen() {
  return (
    <div className="loading-screen">
      <div className="loading-spinner" />
      <span style={{ fontSize: '13px', color: 'var(--spectrum-gray-600, #999)' }}>Loading...</span>
    </div>
  );
}

function NetworkErrorScreen({ onRetry }) {
  const locale = detectLanguage();
  return (
    <div className="loading-screen">
      <p style={{ fontSize: '15px', fontWeight: 600, margin: '0 0 8px', color: 'var(--spectrum-gray-800, #333)' }}>
        {t('error.networkTitle', locale)}
      </p>
      <p style={{ fontSize: '13px', color: 'var(--spectrum-gray-600, #666)', margin: '0 0 16px', textAlign: 'center', lineHeight: 1.5 }}>
        {t('error.networkMessage', locale)}
      </p>
      <Button onClick={onRetry}>{t('error.retry', locale)}</Button>
    </div>
  );
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// アドオンデータ取得（外部 URL + localStorage キャッシュ）
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

const DATA_URL = 'https://anoguchi0830.github.io/express-helper-jp/addons_data.json';
const CACHE_KEY = 'addons_cache';
const CACHE_TTL = 7 * 24 * 60 * 60 * 1000; // 7日

function getCachedData() {
  try {
    const raw = localStorage.getItem(CACHE_KEY);
    if (!raw) return null;
    const { data, cachedAt } = JSON.parse(raw);
    if (Date.now() - cachedAt > CACHE_TTL) return null;
    return data;
  } catch {
    return null;
  }
}

function setCachedData(data) {
  try {
    localStorage.setItem(CACHE_KEY, JSON.stringify({ data, cachedAt: Date.now() }));
  } catch {
    // localStorage が使えない場合は無視
  }
}

async function fetchAddonsData() {
  const cached = getCachedData();
  if (cached) return cached;

  const res = await fetch(DATA_URL);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  setCachedData(data);
  return data;
}

function AppWrapper() {
  const [ready, setReady] = useState(false);
  const [addonsData, setAddonsData] = useState(null);
  const [error, setError] = useState(false);

  const load = () => {
    setError(false);
    Promise.all([
      addOnUISdk.ready,
      fetchAddonsData()
    ]).then(([_, data]) => {
      setAddonsData(data);
      setReady(true);
    }).catch(() => {
      setError(true);
    });
  };

  useEffect(() => { load(); }, []);

  if (error) return <NetworkErrorScreen onRetry={load} />;
  return ready ? <App addonsData={addonsData} /> : <LoadingScreen />;
}

// エントリーポイント
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <Theme system="express" color="light" scale="medium" style={{ height: '100%', display: 'block' }}>
    <AppWrapper />
  </Theme>
);

export default App;

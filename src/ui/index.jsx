import React, { useState, useEffect, useRef } from 'react';
import ReactDOM from 'react-dom/client';
import addOnUISdk from 'https://new.express.adobe.com/static/add-on-sdk/sdk.js';

import addonsData from './data/addons_data.json';
import LanguageSwitcher from './components/LanguageSwitcher';
import SearchBar from './components/SearchBar';
import AddonCard from './components/AddonCard';
import AddonListItem from './components/AddonListItem';
import CategoryList from './components/CategoryList';
import AddonModal from './components/AddonModal';
import { detectLanguage, t, getLocalizedField, getLocalizedCategory } from './utils/i18n';
import { CATEGORY_ICONS } from './utils/constants';

// addOnId が判明しているアドオンのみ使用（不明なものは除外）
const ADDONS = addonsData.addons.filter(a => a.marketplaceUrl);
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

function searchAddons(query, locale) {
  if (!query.trim()) return [];
  const lowerQuery = query.toLowerCase();

  return ADDONS
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
    <div style={uiStyles.sortBar}>
      <button
        style={{ ...uiStyles.sortBtn, ...(sortId === 'default' ? uiStyles.sortBtnActive : {}) }}
        onClick={() => onSortChange('default')}
      >
        {t('sort.default', locale)}
      </button>
      <button
        style={{ ...uiStyles.sortBtn, ...(nameActive ? uiStyles.sortBtnActive : {}) }}
        onClick={handleNameClick}
      >
        {t('sort.name', locale)}{sortId === 'name' ? ' ↑' : sortId === 'name-desc' ? ' ↓' : ''}
      </button>
    </div>
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
          <button
            key={kw}
            style={uiStyles.suggestTag}
            onClick={() => onSuggestClick(kw)}
          >
            {kw}
          </button>
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

function App() {
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
  const searchResults   = sortAddons(searchAddons(searchQuery, locale), sortId === 'default' ? 'default' : sortId, locale);
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
            <button style={styles.viewAllBtn} onClick={handleViewAll}>
              {t('browse.viewAll', locale, { count: ADDONS.length })} →
            </button>
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
          <button style={styles.backBtn} onClick={handleBackToHome}>← Back</button>
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
          <button style={styles.backBtn} onClick={handleBackToHome}>← Back</button>
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
  sectionTitle: { fontSize: '16px', fontWeight: 'bold', color: '#1E1E1E' },
  count:    { fontSize: '14px', fontWeight: 'normal', color: '#666' },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '10px'
  },
  viewAllWrap: {
    padding: '0 16px 8px',
    textAlign: 'right'
  },
  viewAllBtn: {
    padding: '7px 14px',
    fontSize: '13px',
    border: '1px solid #5258E4',
    backgroundColor: '#FFFFFF',
    color: '#5258E4',
    borderRadius: '20px',
    cursor: 'pointer',
    fontFamily: 'inherit',
    fontWeight: '500',
    transition: 'all 0.15s'
  },
  backBtn: {
    padding: '6px 12px',
    fontSize: '13px',
    border: '1px solid #E0E0E0',
    backgroundColor: '#FFFFFF',
    borderRadius: '6px',
    cursor: 'pointer',
    marginBottom: '12px',
    display: 'block'
  }
};

// サブコンポーネント用スタイル
const uiStyles = {
  list: { display: 'flex', flexDirection: 'column', gap: '12px' },
  sortBar: { display: 'flex', gap: '6px', marginBottom: '12px' },
  sortBtn: {
    padding: '5px 12px',
    fontSize: '12px',
    border: '1px solid #E0E0E0',
    backgroundColor: '#FFFFFF',
    borderRadius: '16px',
    cursor: 'pointer',
    fontFamily: 'inherit',
    color: '#555',
    transition: 'all 0.15s'
  },
  sortBtnActive: {
    backgroundColor: '#5258E4',
    color: '#FFFFFF',
    borderColor: '#5258E4'
  },
  noResults: {
    textAlign: 'center',
    padding: '28px 16px'
  },
  noResultsText: {
    color: '#666',
    lineHeight: '1.6',
    fontSize: '14px',
    marginBottom: '20px'
  },
  suggestLabel: {
    fontSize: '12px',
    color: '#999',
    marginBottom: '10px'
  },
  suggestTags: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '8px',
    justifyContent: 'center'
  },
  suggestTag: {
    padding: '6px 14px',
    backgroundColor: '#EEEAFF',
    color: '#5258E4',
    border: '1px solid #C0BDFA',
    borderRadius: '16px',
    fontSize: '13px',
    cursor: 'pointer',
    fontFamily: 'inherit',
    transition: 'all 0.15s'
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
      <span style={{ fontSize: '13px', color: '#999' }}>Loading...</span>
    </div>
  );
}

function AppWrapper() {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    addOnUISdk.ready.then(() => setReady(true));
  }, []);

  return ready ? <App /> : <LoadingScreen />;
}

// エントリーポイント
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<AppWrapper />);

export default App;

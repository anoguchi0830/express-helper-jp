import React, { useEffect, useState } from 'react';
import { CATEGORY_ICONS } from '../utils/constants';
import { getLocalizedField, getLocalizedCategory, t } from '../utils/i18n';

export default function AddonModal({ addon, locale, onClose, openInExpress }) {
  const [visible, setVisible] = useState(false);

  // マウント直後にアニメーション開始
  useEffect(() => {
    const id = requestAnimationFrame(() => setVisible(true));
    return () => cancelAnimationFrame(id);
  }, []);

  // Escape キーで閉じる
  useEffect(() => {
    const onKey = (e) => { if (e.key === 'Escape') handleClose(); };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, []);

  const handleClose = () => {
    setVisible(false);
    setTimeout(onClose, 180); // アニメーション完了後に unmount
  };

  const name = getLocalizedField(addon, 'name', locale);
  const description = getLocalizedField(addon, 'description', locale);
  const localeSuffix = locale.charAt(0).toUpperCase() + locale.slice(1);
  const keywords = addon[`keywords${localeSuffix}`] || addon.keywordsEn || addon.keywords || [];

  return (
    <div
      style={{ ...styles.overlay, opacity: visible ? 1 : 0 }}
      onClick={handleClose}
    >
      <div
        style={{
          ...styles.modal,
          transform: visible ? 'translateY(0)' : 'translateY(24px)',
          opacity: visible ? 1 : 0
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* 閉じるボタン */}
        <button style={styles.closeBtn} onClick={handleClose}>
          {t('actions.close', locale)}
        </button>

        {/* ヘッダー */}
        <div style={styles.header}>
          <span style={styles.icon}>{CATEGORY_ICONS[addon.category] || '📦'}</span>
          <h2 style={styles.title}>{name}</h2>
          <p style={styles.category}>
            {t('addon.category', locale)}: {getLocalizedCategory(addon.category, locale)}
          </p>
        </div>

        {/* ボディ */}
        <div style={styles.body}>
          <h3 style={styles.bodyTitle}>📝 {t('addon.description', locale)}</h3>
          <p style={styles.description}>{description}</p>

          {keywords.length > 0 && (
            <>
              <h3 style={styles.bodyTitle}>🔖 {t('addon.keywords', locale)}</h3>
              <div style={styles.tags}>
                {keywords.map((kw, i) => (
                  <span key={i} style={styles.tag}>#{kw}</span>
                ))}
              </div>
            </>
          )}
        </div>

        {/* フッター */}
        <div style={styles.footer}>
          <button
            style={styles.marketplaceBtn}
            onClick={() => openInExpress(addon)}
          >
            {t('addon.openInExpress', locale)}
          </button>
        </div>
      </div>
    </div>
  );
}

const styles = {
  overlay: {
    position: 'fixed',
    inset: 0,
    backgroundColor: 'rgba(0,0,0,0.5)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
    padding: '16px',
    transition: 'opacity 0.18s ease'
  },
  modal: {
    backgroundColor: '#FFFFFF',
    borderRadius: '14px',
    maxWidth: '480px',
    width: '100%',
    maxHeight: '85vh',
    overflow: 'auto',
    position: 'relative',
    transition: 'transform 0.22s ease, opacity 0.18s ease',
    boxShadow: '0 20px 60px rgba(0,0,0,0.2)'
  },
  closeBtn: {
    position: 'absolute',
    top: '12px',
    right: '12px',
    padding: '6px 10px',
    border: 'none',
    backgroundColor: '#F5F7FA',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '12px',
    fontFamily: 'inherit',
    zIndex: 1,
    transition: 'background-color 0.15s'
  },
  header: {
    padding: '20px 20px 14px',
    borderBottom: '1px solid #E0E0E0'
  },
  icon: {
    display: 'block',
    fontSize: '36px',
    marginBottom: '8px'
  },
  title: {
    fontSize: '18px',
    fontWeight: 'bold',
    marginBottom: '6px',
    paddingRight: '60px'
  },
  category: {
    fontSize: '13px',
    color: '#666'
  },
  body: {
    padding: '16px 20px'
  },
  bodyTitle: {
    fontSize: '14px',
    fontWeight: 'bold',
    marginBottom: '6px',
    marginTop: '14px',
    color: '#333'
  },
  description: {
    fontSize: '13px',
    color: '#555',
    lineHeight: '1.6'
  },
  tags: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '6px',
    marginTop: '6px'
  },
  tag: {
    padding: '4px 10px',
    backgroundColor: '#EEEAFF',
    borderRadius: '14px',
    fontSize: '11px',
    color: '#5258E4'
  },
  footer: {
    padding: '14px 20px',
    borderTop: '1px solid #E0E0E0'
  },
  marketplaceBtn: {
    width: '100%',
    padding: '11px',
    fontSize: '14px',
    border: 'none',
    backgroundColor: '#5258E4',
    color: '#FFFFFF',
    borderRadius: '8px',
    cursor: 'pointer',
    fontFamily: 'inherit',
    fontWeight: 'bold'
  }
};

import React from 'react';
import { CATEGORY_ICONS } from '../utils/constants';
import { getLocalizedField, getLocalizedCategory, t } from '../utils/i18n';

export default function AddonListItem({ addon, locale, onClick, openInExpress }) {
  const name = getLocalizedField(addon, 'name', locale);
  const description = getLocalizedField(addon, 'description', locale);

  return (
    <div style={styles.item}>
      <div style={styles.header}>
        <h3 style={styles.title}>{name}</h3>
      </div>

      <p style={styles.description}>{description}</p>

      <div style={styles.footer}>
        <span>
          {CATEGORY_ICONS[addon.category] || '📦'} {getLocalizedCategory(addon.category, locale)}
        </span>
      </div>

      <div style={styles.actions}>
        <button style={styles.detailBtn} onClick={onClick}>
          {t('addon.viewDetails', locale)}
        </button>
        <button
          style={styles.marketplaceBtn}
          onClick={() => openInExpress(addon)}
        >
          {t('addon.openInExpress', locale)}
        </button>
      </div>
    </div>
  );
}

const styles = {
  item: {
    backgroundColor: '#FFFFFF',
    border: '1px solid #E0E0E0',
    borderRadius: '10px',
    padding: '14px'
  },
  header: {
    marginBottom: '6px'
  },
  title: {
    fontSize: '15px',
    fontWeight: 'bold',
    margin: 0
  },
  description: {
    fontSize: '13px',
    color: '#555',
    marginBottom: '10px',
    lineHeight: '1.5'
  },
  footer: {
    display: 'flex',
    gap: '12px',
    fontSize: '11px',
    color: '#777',
    marginBottom: '10px'
  },
  actions: {
    display: 'flex',
    gap: '8px'
  },
  detailBtn: {
    padding: '7px 14px',
    fontSize: '13px',
    border: '1px solid #5258E4',
    backgroundColor: '#FFFFFF',
    color: '#5258E4',
    borderRadius: '6px',
    cursor: 'pointer',
    fontFamily: 'inherit',
    fontWeight: '500'
  },
  marketplaceBtn: {
    padding: '7px 14px',
    fontSize: '13px',
    border: 'none',
    backgroundColor: '#5258E4',
    color: '#FFFFFF',
    borderRadius: '6px',
    cursor: 'pointer',
    fontFamily: 'inherit',
    fontWeight: '500',
    flex: 1
  }
};

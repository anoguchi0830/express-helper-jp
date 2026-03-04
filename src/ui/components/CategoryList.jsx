import React, { useState } from 'react';
import { CATEGORY_ICONS } from '../utils/constants';
import { getLocalizedCategory, t } from '../utils/i18n';

function CategoryItem({ cat, locale, onClick }) {
  const [hovered, setHovered] = useState(false);

  return (
    <div
      style={{
        ...styles.item,
        ...(hovered ? styles.itemHover : {})
      }}
      onClick={() => onClick(cat.id)}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <span style={styles.icon}>{CATEGORY_ICONS[cat.id] || '📦'}</span>
      <span style={styles.name}>{getLocalizedCategory(cat.id, locale)}</span>
      <span style={styles.count}>({cat.count})</span>
      <span style={{ ...styles.arrow, ...(hovered ? styles.arrowHover : {}) }}>›</span>
    </div>
  );
}

export default function CategoryList({ categories, locale, onCategoryClick }) {
  return (
    <section style={styles.section}>
      <h2 style={styles.sectionTitle}>📁 {t('sections.categories', locale)}</h2>
      <div style={styles.list}>
        {categories.map(cat => (
          <CategoryItem
            key={cat.id}
            cat={cat}
            locale={locale}
            onClick={onCategoryClick}
          />
        ))}
      </div>
    </section>
  );
}

const styles = {
  section: {
    padding: '0 16px 16px'
  },
  sectionTitle: {
    fontSize: '16px',
    fontWeight: 'bold',
    marginBottom: '12px',
    color: '#1E1E1E'
  },
  list: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px'
  },
  item: {
    padding: '10px 12px',
    backgroundColor: '#F5F7FA',
    borderRadius: '8px',
    display: 'flex',
    alignItems: 'center',
    cursor: 'pointer',
    transition: 'background-color 0.15s, box-shadow 0.15s',
    border: '1px solid transparent'
  },
  itemHover: {
    backgroundColor: '#EEEAFF',
    border: '1px solid #C0BDFA'
  },
  icon: {
    fontSize: '18px',
    marginRight: '10px'
  },
  name: {
    fontSize: '13px',
    flex: 1,
    fontWeight: '500'
  },
  count: {
    fontSize: '11px',
    color: '#999',
    marginRight: '6px'
  },
  arrow: {
    fontSize: '16px',
    color: '#CCC',
    transition: 'color 0.15s, transform 0.15s',
    display: 'inline-block'
  },
  arrowHover: {
    color: '#5258E4',
    transform: 'translateX(2px)'
  }
};

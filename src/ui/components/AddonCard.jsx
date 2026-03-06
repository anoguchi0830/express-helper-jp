import React, { useState } from 'react';
import { CATEGORY_ICONS } from '../utils/constants';
import { getLocalizedField, getLocalizedCategory } from '../utils/i18n';

export default function AddonCard({ addon, locale, onClick }) {
  const [hovered, setHovered] = useState(false);
  const name = getLocalizedField(addon, 'name', locale);
  const icon = CATEGORY_ICONS[addon.category] || '📦';

  return (
    <div
      style={{
        ...styles.card,
        ...(hovered ? styles.cardHover : {})
      }}
      onClick={onClick}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <div style={styles.icon}>{icon}</div>
      <h3 style={styles.title}>{name}</h3>
      <p style={styles.category}>{getLocalizedCategory(addon.category, locale)}</p>
    </div>
  );
}

const styles = {
  card: {
    backgroundColor: 'var(--spectrum-gray-50, #FFFFFF)',
    borderWidth: '1px',
    borderStyle: 'solid',
    borderColor: 'var(--spectrum-gray-300, #E0E0E0)',
    borderRadius: '10px',
    padding: '14px',
    textAlign: 'center',
    cursor: 'pointer',
    outline: 'none',
    transition: 'box-shadow 0.18s ease, transform 0.18s ease, border-color 0.18s ease'
  },
  cardHover: {
    boxShadow: '0 4px 14px rgba(82, 88, 228, 0.12)',
    transform: 'translateY(-2px)',
    borderColor: 'var(--spectrum-accent-color-400, #C0BDFA)'
  },
  icon: {
    fontSize: '28px',
    marginBottom: '6px'
  },
  title: {
    fontSize: '13px',
    fontWeight: 'bold',
    margin: '4px 0',
    color: 'var(--spectrum-gray-900, #1E1E1E)',
    lineHeight: '1.3'
  },
  category: {
    fontSize: '11px',
    color: 'var(--spectrum-gray-700, #666)',
    margin: '2px 0'
  }
};

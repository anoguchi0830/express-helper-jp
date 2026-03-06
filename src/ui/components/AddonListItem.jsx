import React from 'react';
import { Button } from '@swc-react/button';
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
        <Button variant="secondary" treatment="outline" onClick={onClick}>
          {t('addon.viewDetails', locale)}
        </Button>
        <Button variant="accent" onClick={() => openInExpress(addon)}>
          {t('addon.openInExpress', locale)}
        </Button>
      </div>
    </div>
  );
}

const styles = {
  item: {
    backgroundColor: 'var(--spectrum-gray-50, #FFFFFF)',
    border: '1px solid var(--spectrum-gray-300, #E0E0E0)',
    borderRadius: '10px',
    padding: '14px'
  },
  header: {
    marginBottom: '6px'
  },
  title: {
    fontSize: '15px',
    fontWeight: 'bold',
    margin: 0,
    color: 'var(--spectrum-gray-900, #1E1E1E)'
  },
  description: {
    fontSize: '13px',
    color: 'var(--spectrum-gray-700, #555)',
    marginBottom: '10px',
    lineHeight: '1.5'
  },
  footer: {
    display: 'flex',
    gap: '12px',
    fontSize: '11px',
    color: 'var(--spectrum-gray-600, #777)',
    marginBottom: '10px'
  },
  actions: {
    display: 'flex',
    gap: '8px'
  }
};

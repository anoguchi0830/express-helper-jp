import React from 'react';
import { ActionGroup } from '@swc-react/action-group';
import { ActionButton } from '@swc-react/action-button';

const languages = [
  { code: 'en', label: 'EN', flag: '🇺🇸' },
  { code: 'ja', label: '日本語', flag: '🇯🇵' },
  { code: 'ko', label: '한국어', flag: '🇰🇷' }
];

export default function LanguageSwitcher({ currentLocale, onLocaleChange }) {
  return (
    <div style={styles.wrap}>
      <ActionGroup>
        {languages.map(lang => (
          <ActionButton
            key={lang.code}
            emphasized
            selected={currentLocale === lang.code}
            onClick={() => onLocaleChange(lang.code)}
          >
            {lang.flag} {lang.label}
          </ActionButton>
        ))}
      </ActionGroup>
    </div>
  );
}

const styles = {
  wrap: {
    padding: '10px 16px',
    backgroundColor: 'var(--spectrum-gray-100, #F5F7FA)',
    borderBottom: '1px solid var(--spectrum-gray-300, #E0E0E0)'
  }
};

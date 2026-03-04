import React from 'react';

const languages = [
  { code: 'en', label: 'EN', flag: '🇺🇸' },
  { code: 'ja', label: '日本語', flag: '🇯🇵' },
  { code: 'ko', label: '한국어', flag: '🇰🇷' }
];

export default function LanguageSwitcher({ currentLocale, onLocaleChange }) {
  return (
    <div style={styles.switcher}>
      {languages.map(lang => (
        <button
          key={lang.code}
          style={{
            ...styles.btn,
            ...(currentLocale === lang.code ? styles.btnActive : {})
          }}
          onClick={() => onLocaleChange(lang.code)}
        >
          <span style={styles.flag}>{lang.flag}</span>
          <span style={styles.label}>{lang.label}</span>
        </button>
      ))}
    </div>
  );
}

const styles = {
  switcher: {
    display: 'flex',
    gap: '6px',
    padding: '10px 16px',
    background: '#F5F7FA',
    borderBottom: '1px solid #E0E0E0'
  },
  btn: {
    display: 'flex',
    alignItems: 'center',
    gap: '4px',
    padding: '5px 10px',
    border: '1px solid #E0E0E0',
    background: '#FFFFFF',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '12px',
    fontFamily: '"Noto Sans JP", sans-serif',
    transition: 'all 0.15s'
  },
  btnActive: {
    background: '#5258E4',
    color: '#FFFFFF',
    borderColor: '#5258E4'
  },
  flag: {
    fontSize: '14px',
    lineHeight: 1
  },
  label: {
    fontWeight: '500'
  }
};

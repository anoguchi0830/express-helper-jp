import en from '../locales/en.json';
import ja from '../locales/ja.json';
import ko from '../locales/ko.json';

const translations = { en, ja, ko };
const SUPPORTED_LOCALES = ['en', 'ja', 'ko'];

// ブラウザ言語を検出し、LocalStorageの設定を優先する
export const detectLanguage = () => {
  const saved = localStorage.getItem('preferredLocale');
  if (saved && SUPPORTED_LOCALES.includes(saved)) return saved;

  const browserLang = navigator.language.split('-')[0];
  return SUPPORTED_LOCALES.includes(browserLang) ? browserLang : 'en';
};

// 翻訳関数: "search.placeholder" 形式のキーを解決し、{{param}} を置換する
export const t = (key, locale, params = {}) => {
  const keys = key.split('.');
  let value = translations[locale];

  for (const k of keys) {
    value = value?.[k];
  }

  if (!value) return key;

  return Object.keys(params).reduce((str, param) => {
    return str.replace(new RegExp(`\\{\\{${param}\\}\\}`, 'g'), params[param]);
  }, value);
};

// Add-onデータの多言語フィールドを取得する
// 例: getLocalizedField(addon, 'description', 'ja') → addon.descriptionJa
export const getLocalizedField = (addon, field, locale) => {
  const suffix = locale.charAt(0).toUpperCase() + locale.slice(1); // 'ja' → 'Ja'
  return addon[`${field}${suffix}`] || addon[`${field}En`] || addon[field];
};

// カテゴリのローカライズ名を取得する
export const getLocalizedCategory = (categoryId, locale) => {
  return t(`categories.${categoryId}`, locale) || categoryId;
};

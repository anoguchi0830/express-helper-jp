const MARKETPLACE_BASE = 'https://new.express.adobe.com/add-ons';

/**
 * アドオンのMarketplace URLを返す。
 * - addon.marketplaceUrl が設定されていればそれを使用
 * - 未設定の場合はマーケットプレイスの検索URLをフォールバックとして生成
 *   例: https://new.express.adobe.com/add-ons?search=Dropbox
 */
export function getMarketplaceUrl(addon) {
  if (addon.marketplaceUrl) return addon.marketplaceUrl;
  const query = encodeURIComponent(addon.nameEn || addon.nameJa || addon.id);
  return `${MARKETPLACE_BASE}?search=${query}`;
}

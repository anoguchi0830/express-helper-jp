export default {
  async fetch(request, env) {
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    // CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    if (request.method !== 'POST') {
      return new Response('Method Not Allowed', { status: 405 });
    }

    try {
      const text = await request.text();

      // text/plain で送られてくるキーワードをそのまま使う
      // JSON フォールバック対応
      let keyword;
      try {
        keyword = JSON.parse(text).keyword;
      } catch {
        keyword = text;
      }

      // バリデーション: 2文字以上、100文字以下のみ受け付ける
      if (!keyword || typeof keyword !== 'string' ||
          keyword.length < 2 || keyword.length > 100) {
        return new Response('Bad Request', { status: 400, headers: corsHeaders });
      }

      const key = keyword.toLowerCase().trim();

      // KV の現在のカウントを取得して +1
      const current = await env.SEARCH_STATS.get(key);
      const count = (parseInt(current) || 0) + 1;
      await env.SEARCH_STATS.put(key, String(count));

      return new Response('OK', { status: 200, headers: corsHeaders });
    } catch {
      return new Response('Bad Request', { status: 400, headers: corsHeaders });
    }
  }
};

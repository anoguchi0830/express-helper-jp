---
name: xpost
description: Generating X (Twitter) thread posts for newly added Adobe Express addons. Use when today's additions to docs/addons_data.json need to be shared on social media.
---

# /xpost — Addon Update X Post Generator

This skill extracts newly added addon entries from `docs/addons_data.json` for the current date and generates a thread for X (Twitter).

## Workflow

### 1. Extract Today's Additions
Run the bundled script to get the list of addons added today:
```bash
node scripts/extract_today_addons.cjs
```

### 2. Generate Thread Posts
Based on the extracted list, generate a series of posts following these rules:

#### Structure (for > 5 addons)
- **Hook (No number)**: Total count, category trends, and "🧵👇". No page number.
- **1/M to (M-1)/M (Intermediate)**: **Group entries by category**.
  - Each post should ideally focus on one or two related categories (e.g., all "AI画像加工系" together).
  - Max **3 entries per post**. If a category has more than 3, split it into the next post.
  - Format: Emoji + 【Category】 + Name + One-sentence description.
  - **Character Limit**: X (Twitter) counts Japanese characters as 2. Limit each post to approx **140 Japanese characters** (280 total counts).
- **M/M (Final)**: Summary, CTA (URL: `https://t.co/zvAFTsZRGI`), hashtags, and disclaimer.

#### Rules for Small Updates (<= 5 addons)
- Use a single post instead of a thread. Include the Hook elements, the list, CTA, and Hashtags/Disclaimer.

#### Description Handling
- If `descriptionJa` is missing or empty, summarize `description` (English) into a concise one-sentence Japanese description.

#### Mandatory Content for Final Post
**CTA URL**: `https://t.co/zvAFTsZRGI`

**Hashtags**:
`#AdobeExpress #アドオン #AIツール #デザイン`

**Disclaimer**:
```
※ 紹介内容はマーケットプレイスの説明文をもとに作成したものです。各アドオンの開発者・公式とは無関係です。実際の動作は各アドオンでご確認ください。
```

## Output Format
Display each post clearly separated (e.g., using code blocks or horizontal rules). Ensure character limits are strictly observed.

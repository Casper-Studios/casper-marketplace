#!/usr/bin/env node
/**
 * DM action items to each person on Slack using Block Kit.
 * Usage: node slack-post.mjs <path-to-action-items.md>
 * Requires env var: SLACK_BOT_TOKEN (with chat:write, im:write scopes)
 * Requires: .claude/slack-users.local.json in the project root (name → Slack user ID mapping)
 */
import { readFileSync } from "fs";
import { execSync } from "child_process";

// --- Args & config ---
const file = process.argv[2];
if (!file) {
  console.error("Usage: node slack-post.mjs <path-to-action-items.md>");
  process.exit(1);
}

const TOKEN = process.env.SLACK_BOT_TOKEN;
if (!TOKEN) {
  console.error("Missing SLACK_BOT_TOKEN env var");
  process.exit(1);
}

// Load slack user mapping from the project's .claude directory
const usersPath = `${process.cwd()}/.claude/slack-users.local.json`;
let userMap;
try {
  const raw = readFileSync(usersPath, "utf-8");
  const stripped = raw.replace(/^\s*\/\/.*$/gm, "");
  userMap = JSON.parse(stripped);
} catch (e) {
  console.error(`Missing or invalid ${usersPath}`);
  console.error("Generate it with: node [SKILL_DIR]/scripts/fetch-slack-users.mjs");
  process.exit(1);
}

const md = readFileSync(file, "utf-8");

// --- Extract header metadata ---
const titleMatch = md.match(/^# (.+)/m);
const dateMatch = md.match(/\*\*Date:\*\* (.+)/);
const linkMatch = md.match(/\*\*Fireflies Link:\*\* (.+)/);
const title = titleMatch?.[1]?.replace(/^Action Items\s*—\s*/, "") ?? "Meeting";
const date = dateMatch?.[1] ?? "";
const link = linkMatch?.[1] ?? "";

// --- Detect mode: all-attendees (## Person sections) vs single-person ---
const personSectionRegex = /^## ([^\n]+)/gm;
const personMatches = [...md.matchAll(personSectionRegex)];

// In all-attendees mode, person names are ## headers with ### category sub-headers
// In single-person mode, the title is "# [Name] Action Items — ..." and ## are categories
const isSinglePerson =
  personMatches.length > 0 &&
  personMatches.every((m) => {
    const name = m[1].trim();
    return /^(High Priority|Pairing|Content|Questions|Exploration|Catch-up|Quick Reference)/.test(
      name
    );
  });

/**
 * Parse a single person's section into categorized items.
 */
function parseCategoryBlocks(sectionMd) {
  const categories = [];
  const catRegex = /^#{2,3} ([^\n]+)/gm;
  const catMatches = [...sectionMd.matchAll(catRegex)];

  for (let i = 0; i < catMatches.length; i++) {
    const catName = catMatches[i][1].trim();
    if (catName === "Quick Reference — Time-Sensitive") continue;
    const start = catMatches[i].index + catMatches[i][0].length;
    const end = i + 1 < catMatches.length ? catMatches[i + 1].index : sectionMd.length;
    const body = sectionMd.slice(start, end).trim();

    const items = parseItems(body);
    if (items.length > 0) {
      categories.push({ category: catName, items });
    }
  }
  return categories;
}

/**
 * Parse action items from a category body.
 */
function parseItems(body) {
  const items = [];
  const lines = body.split("\n");
  let current = null;

  for (const line of lines) {
    const itemMatch = line.match(/^- \[ \] \*\*(.+?)\*\*(.*)/);
    const numberedMatch = line.match(/^\d+\.\s+\*?\*?(.+?)\*?\*?\s*[—–-]\s*(.+)/);

    if (itemMatch) {
      if (current) items.push(current);
      const trailing = itemMatch[2]?.replace(/^\s*[—–-]\s*/, "").trim();
      current = { title: itemMatch[1], details: trailing ? [trailing] : [], quote: null };
    } else if (numberedMatch && !current) {
      if (current) items.push(current);
      current = { title: line.trim(), details: [], quote: null };
    } else if (current) {
      const quoteMatch = line.match(/^\s+- > "(.+)"/) || line.match(/^\s+- > (.+)/);
      const detailMatch = line.match(/^\s+- (.+)/);
      if (quoteMatch) {
        current.quote = quoteMatch[1];
      } else if (detailMatch) {
        current.details.push(detailMatch[1]);
      }
    }
  }
  if (current) items.push(current);
  return items;
}

/**
 * Extract the Quick Reference section if present.
 */
function parseQuickReference(sectionMd) {
  const match = sectionMd.match(
    /#{2,3} Quick Reference — Time-Sensitive\n([\s\S]*?)(?=\n#{2,3} |\n*$)/
  );
  if (!match) return null;
  return match[1].trim();
}

/**
 * Convert markdown links [text](url) to Slack mrkdwn <url|text>.
 */
function mdLinksToSlack(text) {
  return text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, "<$2|$1>");
}

/**
 * Parse a text string (possibly containing markdown links) into rich_text elements.
 */
function textToRichElements(text, style) {
  const elements = [];
  const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
  let lastIndex = 0;
  let match;

  while ((match = linkRegex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      const el = { type: "text", text: text.slice(lastIndex, match.index) };
      if (style) el.style = style;
      elements.push(el);
    }
    const linkEl = { type: "link", url: match[2], text: match[1] };
    if (style) linkEl.style = style;
    elements.push(linkEl);
    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < text.length) {
    const el = { type: "text", text: text.slice(lastIndex) };
    if (style) el.style = style;
    elements.push(el);
  }

  return elements.length > 0 ? elements : [{ type: "text", text, ...(style ? { style } : {}) }];
}

/**
 * Build Block Kit blocks for one person's action items using rich_text for copy-paste fidelity.
 */
function buildBlocks(personName, categories, quickRef) {
  const blocks = [];

  blocks.push({
    type: "header",
    text: { type: "plain_text", text: `Action Items — ${title}`, emoji: true },
  });

  // Metadata line
  const metaElements = [];
  if (date) metaElements.push({ type: "text", text: `Date: ${date}`, style: { bold: true } });
  if (date && link) metaElements.push({ type: "text", text: "  |  " });
  if (link) metaElements.push({ type: "link", url: link, text: "View in Fireflies" });
  if (metaElements.length > 0) {
    blocks.push({
      type: "rich_text",
      elements: [{ type: "rich_text_section", elements: metaElements }],
    });
  }

  for (const { category, items } of categories) {
    // Category header + bullet list in one rich_text block
    const rtElements = [];

    // Category name as bold text section
    rtElements.push({
      type: "rich_text_section",
      elements: [{ type: "text", text: category, style: { bold: true } }],
    });

    // Items as a bullet list
    const listItems = [];
    for (const item of items) {
      const itemElements = [];
      itemElements.push({ type: "text", text: item.title });
      if (item.details.length > 0) {
        itemElements.push({ type: "text", text: " — " });
        itemElements.push(...textToRichElements(item.details.join("; ")));
      }
      listItems.push({ type: "rich_text_section", elements: itemElements });
    }

    rtElements.push({
      type: "rich_text_list",
      style: "bullet",
      elements: listItems,
    });

    blocks.push({ type: "rich_text", elements: rtElements });
  }

  if (quickRef) {
    const qrElements = [
      {
        type: "rich_text_section",
        elements: [
          { type: "text", text: "Quick Reference — Time-Sensitive\n", style: { bold: true } },
          { type: "text", text: quickRef },
        ],
      },
    ];
    blocks.push({ type: "rich_text", elements: qrElements });
  }

  return blocks;
}

/**
 * Build a plain-text fallback for the `text` field.
 */
function buildFallback(personName, categories) {
  let text = `Action Items — ${title}\n`;
  for (const { category, items } of categories) {
    text += `\n${category}\n`;
    for (const item of items) {
      text += `• ${item.title}\n`;
    }
  }
  return text;
}

/**
 * Call Slack API via curl.
 */
function slackApi(method, body) {
  const payload = JSON.stringify(body);
  const resp = execSync(
    `curl -s -X POST https://slack.com/api/${method} -H "Authorization: Bearer ${TOKEN}" -H "Content-Type: application/json; charset=utf-8" -d @-`,
    { input: payload, encoding: "utf-8" }
  );
  return JSON.parse(resp);
}

/**
 * Open a DM channel with a user and return the channel ID.
 */
function openDm(userId) {
  const result = slackApi("conversations.open", { users: userId });
  if (!result.ok) {
    throw new Error(`conversations.open failed for ${userId}: ${result.error}`);
  }
  return result.channel.id;
}

/**
 * Post blocks to a channel, splitting into multiple messages if >50 blocks.
 */
function postBlocks(channelId, blocks, fallbackText) {
  const MAX_BLOCKS = 50;
  const chunks = [];

  for (let i = 0; i < blocks.length; i += MAX_BLOCKS) {
    chunks.push(blocks.slice(i, i + MAX_BLOCKS));
  }

  for (let i = 0; i < chunks.length; i++) {
    const result = slackApi("chat.postMessage", {
      channel: channelId,
      text: fallbackText,
      blocks: chunks[i],
      unfurl_links: false,
    });
    if (result.ok) {
      console.log(`  Message ${i + 1}/${chunks.length}: posted (ts=${result.ts})`);
    } else {
      console.error(`  Message ${i + 1}/${chunks.length}: FAILED - ${result.error}`);
    }
  }
}

/**
 * Resolve person name to Slack user ID (exact match, then fuzzy first-name match).
 */
function resolveUserId(name) {
  if (userMap[name]) return { id: userMap[name], matchedName: name };

  const lowerName = name.toLowerCase();
  for (const [fullName, id] of Object.entries(userMap)) {
    const firstName = fullName.split(" ")[0].toLowerCase();
    if (firstName === lowerName) return { id, matchedName: fullName };
  }

  return null;
}

// --- Main ---
const warnings = [];

if (isSinglePerson) {
  const nameMatch = md.match(/^# (.+?) Action Items/m);
  const personName = nameMatch?.[1] ?? "Unknown";

  const resolved = resolveUserId(personName);
  if (!resolved) {
    console.error(
      `Could not resolve Slack user for "${personName}". Check .claude/slack-users.local.json.`
    );
    process.exit(1);
  }

  const categories = parseCategoryBlocks(md);
  const quickRef = parseQuickReference(md);
  const blocks = buildBlocks(personName, categories, quickRef);
  const fallback = buildFallback(personName, categories);

  console.log(`Sending DM to ${personName} (${resolved.matchedName} → ${resolved.id})`);
  const dmChannel = openDm(resolved.id);
  postBlocks(dmChannel, blocks, fallback);
} else {
  const sections = md.split(/^(?=## [^\n]+$)/m).filter((s) => s.startsWith("## "));

  for (const section of sections) {
    const headerMatch = section.match(/^## ([^\n]+)/);
    if (!headerMatch) continue;
    const personName = headerMatch[1].trim();

    if (personName === "Quick Reference — Time-Sensitive") continue;

    const resolved = resolveUserId(personName);
    if (!resolved) {
      warnings.push(personName);
      console.warn(`  ⚠ Skipping "${personName}" — not found in .claude/slack-users.local.json`);
      continue;
    }

    const categories = parseCategoryBlocks(section);
    if (categories.length === 0) {
      console.log(`  Skipping ${personName} — no action items`);
      continue;
    }

    const personQuickRef = parseQuickReference(section);
    const blocks = buildBlocks(personName, categories, personQuickRef);
    const fallback = buildFallback(personName, categories);

    console.log(`Sending DM to ${personName} (${resolved.matchedName} → ${resolved.id})`);
    const dmChannel = openDm(resolved.id);
    postBlocks(dmChannel, blocks, fallback);
  }
}

if (warnings.length > 0) {
  console.warn(`\n⚠ Could not resolve ${warnings.length} name(s): ${warnings.join(", ")}`);
  console.warn(
    "Add them to .claude/slack-users.local.json or run: node [SKILL_DIR]/scripts/fetch-slack-users.mjs"
  );
}

console.log("Done.");

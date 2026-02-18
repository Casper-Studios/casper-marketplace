#!/usr/bin/env node
/**
 * Post action items markdown to Slack as mrkdwn.
 * Usage: node slack-post.mjs <path-to-action-items.md>
 * Requires env vars: SLACK_BOT_TOKEN, SLACK_CHANNEL_ID
 */
import { readFileSync } from "fs";
import { execSync } from "child_process";

const file = process.argv[2];
if (!file) {
  console.error("Usage: node slack-post.mjs <path-to-action-items.md>");
  process.exit(1);
}

const TOKEN = process.env.SLACK_BOT_TOKEN;
const CHANNEL = process.env.SLACK_CHANNEL_ID;
if (!TOKEN || !CHANNEL) {
  console.error("Missing SLACK_BOT_TOKEN or SLACK_CHANNEL_ID");
  process.exit(1);
}

const md = readFileSync(file, "utf-8");

// --- Extract header metadata ---
const dateMatch = md.match(/\*\*Date:\*\* (.+)/);
const linkMatch = md.match(/\*\*Fireflies Link:\*\* (.+)/);
const titleMatch = md.match(/^# (.+)/m);
const date = dateMatch?.[1] ?? "";
const link = linkMatch?.[1] ?? "";
const title = titleMatch?.[1] ?? "Action Items";
const header = `*${title}* | <${link}|Fireflies> | ${date}`;

// --- Strip header block, keep body from first ## onward ---
const bodyStart = md.indexOf("\n## ");
const body = bodyStart >= 0 ? md.slice(bodyStart) : md;

// --- Markdown -> Slack mrkdwn line-by-line ---
function convertLine(line) {
  if (line.trim() === "---") return "";
  if (line.startsWith("## ")) return `\n*${line.slice(3).trim()}*`;
  if (line.startsWith("### ")) return `_${line.slice(4).trim()}_`;
  if (line.startsWith("# ")) return `*${line.slice(2).trim()}*`;

  line = line.replace(/^- \[ \] \*\*(.+?)\*\*/, "• *$1*");
  line = line.replace(/^(\d+)\. \*\*(.+?)\*\*/, "$1. *$2*");
  line = line.replace(/\*\*(.+?)\*\*/g, "*$1*");
  line = line.replace(/^(\s+)- > "(.+)"/, '$1> _"$2"_');
  line = line.replace(/^(\s+)- > (.+)/, "$1> _$2_");
  line = line.replace(/^  - (.+)/, "   $1");
  line = line.replace(/\[(.+?)\]\((.+?)\)/g, "<$2|$1>");
  return line;
}

const converted = body
  .split("\n")
  .map(convertLine)
  .join("\n")
  .replace(/\n{3,}/g, "\n\n")
  .trim();

const fullText = `${header}\n\n${converted}`;

// --- Chunk by person sections, max 3900 chars ---
const sections = fullText.split(/\n\n(?=\n?\*[A-Z])/);
const MAX = 3900;
const chunks = [];
let current = "";
for (const section of sections) {
  if (current.length + section.length + 2 > MAX && current.length > 0) {
    chunks.push(current.trim());
    current = section;
  } else {
    current = current ? current + "\n\n" + section : section;
  }
}
if (current) chunks.push(current.trim());

// --- Post each chunk ---
console.log(`Posting ${chunks.length} message(s) (${fullText.length} chars total)`);
for (let i = 0; i < chunks.length; i++) {
  const payload = JSON.stringify({
    channel: CHANNEL,
    text: chunks[i],
    unfurl_links: false,
    mrkdwn: true,
  });
  try {
    const resp = execSync(
      `curl -s -X POST https://slack.com/api/chat.postMessage -H "Authorization: Bearer ${TOKEN}" -H "Content-Type: application/json; charset=utf-8" -d @-`,
      { input: payload, encoding: "utf-8" }
    );
    const result = JSON.parse(resp);
    if (result.ok) {
      console.log(`  Message ${i + 1}/${chunks.length}: posted (ts=${result.ts})`);
    } else {
      console.log(`  Message ${i + 1}/${chunks.length}: FAILED - ${result.error}`);
    }
  } catch (e) {
    console.error(`  Message ${i + 1}/${chunks.length}: ERROR - ${e.message}`);
  }
}

#!/usr/bin/env node
/**
 * Fetch all non-bot Slack workspace members and print a name → user ID mapping.
 * Usage: node fetch-slack-users.mjs
 * Requires env var: SLACK_BOT_TOKEN (with users:read scope)
 *
 * Pipe output to update slack-users.json:
 *   node scripts/fetch-slack-users.mjs > slack-users.json
 */
import { execSync } from "child_process";

const TOKEN = process.env.SLACK_BOT_TOKEN;
if (!TOKEN) {
  console.error("Missing SLACK_BOT_TOKEN env var");
  process.exit(1);
}

const resp = execSync(
  `curl -s -H "Authorization: Bearer ${TOKEN}" https://slack.com/api/users.list`,
  { encoding: "utf-8" }
);

const data = JSON.parse(resp);
if (!data.ok) {
  console.error("Slack API error:", data.error);
  process.exit(1);
}

const map = {};
data.members
  .filter((m) => !m.is_bot && !m.deleted && m.id !== "USLACKBOT")
  .forEach((m) => {
    const name = m.profile.real_name || m.real_name;
    if (name) map[name] = m.id;
  });

console.log(JSON.stringify(map, null, 2));

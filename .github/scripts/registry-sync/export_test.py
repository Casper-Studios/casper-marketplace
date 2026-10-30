import json
import tempfile
import unittest
from pathlib import Path

import export
from export import RegistryRow, ambiguous_names, build_rows, check_json, payload, send, to_json, write_json

SECRET = "Casper-Studios/casper-secret-sauce"


class RepoTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.write(".claude-plugin/marketplace.json", json.dumps({"name": "casper-secret-sauce", "plugins": []}))
        self.write("plugins/ops/float/.claude-plugin/plugin.json", json.dumps({"name": "float", "version": "1.2.0"}))
        self.write("plugins/ops/float/skills/log-my-time/SKILL.md", "---\nname: log-my-time\ndescription: Log it.\n---\n")
        self.write("plugins/ops/float/skills/broken/SKILL.md", "no frontmatter\n")
        self.write("plugins/project-management/brain/commands/init-brain.md", "# init")

    def write(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    def test_rows_cover_skills_commands_and_client_list(self):
        self.write("telemetry/client-plugins.json", json.dumps(["sphera-cow"]))
        rows, skipped = build_rows(self.root, SECRET, "abc123")
        self.assertEqual(skipped, [])
        self.assertEqual(
            [(r.plugin, r.skill, r.kind, r.origin, r.plugin_version, r.frontmatter_ok) for r in rows],
            [
                ("brain", "init-brain", "command", "casper", None, True),
                ("float", "broken", "skill", "casper", "1.2.0", False),
                ("float", "log-my-time", "skill", "casper", "1.2.0", True),
                ("sphera-cow", "*", "skill", "client", None, True),
            ],
        )
        self.assertEqual((rows[2].marketplace, rows[2].marketplace_name, rows[2].user_group, rows[2].snapshot_id), ("Secret Sauce", "casper-secret-sauce", "Ops", "abc123"))
        self.assertEqual(rows[0].user_group, "Project Management")

    def test_unknown_repo_is_a_client_marketplace(self):
        self.write(".claude-plugin/marketplace.json", json.dumps({"name": "sphera-cow", "plugins": []}))
        rows, _ = build_rows(self.root, "Casper-Studios/sphera-m3-cow", "abc123")
        self.assertTrue(all(r.origin == "client" and r.marketplace == "sphera-cow" for r in rows))

    def test_ambiguous_names(self):
        self.write("plugins/engineering/git-pr/skills/log-my-time/SKILL.md", "---\nname: log-my-time\ndescription: Same name, other plugin.\n---\n")
        rows, _ = build_rows(self.root, SECRET, "abc123")
        self.assertEqual(ambiguous_names(rows), ["commit", "data-analysis", "log-my-time"])

    def test_json_omits_snapshot_and_check_detects_drift(self):
        rows, _ = build_rows(self.root, SECRET, "abc123")
        ambiguous = ambiguous_names(rows)
        out = self.root / "telemetry"
        self.assertIn("is missing", check_json(rows, ambiguous, out))
        write_json(rows, ambiguous, out)
        self.assertIsNone(check_json(rows, ambiguous, out))
        self.assertNotIn("abc123", (out / "casper-skills.json").read_text())
        later, _ = build_rows(self.root, SECRET, "def456")
        self.assertIsNone(check_json(later, ambiguous, out))
        self.write("plugins/ops/float/skills/new-one/SKILL.md", "---\nname: new-one\ndescription: x\n---\n")
        changed, _ = build_rows(self.root, SECRET, "def456")
        self.assertIn("out of date", check_json(changed, ambiguous_names(changed), out))


class FakeTransport:
    def __init__(self):
        self.calls = []

    def post(self, url, headers, body):
        self.calls.append((url, headers, json.loads(body)))
        return 200


class PayloadTest(unittest.TestCase):
    def row(self, **overrides):
        base = dict(snapshot_id="abc123", repo=SECRET, marketplace="Secret Sauce", marketplace_name="casper-secret-sauce", plugin="float",
                    plugin_version="1.2.0", skill="log-my-time", folder="log-my-time", kind="skill", category="ops", user_group="Ops",
                    path="plugins/ops/float/skills/log-my-time/SKILL.md", origin="casper", frontmatter_ok=True)
        return RegistryRow(**{**base, **overrides})

    def test_payload_shape(self):
        body = payload([self.row(), self.row(skill="init-brain", kind="command")], ["commit"], "abc123", SECRET, now_ns=42)
        resource = body["resourceLogs"][0]
        attrs = {a["key"]: a["value"] for a in resource["resource"]["attributes"]}
        self.assertEqual(attrs["service.name"], {"stringValue": "casper-skill-registry"})
        records = resource["scopeLogs"][0]["logRecords"]
        self.assertEqual([r["body"]["stringValue"] for r in records], ["registry.skill", "registry.skill", "registry.ambiguous", "registry.snapshot"])
        first = {a["key"]: a["value"] for a in records[0]["attributes"]}
        self.assertEqual(first["registry.skill"], {"stringValue": "log-my-time"})
        self.assertEqual(first["registry.frontmatter_ok"], {"boolValue": True})
        self.assertEqual(records[0]["timeUnixNano"], "42")
        summary = {a["key"]: a["value"] for a in records[-1]["attributes"]}
        self.assertEqual(summary["registry.skills"], {"intValue": "1"})
        self.assertEqual(summary["registry.commands"], {"intValue": "1"})
        self.assertEqual(summary["registry.ambiguous"], {"intValue": "1"})

    def test_send_posts_to_logs_endpoint_with_token(self):
        transport = FakeTransport()
        status = send({"resourceLogs": []}, "pylf_v1_token", "https://logfire-us.pydantic.dev/", transport)
        self.assertEqual(status, 200)
        url, headers, body = transport.calls[0]
        self.assertEqual(url, "https://logfire-us.pydantic.dev/v1/logs")
        self.assertEqual(headers["Authorization"], "pylf_v1_token")
        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertEqual(body, {"resourceLogs": []})

    def test_to_json_is_sorted_and_stable(self):
        text = to_json([self.row()], ["commit"])
        data = json.loads(text)
        self.assertEqual(list(data), ["ambiguous", "rows"])
        self.assertNotIn("snapshot_id", data["rows"][0])
        self.assertTrue(text.endswith("\n"))


if __name__ == "__main__":
    unittest.main()

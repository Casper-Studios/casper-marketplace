import tempfile
import unittest
from pathlib import Path

import notion
from notion import Page
from reconcile import RepoSkill, command_names, plan, reconcile, repo_skills
from registry import Row

SECRET = "Secret Sauce"
PUBLIC = "Public Marketplace"


def skill(name="a-skill", plugin="candidate-evaluation", category="hr", description="Does the thing.", error=None):
    return RepoSkill(
        folder=name, category=category, plugin=plugin, path=f"plugins/{category}/{plugin}/skills/{name}/SKILL.md",
        name=name, description=description, error=error,
    )


def row(name="a-skill", status="Beta", marketplace=SECRET, plugin="candidate-evaluation", user_group="HR", id="row-id"):
    return Row(id=id, url=f"https://www.notion.so/{id}", status=status, name=name, marketplace=marketplace, plugin=plugin, user_group=user_group)


def no_owner(skill):
    return None


class PlanTest(unittest.TestCase):
    def test_matching_row_is_unchanged_and_not_listed(self):
        result = plan([skill()], set(), [row()], SECRET, no_owner)
        self.assertEqual((result.actions, result.unchanged, result.failures), ([], 1, []))

    def test_missing_row_is_created(self):
        result = plan([skill()], set(), [], SECRET, lambda s: "owner-id")
        action = result.actions[0]
        self.assertEqual(action.create["Status"], notion.status("Needs Documentation"))
        self.assertEqual(action.create["Owner"], notion.people("owner-id"))
        self.assertEqual(action.create["Marketplace"], notion.select(SECRET))
        self.assertIn("Row created", action.result.outcome)

    def test_missing_row_without_frontmatter_is_not_created(self):
        result = plan([skill(description=None, error="no frontmatter block")], set(), [], SECRET, no_owner)
        action = result.actions[0]
        self.assertIsNone(action.create)
        self.assertIn("Fix the frontmatter first", action.result.outcome)
        self.assertIn("folder name was used", action.result.warnings[0])

    def test_unreadable_frontmatter_still_fixes_path_fields(self):
        result = plan([skill(description=None, error="bad yaml")], set(), [row(plugin="old-plugin")], SECRET, no_owner)
        action = result.actions[0]
        self.assertEqual(action.update, {"Plugin": notion.select("candidate-evaluation")})
        self.assertIn("folder name was used", action.result.warnings[0])

    def test_drift_is_fixed(self):
        result = plan([skill()], set(), [row(plugin="onboarding", user_group="Engineering", marketplace=None)], SECRET, no_owner)
        action = result.actions[0]
        self.assertEqual(set(action.update), {"Plugin", "User Group", "Marketplace"})
        self.assertIn("Plugin onboarding to candidate-evaluation", action.result.outcome)
        self.assertIn("Marketplace empty to Secret Sauce", action.result.outcome)

    def test_deprecated_row_with_a_folder_comes_back(self):
        result = plan([skill()], set(), [row(status="Deprecated")], SECRET, no_owner)
        self.assertEqual(result.actions[0].update, {"Status": notion.status("Beta")})

    def test_row_without_a_folder_is_deprecated(self):
        result = plan([skill()], set(), [row(), row(name="gone", id="gone-id")], SECRET, no_owner)
        self.assertEqual(len(result.actions), 1)
        action = result.actions[0]
        self.assertEqual((action.result.name, action.update), ("gone", {"Status": notion.status("Deprecated")}))

    def test_in_flight_orphan_is_left_alone(self):
        for status in ("For Review", "Needs Documentation", "Not Created"):
            with self.subTest(status=status):
                result = plan([], set(), [row(name="pending", status=status)], SECRET, no_owner)
                self.assertIsNone(result.actions[0].update)
                self.assertIn("open pull request", result.actions[0].result.outcome)

    def test_orphan_with_empty_status_is_deprecated(self):
        result = plan([], set(), [row(name="gone", status=None)], SECRET, no_owner)
        self.assertEqual(result.actions[0].update, {"Status": notion.status("Deprecated")})

    def test_already_deprecated_orphan_is_left_and_counted(self):
        result = plan([], set(), [row(name="gone", status="Deprecated")], SECRET, no_owner)
        self.assertEqual((result.actions, result.unchanged), ([], 1))

    def test_command_row_is_left_alone(self):
        result = plan([], {"init-brain"}, [row(name="init-brain")], SECRET, no_owner)
        self.assertIsNone(result.actions[0].update)
        self.assertIn("command", result.actions[0].result.outcome)

    def test_other_marketplace_rows_are_not_touched(self):
        result = plan([], set(), [row(name="public-skill", marketplace=PUBLIC)], SECRET, no_owner)
        self.assertEqual((result.actions, result.unchanged), ([], 0))

    def test_skill_whose_row_is_in_the_other_marketplace_is_moved(self):
        result = plan([skill()], set(), [row(marketplace=SECRET)], PUBLIC, no_owner)
        self.assertEqual(result.actions[0].update, {"Marketplace": notion.select(PUBLIC)})

    def test_two_rows_with_one_name_fail(self):
        result = plan([skill()], set(), [row(), row(id="two")], SECRET, no_owner)
        self.assertIn("Two or more registry rows are named `a-skill`", result.failures[0])
        self.assertEqual(result.actions[0].result.outcome, "Nothing was written.")

    def test_governance_maps(self):
        result = plan([skill(category="governance", plugin="marketplace")], set(), [], PUBLIC, no_owner)
        self.assertEqual(result.actions[0].create["User Group"], notion.select("Governance"))


class RepoTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())

    def write(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    def test_reads_every_skill(self):
        self.write("plugins/hr/candidate-evaluation/skills/a-skill/SKILL.md", "---\nname: a-skill\ndescription: Does it.\n---\n")
        self.write("plugins/hr/candidate-evaluation/skills/broken/SKILL.md", "no frontmatter\n")
        self.write("plugins/product/data-analysis/SKILL.md", "---\nname: not-a-skill-folder\ndescription: x\n---\n")
        self.write("plugins/weird/thing/skills/x/SKILL.md", "---\nname: x\ndescription: x\n---\n")
        skills, skipped = repo_skills(self.root)
        self.assertEqual([(s.name, s.description, s.error is None) for s in skills], [("a-skill", "Does it.", True), ("broken", None, False)])
        self.assertEqual(skills[1].path, "plugins/hr/candidate-evaluation/skills/broken/SKILL.md")
        self.assertEqual(len(skipped), 1)
        self.assertIn("unknown category `weird`", skipped[0])

    def test_frontmatter_name_wins_over_folder(self):
        self.write("plugins/hr/candidate-evaluation/skills/folder/SKILL.md", "---\nname: real-name\ndescription: x\n---\n")
        skills, _ = repo_skills(self.root)
        self.assertEqual((skills[0].name, skills[0].folder), ("real-name", "folder"))

    def test_command_names(self):
        self.write("plugins/project-management/brain/commands/init-brain.md", "# init")
        self.write("plugins/project-management/brain/commands/init-brain/templates/x.tmpl", "")
        self.assertEqual(command_names(self.root), {"init-brain"})


class FakeApi:
    dry_run = False

    def __init__(self, pages, content=()):
        self.pages = pages
        self.writes = []
        self.content = set(content)

    def query_all(self, data_source_id):
        return self.pages

    def find_user(self, display_name):
        return "owner-id" if display_name else None

    def create_page(self, data_source_id, properties):
        self.writes.append(("create", properties))
        return Page.model_validate({"id": "new-id", "url": "https://www.notion.so/new"})

    def update_page(self, page_id, properties):
        self.writes.append(("update", page_id, properties))
        return Page.model_validate({"id": page_id})

    def has_content(self, page_id):
        return page_id in self.content

    def append_blocks(self, page_id, blocks):
        self.writes.append(("blocks", page_id))

    def get_page(self, page_id):
        return None

    def query_by_name(self, data_source_id, name):
        return []


def page(name, status="Beta", marketplace=SECRET, plugin="candidate-evaluation", id=None, in_trash=False):
    return Page.model_validate({
        "id": id or name, "url": f"https://www.notion.so/{name}", "in_trash": in_trash,
        "properties": {
            "Name": {"title": [{"plain_text": name}]},
            "Status": {"status": {"name": status}},
            "Marketplace": {"select": {"name": marketplace}},
            "Plugin": {"select": {"name": plugin}},
            "User Group": {"select": {"name": "HR"}},
        },
    })


class ReconcileTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        md = self.root / "plugins/hr/candidate-evaluation/skills/a-skill/SKILL.md"
        md.parent.mkdir(parents=True)
        md.write_text("---\nname: a-skill\ndescription: Does it.\n---\n", encoding="utf-8")

    def test_creates_deprecates_and_fills_empty_pages(self):
        api = FakeApi([page("gone"), page("trashed", in_trash=True)])
        report = reconcile(api, "ds", self.root, "o/r", SECRET, lambda s: "owner-id")
        self.assertEqual([w[0] for w in api.writes], ["create", "blocks", "update"])
        self.assertEqual(api.writes[2][1:], ("gone", {"Status": notion.status("Deprecated")}))
        self.assertEqual((report.skills, report.rows, report.unchanged), (1, 1, 0))
        self.assertEqual([r.name for r in report.results], ["a-skill", "gone"])
        self.assertEqual(report.results[0].url, "https://www.notion.so/new")

    def test_update_fills_only_an_empty_page(self):
        api = FakeApi([page("a-skill", plugin="old")])
        reconcile(api, "ds", self.root, "o/r", SECRET, lambda s: None)
        self.assertEqual([w[0] for w in api.writes], ["update", "blocks"])
        full = FakeApi([page("a-skill", plugin="old")], content={"a-skill"})
        reconcile(full, "ds", self.root, "o/r", SECRET, lambda s: None)
        self.assertEqual([w[0] for w in full.writes], ["update"])

    def test_nothing_to_do(self):
        api = FakeApi([page("a-skill")])
        report = reconcile(api, "ds", self.root, "o/r", SECRET, lambda s: None)
        self.assertEqual((api.writes, report.results, report.unchanged), ([], [], 1))


if __name__ == "__main__":
    unittest.main()

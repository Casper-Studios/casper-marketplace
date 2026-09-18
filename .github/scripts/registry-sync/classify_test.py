import json
import subprocess
import unittest
from pathlib import Path

import classify
from classify import FrontmatterError, classify as run, notion_page_id, parse_frontmatter

TEMPLATE_COMMENT = "<!-- Required for existing skills. Leave blank for new skills. -->"
URL = "https://app.notion.com/p/3c8e373e28c681868974ec9caf2865ae"
ID = "3c8e373e28c681868974ec9caf2865ae"


def body(notion_line=None, skill_name=None, ticked="Add a new skill", extra=""):
    lines = ["## About this PR", "", "**Change type:**", ""]
    for label in classify.CHECKBOX_MODES:
        mark = "x" if label == ticked else " "
        lines.append(f"- [{mark}] {label}")
    lines.append("- [ ] Update supporting tooling or documentation")
    lines.append("")
    if skill_name is not None:
        lines.append(f"**Skill name:** {skill_name}".rstrip())
    if notion_line is not None:
        lines.append(f"**Notion page:** {notion_line}".rstrip())
    lines += ["", "### What changed and why", "", extra]
    return "\n".join(lines)


def skill_md(name, description="Does the thing. Use when asked."):
    return f"---\nname: {name}\ndescription: {description}\n---\n\n# {name}\n"


class Repo:
    """Files at BASE and at HEAD."""

    def __init__(self, base=None, head=None):
        self.files = {"BASE": base or {}, "HEAD": head or {}}

    def __call__(self, revision, path):
        return self.files[revision].get(path)


def plan(diff, prbody="", base=None, head=None):
    return run(diff, prbody, "BASE", "HEAD", Repo(base, head))


NEW_MD = "plugins/engineering/engineering-nursery/skills/draft-weekly-digest/SKILL.md"


class NotionLineTest(unittest.TestCase):
    def test_good_url(self):
        self.assertEqual(notion_page_id(body(URL)), ID)

    def test_url_with_trailing_comment(self):
        self.assertEqual(notion_page_id(body(f"{URL} {TEMPLATE_COMMENT}")), ID)

    def test_dashed_url_with_query_string(self):
        line = (
            "https://www.notion.so/casperstudios/Skill-Registry-3c2e373e-28c6-812d-88c6-fc27429d9017"
            "?v=39ce373e28c680fdbc54000c06edf5e6"
        )
        self.assertEqual(notion_page_id(body(line)), "3c2e373e28c6812d88c6fc27429d9017")

    def test_blank_line(self):
        self.assertIsNone(notion_page_id(body("")))

    def test_not_applicable(self):
        self.assertIsNone(notion_page_id(body("N/A")))

    def test_template_comment_alone(self):
        self.assertIsNone(notion_page_id(body(TEMPLATE_COMMENT)))

    def test_skill_placeholder(self):
        self.assertIsNone(notion_page_id(body("_(added after approval)_")))

    def test_no_line_at_all(self):
        self.assertIsNone(notion_page_id("## What this is\n\nA new plugin.\n"))
        self.assertIsNone(classify.notion_line("## What this is\n"))

    def test_prose_without_link(self):
        self.assertIsNone(notion_page_id(body("will add later")))

    def test_first_link_wins(self):
        other = "https://www.notion.so/Other-11111111111111111111111111111111"
        self.assertEqual(notion_page_id(body(f"{URL} and {other}")), ID)


class SkillNameLineTest(unittest.TestCase):
    def test_present(self):
        self.assertEqual(classify.skill_name_line(body(skill_name="draft-weekly-digest")), "draft-weekly-digest")

    def test_blank(self):
        self.assertIsNone(classify.skill_name_line(body(skill_name="")))

    def test_absent(self):
        self.assertIsNone(classify.skill_name_line("nothing here"))


class DiffTest(unittest.TestCase):
    def test_add(self):
        result = plan(f"A\t{NEW_MD}", body(skill_name="draft-weekly-digest"), head={NEW_MD: skill_md("draft-weekly-digest")})
        self.assertEqual(len(result.skills), 1)
        skill = result.skills[0]
        self.assertEqual((skill.name, skill.mode, skill.plugin, skill.user_group), ("draft-weekly-digest", "new", "engineering-nursery", "Engineering"))
        self.assertIsNone(skill.base_name)
        self.assertEqual(skill.description, "Does the thing. Use when asked.")

    def test_update(self):
        files = {NEW_MD: skill_md("draft-weekly-digest")}
        result = plan(f"M\t{NEW_MD}", body(ticked="Update an existing skill"), base=files, head={NEW_MD: skill_md("draft-weekly-digest", "Changed.")})
        skill = result.skills[0]
        self.assertEqual(skill.mode, "update")
        self.assertEqual(skill.base_description, "Does the thing. Use when asked.")
        self.assertEqual(skill.description, "Changed.")

    def test_update_touching_only_a_reference_file(self):
        ref = "plugins/engineering/engineering-nursery/skills/draft-weekly-digest/references/x.md"
        files = {NEW_MD: skill_md("draft-weekly-digest")}
        result = plan(f"A\t{ref}", "", base=files, head=files)
        self.assertEqual([(s.name, s.mode) for s in result.skills], [("draft-weekly-digest", "update")])

    def test_rename_folder(self):
        old = "plugins/engineering/engineering-nursery/skills/old-name/SKILL.md"
        new = "plugins/engineering/engineering-nursery/skills/new-name/SKILL.md"
        result = plan(f"R095\t{old}\t{new}", body(ticked="Rename or move a skill"), base={old: skill_md("old-name")}, head={new: skill_md("new-name")})
        skill = result.skills[0]
        self.assertEqual((skill.mode, skill.name, skill.base_name, skill.base_path), ("rename", "new-name", "old-name", old))
        self.assertEqual(skill.search_names, ["old-name", "new-name"])

    def test_move_between_plugins(self):
        old = "plugins/engineering/engineering-nursery/skills/x/SKILL.md"
        new = "plugins/engineering/tools/skills/x/SKILL.md"
        result = plan(f"R100\t{old}\t{new}", "", base={old: skill_md("x")}, head={new: skill_md("x")})
        self.assertEqual((result.skills[0].mode, result.skills[0].plugin), ("rename", "tools"))

    def test_delete(self):
        files = {NEW_MD: skill_md("draft-weekly-digest")}
        result = plan(f"D\t{NEW_MD}", body(ticked="Deprecate or remove a skill"), base=files, head={})
        skill = result.skills[0]
        self.assertEqual((skill.mode, skill.name, skill.head_path), ("removed", "draft-weekly-digest", None))
        self.assertEqual(skill.warnings, [])

    def test_delete_of_a_reference_file_is_an_update(self):
        ref = "plugins/engineering/engineering-nursery/skills/draft-weekly-digest/references/x.md"
        files = {NEW_MD: skill_md("draft-weekly-digest")}
        result = plan(f"D\t{ref}", "", base=files, head=files)
        self.assertEqual([(s.name, s.mode) for s in result.skills], [("draft-weekly-digest", "update")])

    def test_two_skills_one_url(self):
        other = "plugins/engineering/engineering-nursery/skills/other/SKILL.md"
        head = {NEW_MD: skill_md("draft-weekly-digest"), other: skill_md("other")}
        result = plan(f"A\t{NEW_MD}\nA\t{other}", body(URL, skill_name="other"), head=head)
        by_name = {s.name: s for s in result.skills}
        self.assertEqual(by_name["other"].notion_id, ID)
        self.assertIsNone(by_name["draft-weekly-digest"].notion_id)

    def test_url_without_skill_name_line_goes_to_nobody(self):
        result = plan(f"A\t{NEW_MD}", body(URL), head={NEW_MD: skill_md("draft-weekly-digest")})
        self.assertIsNone(result.skills[0].notion_id)
        self.assertEqual(result.notion_id, ID)

    def test_rename_from_unparseable_old_path_is_an_update(self):
        old = "plugins/engineering-nursery/skills/create-repo-onboarding-skill/SKILL.md"
        new = "plugins/engineering/engineering-nursery/skills/create-repo-onboarding-skill/SKILL.md"
        md = skill_md("create-onboarding-skill")
        result = plan(f"R100\t{old}\t{new}", "", base={old: md}, head={new: md})
        skill = result.skills[0]
        self.assertEqual((skill.mode, skill.name, skill.plugin), ("update", "create-onboarding-skill", "engineering-nursery"))

    def test_rename_from_unparseable_old_path_with_new_folder_is_a_rename(self):
        old = "plugins/engineering-nursery/skills/old/SKILL.md"
        new = "plugins/engineering/engineering-nursery/skills/new/SKILL.md"
        result = plan(f"R080\t{old}\t{new}", "", base={old: skill_md("x")}, head={new: skill_md("x")})
        self.assertEqual(result.skills[0].mode, "rename")

    def test_move_with_heavy_edits_pairs_delete_and_add(self):
        old = "plugins/product/product-nursery/skills/old-folder/SKILL.md"
        new = "plugins/product/discovery/skills/new-folder/SKILL.md"
        result = plan(f"D\t{old}\nA\t{new}", "", base={old: skill_md("same-name", "Old text.")}, head={new: skill_md("same-name", "New text.")})
        self.assertEqual(len(result.skills), 1)
        skill = result.skills[0]
        self.assertEqual((skill.mode, skill.name, skill.base_path, skill.plugin), ("rename", "same-name", old, "discovery"))
        self.assertEqual(skill.base_description, "Old text.")

    def test_frontmatter_name_changed_in_place(self):
        result = plan(f"M\t{NEW_MD}", "", base={NEW_MD: skill_md("old-name")}, head={NEW_MD: skill_md("new-name")})
        skill = result.skills[0]
        self.assertEqual((skill.mode, skill.name, skill.base_name), ("update", "new-name", "old-name"))
        self.assertEqual(skill.search_names, ["old-name", "new-name"])

    def test_no_frontmatter_is_skipped_and_named(self):
        result = plan(f"A\t{NEW_MD}", "", head={NEW_MD: "# Just a heading\n"})
        self.assertEqual(result.skills, [])
        self.assertEqual(result.skipped, [f"`{NEW_MD}`: no frontmatter block. Fix the frontmatter and push again."])

    def test_unreadable_base_frontmatter_is_a_warning_not_a_skip(self):
        result = plan(f"M\t{NEW_MD}", "", base={NEW_MD: "no frontmatter"}, head={NEW_MD: skill_md("draft-weekly-digest")})
        self.assertEqual(result.skipped, [])
        skill = result.skills[0]
        self.assertEqual((skill.mode, skill.base_name), ("update", None))
        self.assertIn("before this pull request could not be read", skill.warnings[0])

    def test_removed_skill_with_unreadable_base_is_skipped(self):
        result = plan(f"D\t{NEW_MD}", "", base={NEW_MD: "no frontmatter"}, head={})
        self.assertEqual(result.skills, [])
        self.assertIn("removed", result.skipped[0])

    def test_checkbox_disagrees_with_diff(self):
        result = plan(f"A\t{NEW_MD}", body(ticked="Update an existing skill"), head={NEW_MD: skill_md("draft-weekly-digest")})
        warning = result.skills[0].warnings[0]
        self.assertIn("'Update an existing skill'", warning)
        self.assertIn("adds a new skill", warning)

    def test_checkbox_agrees(self):
        result = plan(f"A\t{NEW_MD}", body(ticked="Add a new skill"), head={NEW_MD: skill_md("draft-weekly-digest")})
        self.assertEqual(result.skills[0].warnings, [])

    def test_no_skills_touched(self):
        result = plan("M\t.claude-plugin/marketplace.json\nM\tREADME.md", body())
        self.assertEqual(result.skills, [])

    def test_user_group_mapping(self):
        self.assertEqual(
            classify.USER_GROUPS,
            {
                "bizdev": "BizDev",
                "design": "Design",
                "engineering": "Engineering",
                "governance": "Governance",
                "hr": "HR",
                "ops": "Ops",
                "product": "Product",
                "project-management": "Project Management",
            },
        )

    def test_unknown_category_is_skipped_and_named(self):
        path = "plugins/weird/tools/skills/x/SKILL.md"
        result = plan(f"A\t{path}", "", head={path: skill_md("x")})
        self.assertEqual(result.skills, [])
        self.assertIn("unknown category `weird`", result.skipped[0])


# SKILL.md files whose frontmatter the sync cannot read, per marketplace. The reconcile falls
# back to the folder name for these. Fix the file and remove it from the list.
KNOWN_UNREADABLE = {
    "casper-secret-sauce": [
        # `: ` inside a plain scalar is not valid YAML.
        "plugins/hr/candidate-evaluation/skills/tech-screen-prep/SKILL.md",
        "plugins/product/discovery/skills/discovery-automations/SKILL.md",
    ],
    "casper-studios": [],
}


class FrontmatterTest(unittest.TestCase):
    def test_plain(self):
        fm = parse_frontmatter("---\nname: a\ndescription: Plain text, one line.\nextra: ignored\n---\n")
        self.assertEqual((fm.name, fm.description), ("a", "Plain text, one line."))

    def test_colon_space_in_plain_scalar_is_not_yaml(self):
        with self.assertRaises(FrontmatterError) as caught:
            parse_frontmatter("---\nname: a\ndescription: Plain text: with a colon.\n---\n")
        self.assertIn("not valid YAML", str(caught.exception))

    def test_name_must_be_a_string(self):
        with self.assertRaises(FrontmatterError):
            parse_frontmatter("---\nname: 12\ndescription: x\n---\n")

    def test_double_quoted_with_escapes(self):
        fm = parse_frontmatter('---\nname: a\ndescription: "Say \\"hi\\" now."\n---\n')
        self.assertEqual(fm.description, 'Say "hi" now.')

    def test_single_quoted(self):
        fm = parse_frontmatter("---\nname: 'a'\ndescription: 'It''s fine'\n---\n")
        self.assertEqual((fm.name, fm.description), ("a", "It's fine"))

    def test_folded_block_with_paragraphs(self):
        text = "---\nname: a\ndescription: >\n  First line\n  same paragraph.\n\n  Second paragraph.\ncompat: x\n---\n"
        fm = parse_frontmatter(text)
        self.assertEqual(fm.description, "First line same paragraph.\nSecond paragraph.")

    def test_literal_block(self):
        fm = parse_frontmatter("---\nname: a\ndescription: |\n  one\n  two\n---\n")
        self.assertEqual(fm.description, "one\ntwo")

    def test_no_frontmatter(self):
        with self.assertRaises(FrontmatterError):
            parse_frontmatter("# heading\n")

    def test_missing_name(self):
        with self.assertRaises(FrontmatterError):
            parse_frontmatter("---\ndescription: x\n---\n")

    def test_description_as_list_is_unreadable(self):
        with self.assertRaises(FrontmatterError):
            parse_frontmatter("---\nname: a\ndescription:\n  - one\n  - two\n---\n")

    def test_every_skill_md_on_main(self):
        root = Path(__file__).resolve().parents[3]
        marketplace = json.loads((root / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))["name"]
        paths = subprocess.run(["git", "ls-files", "plugins/*/*/skills/*/SKILL.md"], cwd=root, capture_output=True, text=True, check=True).stdout.split()
        self.assertGreaterEqual(len(paths), 20)
        unreadable = []
        for path in paths:
            try:
                fm = parse_frontmatter((root / path).read_text(encoding="utf-8"))
                self.assertTrue(fm.name and fm.description, path)
            except FrontmatterError:
                unreadable.append(path)
        self.assertEqual(unreadable, KNOWN_UNREADABLE[marketplace])

if __name__ == "__main__":
    unittest.main()

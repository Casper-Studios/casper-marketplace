import unittest

from render import ReconcileReport, ReconcileResult, Report, SkillResult, marker, read_marker, render, render_reconcile


class MarkerTest(unittest.TestCase):
    def test_round_trip(self):
        body = render(Report(skills=[], remembered={"a-skill": "Beta"}))
        self.assertEqual(read_marker(body), {"a-skill": "Beta"})

    def test_not_ours(self):
        self.assertIsNone(read_marker("LGTM"))
        self.assertIsNone(read_marker(""))

    def test_empty_remembered(self):
        self.assertEqual(read_marker(marker({})), {})

    def test_broken_json_is_ours_with_nothing_remembered(self):
        self.assertEqual(read_marker("<!-- registry-sync {not json} -->"), {})


class RenderTest(unittest.TestCase):
    def test_one_line_per_skill_with_link_and_warning(self):
        report = Report(
            skills=[
                SkillResult("a", "new", "Row created with Status For Review.", "https://n/a", ["You ticked 'Update an existing skill', but this pull request adds a new skill. The diff decides."]),
                SkillResult("b", "removed", "This skill was removed from the repo. The row was left alone."),
            ],
            skipped=["`plugins/x/y/skills/z/SKILL.md`: no frontmatter block. Fix the frontmatter and push again."],
        )
        text = render(report)
        self.assertIn("- **a** (new skill): Row created with Status For Review. [Open the Notion page](https://n/a). ⚠️ You ticked", text)
        self.assertIn("- **b** (removed skill): This skill was removed from the repo. The row was left alone.\n", text)
        self.assertIn("- ⚠️ Skipped `plugins/x/y/skills/z/SKILL.md`: no frontmatter block. Fix the frontmatter and push again.", text)
        self.assertTrue(text.startswith("<!-- registry-sync "))
        self.assertIn("finish the documentation before this is merged", text)

    def test_only_removed_skills_says_what_merge_does(self):
        text = render(Report(skills=[SkillResult("b", "removed", "x")]))
        self.assertIn("When this pull request is merged, the row is set to Deprecated", text)
        merged = render(Report(skills=[SkillResult("b", "removed", "x")], merged=True, closed=True))
        self.assertIn("The registry matches main", merged)

    def test_dry_run_banner(self):
        self.assertIn("_Dry run. Nothing was written to Notion._", render(Report(skills=[], dry_run=True)))
        self.assertNotIn("Dry run", render(Report(skills=[])))

    def test_next_step_by_state(self):
        self.assertIn("finish the documentation before this is merged", render(Report(skills=[SkillResult("a", "new", "x")])))
        self.assertIn("The registry matches main", render(Report(skills=[SkillResult("a", "new", "x")], merged=True, closed=True)))
        self.assertIn("The pull request is closed", render(Report(skills=[SkillResult("a", "new", "x")], closed=True)))
        self.assertIn("Nothing for you to do. The sync failed on its own side.", render(Report(skills=[], failures=["Two rows named a."])))
        self.assertIn("❌ Two rows named a.", render(Report(skills=[], failures=["Two rows named a."])))


class ReconcileRenderTest(unittest.TestCase):
    def test_counts_lines_and_next_step(self):
        report = ReconcileReport(
            results=[
                ReconcileResult("a", "No row. Row created with Status Needs Documentation.", "https://n/a"),
                ReconcileResult("gone", "No folder in the repo. Status set to Deprecated.", "https://n/gone"),
                ReconcileResult("odd", "Fixed: Plugin x to y.", None, ["The frontmatter at `p` could not be read (bad), so the folder name was used as the skill name."]),
            ],
            skipped=["`plugins/weird/x/skills/y/SKILL.md`: unknown category `weird`. Add it to USER_GROUPS in classify.py."],
            dry_run=True, marketplace="Secret Sauce", skills=20, rows=23, unchanged=17,
        )
        text = render_reconcile(report)
        self.assertIn("_Dry run. Nothing was written to Notion._", text)
        self.assertIn("20 skills in the repository, 23 Secret Sauce rows in the registry.", text)
        self.assertIn("17 already match. Not listed.", text)
        self.assertIn("- **a**: No row. Row created with Status Needs Documentation. [Open the Notion page](https://n/a).", text)
        self.assertIn("- **odd**: Fixed: Plugin x to y. ⚠️ The frontmatter", text)
        self.assertIn("- ⚠️ Skipped `plugins/weird", text)
        self.assertIn("**Next step:** Open each new Notion page and finish the documentation.", text)
        self.assertNotIn("registry-sync {", text)

    def test_failure_and_quiet_next_steps(self):
        failed = render_reconcile(ReconcileReport(results=[], failures=["Two rows named a."]))
        self.assertIn("- ❌ Two rows named a.", failed)
        self.assertIn("The sync owner fixes the cause", failed)
        self.assertIn("Nothing. The registry matches main.", render_reconcile(ReconcileReport(results=[])))


if __name__ == "__main__":
    unittest.main()

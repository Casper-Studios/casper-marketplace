import unittest

import notion
from classify import Plan, SkillChange
from notion import Page
from registry import Ambiguous, Row, marketplace_for
from sync import MERGED_STATUS, NEW_STATUS, Event, decide, find_row, sync

SECRET = "Secret Sauce"
PUBLIC = "Public Marketplace"


def event(action="opened", merged=False, repo="Casper-Studios/casper-secret-sauce"):
    closed = action == "closed"
    return Event(
        number=1, action=action, state="closed" if closed else "open", merged=merged,
        merge_commit_sha="abc" if merged else None, head_sha="head", body="", title="", branch="", author="me", repo=repo,
    )


def skill(mode="new", name="a-skill", description="Does the thing.", base_description=None, base_name=None, notion_id=None):
    return SkillChange(
        name=name, mode=mode, category="hr", plugin="candidate-evaluation", folder=name,
        head_path=None if mode == "removed" else f"plugins/hr/candidate-evaluation/skills/{name}/SKILL.md",
        base_path=None if mode == "new" else f"plugins/hr/candidate-evaluation/skills/{name}/SKILL.md",
        description=description, base_name=base_name, base_description=base_description, notion_id=notion_id,
    )


def row(status="For Review", name="a-skill", marketplace=SECRET):
    return Row(id="row-id", url="https://www.notion.so/row", status=status, name=name, marketplace=marketplace)


class OpenEventTest(unittest.TestCase):
    def test_create_on_open(self):
        decision = decide(skill(), None, event(), None, "owner-id", SECRET)
        self.assertIsNotNone(decision.create)
        self.assertIsNone(decision.update)
        self.assertEqual(set(decision.create), {"Name", "Description", "Owner", "Status", "Marketplace", "User Group", "Plugin"})
        self.assertEqual(decision.create["Status"], notion.status(NEW_STATUS))
        self.assertEqual(decision.create["User Group"], notion.select("HR"))
        self.assertEqual(decision.create["Marketplace"], notion.select(SECRET))
        self.assertEqual(decision.create["Owner"], notion.people("owner-id"))
        self.assertEqual(decision.create["Description"], notion.rich_text("Does the thing."))
        self.assertIsNone(decision.remember)

    def test_create_without_owner(self):
        decision = decide(skill(), None, event(), None, None, SECRET)
        self.assertNotIn("Owner", decision.create)

    def test_create_in_marketplace_repo(self):
        decision = decide(skill(), None, event(), None, None, PUBLIC)
        self.assertEqual(decision.create["Marketplace"], notion.select(PUBLIC))

    def test_for_review_remembers_old_status(self):
        for old in ("Beta", "Standard", "Not Created", "Deprecated", None):
            with self.subTest(old=old):
                decision = decide(skill("update"), row(old), event("synchronize"), None, None, SECRET)
                self.assertEqual(decision.update, {"Status": notion.status("For Review")})
                self.assertIsNone(decision.create)
                self.assertEqual(decision.remember, old or "")
                self.assertEqual(decision.warnings, [])

    def test_for_review_keeps_the_first_remembered_value(self):
        decision = decide(skill("update"), row("Beta"), event("synchronize"), "Standard", None, SECRET)
        self.assertEqual(decision.remember, "Standard")

    def test_leave_for_review_alone(self):
        for status in ("For Review", "Needs Documentation"):
            with self.subTest(status=status):
                decision = decide(skill("update"), row(status), event("edited"), "Beta", None, SECRET)
                self.assertIsNone(decision.update)
                self.assertIsNone(decision.create)
                self.assertEqual(decision.remember, "Beta")

    def test_only_status_is_written_before_merge(self):
        decision = decide(skill("update", description="new text", base_description="old text"), row("Beta"), event("synchronize"), None, None, SECRET)
        self.assertEqual(list(decision.update), ["Status"])

    def test_row_from_other_marketplace_warns_but_is_not_moved_yet(self):
        decision = decide(skill("update"), row("Beta", marketplace=SECRET), event(), None, None, PUBLIC)
        self.assertEqual(list(decision.update), ["Status"])
        self.assertIn("Merging this pull request moves it to Public Marketplace", decision.warnings[0])


class MergeTest(unittest.TestCase):
    def test_merge_refreshes_and_sets_beta(self):
        decision = decide(skill("update"), row("For Review"), event("closed", merged=True), "Beta", None, SECRET)
        self.assertEqual(set(decision.update), {"Name", "Plugin", "User Group", "Status"})
        self.assertEqual(decision.update["Status"], notion.status(MERGED_STATUS))
        self.assertEqual(decision.update["Name"], notion.title("a-skill"))
        self.assertIsNone(decision.remember)

    def test_merge_refreshes_description_only_when_changed(self):
        same = decide(skill("update", description="x", base_description="x"), row(), event("closed", merged=True), None, None, SECRET)
        self.assertNotIn("Description", same.update)
        new_only = decide(skill("new", description="x"), row(), event("closed", merged=True), None, None, SECRET)
        self.assertNotIn("Description", new_only.update)
        changed = decide(skill("update", description="y", base_description="x"), row(), event("closed", merged=True), None, None, SECRET)
        self.assertEqual(changed.update["Description"], notion.rich_text("y"))

    def test_merge_writes_new_name_on_renamed_skill(self):
        decision = decide(skill("update", name="new-name", base_name="old-name"), row(name="old-name"), event("closed", merged=True), None, None, SECRET)
        self.assertEqual(decision.update["Name"], notion.title("new-name"))

    def test_merge_creates_missing_row_as_needs_documentation(self):
        decision = decide(skill(), None, event("closed", merged=True), None, "owner-id", SECRET)
        self.assertEqual(decision.create["Status"], notion.status(NEW_STATUS))
        self.assertIn("Owner", decision.create)

    def test_merge_brings_a_deprecated_row_back(self):
        decision = decide(skill("update"), row("Deprecated"), event("closed", merged=True), None, None, SECRET)
        self.assertEqual(decision.update["Status"], notion.status(MERGED_STATUS))
        self.assertEqual(decision.warnings, [])

    def test_merge_moves_the_row_to_this_marketplace(self):
        decision = decide(skill("update"), row("Deprecated", marketplace=SECRET), event("closed", merged=True), None, None, PUBLIC)
        self.assertEqual(decision.update["Marketplace"], notion.select(PUBLIC))
        self.assertEqual(decision.update["Status"], notion.status(MERGED_STATUS))
        self.assertIn("This row was Secret Sauce. It is now Public Marketplace.", decision.warnings[0])

    def test_merge_fills_an_empty_marketplace_without_warning(self):
        decision = decide(skill("update"), row("Beta", marketplace=None), event("closed", merged=True), None, None, SECRET)
        self.assertEqual(decision.update["Marketplace"], notion.select(SECRET))
        self.assertEqual(decision.warnings, [])

    def test_merge_same_marketplace_leaves_it(self):
        decision = decide(skill("update"), row("Beta"), event("closed", merged=True), None, None, SECRET)
        self.assertNotIn("Marketplace", decision.update)


class CloseUnmergedTest(unittest.TestCase):
    def test_close_unmerged_restores(self):
        for old in ("Beta", "Deprecated"):
            with self.subTest(old=old):
                decision = decide(skill("update"), row("For Review"), event("closed"), old, None, SECRET)
                self.assertEqual(decision.update, {"Status": notion.status(old)})
                self.assertIsNone(decision.remember)

    def test_close_unmerged_restores_empty(self):
        decision = decide(skill("update"), row("For Review"), event("closed"), "", None, SECRET)
        self.assertEqual(decision.update, {"Status": notion.clear_status()})

    def test_close_unmerged_no_restore_when_row_moved(self):
        decision = decide(skill("update"), row("Standard"), event("closed"), "Beta", None, SECRET)
        self.assertIsNone(decision.update)
        self.assertIn("left alone", decision.outcome)

    def test_close_unmerged_nothing_remembered(self):
        decision = decide(skill(), row("For Review"), event("closed"), None, None, SECRET)
        self.assertIsNone(decision.update)
        self.assertIsNone(decision.create)

    def test_close_unmerged_no_row(self):
        decision = decide(skill(), None, event("closed"), None, None, SECRET)
        self.assertIsNone(decision.create)

    def test_edited_after_close_counts_as_closed(self):
        closed = Event(number=1, action="edited", state="closed", merged=False, merge_commit_sha=None, head_sha="h", body="", title="", branch="", author="", repo="o/r")
        decision = decide(skill("update"), row("Beta"), closed, None, None, SECRET)
        self.assertIsNone(decision.update)


class RemovedTest(unittest.TestCase):
    def test_removed_and_merged_deprecates(self):
        for status in ("Beta", "For Review", "Needs Documentation", None):
            with self.subTest(status=status):
                decision = decide(skill("removed"), row(status), event("closed", merged=True), None, None, SECRET)
                self.assertEqual(decision.update, {"Status": notion.status("Deprecated")})
                self.assertIsNone(decision.create)

    def test_removed_and_merged_already_deprecated(self):
        decision = decide(skill("removed"), row("Deprecated"), event("closed", merged=True), None, None, SECRET)
        self.assertIsNone(decision.update)
        self.assertIn("already Deprecated", decision.outcome)

    def test_removed_open_or_closed_writes_nothing(self):
        for action, merged in (("opened", False), ("synchronize", False), ("closed", False)):
            with self.subTest(action=action):
                decision = decide(skill("removed"), row("Beta"), event(action, merged), "Beta", None, SECRET)
                self.assertIsNone(decision.create)
                self.assertIsNone(decision.update)
        self.assertIn("set to Deprecated when this pull request is merged", decide(skill("removed"), row(), event(), None, None, SECRET).outcome)

    def test_removed_open_keeps_the_marker(self):
        self.assertEqual(decide(skill("removed"), row(), event(), "Beta", None, SECRET).remember, "Beta")

    def test_removed_without_row(self):
        for action, merged in (("opened", False), ("closed", True), ("closed", False)):
            with self.subTest(action=action, merged=merged):
                decision = decide(skill("removed"), None, event(action, merged), None, None, SECRET)
                self.assertIsNone(decision.create)
                self.assertIsNone(decision.update)


class MarketplaceTest(unittest.TestCase):
    def test_known_repos(self):
        self.assertEqual(marketplace_for("Casper-Studios/casper-secret-sauce"), SECRET)
        self.assertEqual(marketplace_for("Casper-Studios/casper-marketplace"), PUBLIC)

    def test_unknown_repo_stops(self):
        with self.assertRaises(SystemExit) as caught:
            marketplace_for("Casper-Studios/private-casper-marketplace")
        self.assertIn("not a repository the sync knows", str(caught.exception))


class FakeApi:
    dry_run = True

    def __init__(self, page=None, rows=None, content=()):
        self.page = page
        self.rows = rows or {}
        self.queries = []
        self.writes = []
        self.content = set(content)

    def find_user(self, display_name):
        return None

    def create_page(self, data_source_id, properties):
        self.writes.append(("create", data_source_id, properties))
        return Page.model_validate({"id": "new-id", "url": "https://www.notion.so/new"})

    def update_page(self, page_id, properties):
        self.writes.append(("update", page_id, properties))
        return Page.model_validate({"id": page_id})

    def get_page(self, page_id):
        return self.page

    def query_by_name(self, data_source_id, name):
        self.queries.append(name)
        return self.rows.get(name, [])

    def query_all(self, data_source_id):
        return [page for pages in self.rows.values() for page in pages]

    def has_content(self, page_id):
        return page_id in self.content

    def append_blocks(self, page_id, blocks):
        self.writes.append(("blocks", page_id, blocks))


def page(**overrides):
    base = {
        "id": "page-id", "url": "https://www.notion.so/page", "archived": False, "in_trash": False,
        "parent": {"type": "data_source_id", "data_source_id": "39ce373e-28c6-806c-a81c-000b11e50a5a"},
        "properties": {"Name": {"title": [{"plain_text": "a-skill"}]}, "Status": {"status": {"name": "Beta"}}},
    }
    base.update(overrides)
    return Page.model_validate(base)


DS = "39ce373e-28c6-806c-a81c-000b11e50a5a"


class FindRowTest(unittest.TestCase):
    def test_link_resolves(self):
        api = FakeApi(page=page())
        warnings = []
        found = find_row(api, DS, skill(notion_id="page-id"), warnings)
        self.assertEqual((found.id, found.status), ("page-id", "Beta"))
        self.assertEqual((api.queries, warnings), ([], []))

    def test_dead_link_falls_back_to_search(self):
        api = FakeApi(page=None, rows={"a-skill": [page(id="found")]})
        warnings = []
        found = find_row(api, DS, skill(notion_id="page-id"), warnings)
        self.assertEqual(found.id, "found")
        self.assertIn("did not resolve", warnings[0])

    def test_trashed_link_falls_back(self):
        api = FakeApi(page=page(in_trash=True))
        warnings = []
        self.assertIsNone(find_row(api, DS, skill(notion_id="page-id"), warnings))
        self.assertIn("trash", warnings[0])
        self.assertEqual(api.queries, ["a-skill"])

    def test_link_to_another_database_falls_back(self):
        api = FakeApi(page=page(parent={"type": "data_source_id", "data_source_id": "other"}))
        warnings = []
        self.assertIsNone(find_row(api, DS, skill(notion_id="page-id"), warnings))
        self.assertIn("not a Skill Registry page", warnings[0])

    def test_search_by_base_name_first(self):
        api = FakeApi(rows={"old-name": [page(id="old-row")]})
        found = find_row(api, DS, skill("update", name="new-name", base_name="old-name"), [])
        self.assertEqual((found.id, api.queries), ("old-row", ["old-name"]))

    def test_search_falls_through_to_new_name(self):
        api = FakeApi(rows={"new-name": [page(id="new-row")]})
        found = find_row(api, DS, skill("update", name="new-name", base_name="old-name"), [])
        self.assertEqual((found.id, api.queries), ("new-row", ["old-name", "new-name"]))

    def test_two_rows_is_a_failure(self):
        api = FakeApi(rows={"a-skill": [page(), page()]})
        with self.assertRaises(Ambiguous):
            find_row(api, DS, skill(), [])

    def test_row_carries_the_selects(self):
        props = {
            "Name": {"title": [{"plain_text": "a-skill"}]},
            "Status": {"status": {"name": "Beta"}},
            "Marketplace": {"select": {"name": "Secret Sauce"}},
            "Plugin": {"select": {"name": "onboarding"}},
            "User Group": {"select": {"name": "Engineering"}},
        }
        found = find_row(FakeApi(rows={"a-skill": [page(properties=props)]}), DS, skill(), [])
        self.assertEqual((found.marketplace, found.plugin, found.user_group), ("Secret Sauce", "onboarding", "Engineering"))


def plan(*skills):
    return Plan(skills=list(skills), notion_id=None, notion_line=None, skill_name=None, ticked=[])


class SyncBodyTest(unittest.TestCase):
    def test_create_writes_the_headings(self):
        api = FakeApi()
        report = sync(event(), plan(skill()), api, DS, {}, SECRET)
        kinds = [write[0] for write in api.writes]
        self.assertEqual(kinds, ["create", "blocks"])
        self.assertEqual(api.writes[1][1], "new-id")
        self.assertIn("headings were added", report.skills[0].outcome)
        self.assertEqual(report.skills[0].url, "https://www.notion.so/new")

    def test_update_fills_only_an_empty_page(self):
        empty = FakeApi(rows={"a-skill": [page()]})
        sync(event("closed", merged=True), plan(skill("update")), empty, DS, {}, SECRET)
        self.assertEqual([w[0] for w in empty.writes], ["update", "blocks"])
        full = FakeApi(rows={"a-skill": [page()]}, content={"page-id"})
        report = sync(event("closed", merged=True), plan(skill("update")), full, DS, {}, SECRET)
        self.assertEqual([w[0] for w in full.writes], ["update"])
        self.assertNotIn("headings", report.skills[0].outcome)

    def test_no_write_means_no_headings(self):
        api = FakeApi(rows={"a-skill": [page(properties={"Name": {"title": [{"plain_text": "a-skill"}]}, "Status": {"status": {"name": "For Review"}}})]})
        sync(event(), plan(skill("update")), api, DS, {}, SECRET)
        self.assertEqual(api.writes, [])

    def test_deprecating_never_adds_headings(self):
        api = FakeApi(rows={"a-skill": [page()]})
        sync(event("closed", merged=True), plan(skill("removed")), api, DS, {}, SECRET)
        self.assertEqual([w[0] for w in api.writes], ["update"])
        self.assertEqual(api.writes[0][2], {"Status": notion.status("Deprecated")})


if __name__ == "__main__":
    unittest.main()

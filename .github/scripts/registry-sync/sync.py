#!/usr/bin/env python3
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "pydantic>=2,<3",
#   "pyyaml>=6,<7",
# ]
# ///
"""Keep the Notion Skill Registry in step with this repository.

    uv run --locked --script sync.py run [--pr <n>] [--dry-run] [--data-source <id>]
    uv run --locked --script sync.py reconcile [--dry-run] [--data-source <id>]
    uv run --locked --script sync.py export [--dry-run] [--check] [--out telemetry]
    uv run --locked --script sync.py test

``run`` syncs one pull request. On a ``pull_request`` event the fields come from
environment variables (``PR_NUMBER``, ``PR_ACTION``, ...). With ``--pr <n>`` they come
from ``gh pr view``. ``reconcile`` compares every skill in the checkout with the
registry and fixes what differs.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path

import body
import export
import notion
import reconcile
from classify import Plan, SkillChange, classify
from notion import Notion, NotionError, Page
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from registry import (
    DATA_SOURCE_ID,
    DEFAULT_REPO,
    DEPRECATED_STATUS,
    LEAVE_ALONE,
    MERGED_STATUS,
    NEW_STATUS,
    REVIEW_STATUS,
    Ambiguous,
    Registry,
    Row,
    find_by_name,
    marketplace_for,
    new_row_properties,
    row_from,
)
from render import Report, SkillResult, read_marker, render, render_reconcile


class Event(BaseModel):
    """One pull request event."""

    model_config = ConfigDict(extra="forbid")

    number: int
    action: str
    state: str
    merged: bool
    merge_commit_sha: str | None
    head_sha: str
    body: str
    title: str
    branch: str
    author: str
    repo: str

    @property
    def closed(self):
        return self.action == "closed" or self.state.lower() in ("closed", "merged")


@dataclass
class Decision:
    outcome: str
    create: dict[str, object] | None = None
    update: dict[str, object] | None = None
    remember: str | None = None
    warnings: list[str] = field(default_factory=list)


# --- the write table -------------------------------------------------------------


def full_properties(skill: SkillChange, owner_id: str | None, status_name: str, marketplace: str):
    if skill.description is None:
        raise RuntimeError(f"{skill.name} has no description to write; only removed skills lack one.")
    return new_row_properties(skill.name, skill.description, status_name, marketplace, skill.user_group, skill.plugin, owner_id)


def status_property(name: str):
    return notion.status(name) if name else notion.clear_status()


def decide(skill: SkillChange, row: Row | None, event: Event, remembered: str | None, owner_id: str | None, marketplace: str):
    """What to write for one skill. No network, no git."""
    warnings = list(skill.warnings)
    if skill.mode == "removed":
        return decide_removed(row, event, remembered, warnings)

    if event.closed and event.merged:
        if row is None:
            return Decision(
                f"Merged. Row created with Status {NEW_STATUS}.",
                create=full_properties(skill, owner_id, NEW_STATUS, marketplace),
                warnings=warnings,
            )
        props: dict[str, object] = {
            "Name": notion.title(skill.name),
            "Plugin": notion.select(skill.plugin),
            "User Group": notion.select(skill.user_group),
            "Status": notion.status(MERGED_STATUS),
        }
        parts = ["Name, Plugin and User Group refreshed", f"Status set to {MERGED_STATUS}"]
        if row.marketplace != marketplace:
            props["Marketplace"] = notion.select(marketplace)
            parts.append(f"Marketplace set to {marketplace}")
            if row.marketplace:
                warnings.append(
                    f"This row was {row.marketplace}. It is now {marketplace}. "
                    "If the skill is still in the other repository, remove it there."
                )
        if skill.base_description and skill.description and skill.base_description != skill.description:
            props["Description"] = notion.rich_text(skill.description)
            parts.append("Description refreshed because it changed in this pull request")
        return Decision(f"Merged. {'; '.join(parts)}.", update=props, warnings=warnings)

    if event.closed:
        if row is None:
            return Decision("Closed without merge. It has no registry row, so there is nothing to do.", warnings=warnings)
        if remembered is not None and row.status == REVIEW_STATUS:
            return Decision(
                f"Closed without merge. Status put back to {remembered or 'empty'}.",
                update={"Status": status_property(remembered)},
                warnings=warnings,
            )
        if remembered is not None:
            return Decision(
                f"Closed without merge. Status is {row.status or 'empty'}, not {REVIEW_STATUS}, so it was left alone.",
                warnings=warnings,
            )
        return Decision("Closed without merge. The row was left alone.", warnings=warnings)

    if row is None:
        return Decision(
            f"Row created with Status {NEW_STATUS}.",
            create=full_properties(skill, owner_id, NEW_STATUS, marketplace),
            warnings=warnings,
        )
    if row.marketplace and row.marketplace != marketplace:
        warnings.append(f"This row is {row.marketplace}. Merging this pull request moves it to {marketplace}.")
    if row.status in LEAVE_ALONE:
        return Decision(f"Row already exists and is {row.status}. Nothing changed.", remember=remembered, warnings=warnings)
    old = row.status or ""
    return Decision(
        f"Row exists. Status moved from {old or 'empty'} to {REVIEW_STATUS}.",
        update={"Status": notion.status(REVIEW_STATUS)},
        remember=remembered if remembered is not None else old,
        warnings=warnings,
    )


def decide_removed(row: Row | None, event: Event, remembered: str | None, warnings: list[str]):
    if row is None:
        return Decision("Removed from the repo. It has no registry row, so there is nothing to do.", warnings=warnings)
    if event.closed and event.merged:
        if row.status == DEPRECATED_STATUS:
            return Decision(f"Removed from the repo. The row was already {DEPRECATED_STATUS}.", warnings=warnings)
        return Decision(
            f"Removed from the repo. Status set to {DEPRECATED_STATUS}.",
            update={"Status": notion.status(DEPRECATED_STATUS)},
            warnings=warnings,
        )
    if event.closed:
        return Decision("Closed without merge. The row was left alone.", warnings=warnings)
    return Decision(
        f"Removed from the repo. The row is set to {DEPRECATED_STATUS} when this pull request is merged.",
        remember=remembered,
        warnings=warnings,
    )


# --- finding the row -------------------------------------------------------------


def find_row(api: Registry, data_source_id: str, skill: SkillChange, warnings: list[str]):
    if skill.notion_id:
        page = api.get_page(skill.notion_id)
        if page is None:
            warnings.append("The Notion link on this pull request did not resolve (no such page), so the registry was searched by name.")
        elif page.archived or page.in_trash:
            warnings.append("The Notion link on this pull request points at a page in the trash, so the registry was searched by name.")
        elif page.parent_id != notion.normalize_id(data_source_id):
            warnings.append("The Notion link on this pull request is not a Skill Registry page, so the registry was searched by name.")
        else:
            return row_from(page)
    return find_by_name(api, data_source_id, skill.search_names)


# --- git and gh ------------------------------------------------------------------


class PullRequestView(BaseModel):
    """The fields the sync reads from ``gh pr view --json``."""

    model_config = ConfigDict(extra="ignore")

    class Author(BaseModel):
        model_config = ConfigDict(extra="ignore")
        login: str = ""

    class MergeCommit(BaseModel):
        model_config = ConfigDict(extra="ignore")
        oid: str

    number: int
    state: str
    body: str | None = None
    title: str = ""
    author: Author = Field(default_factory=Author)
    head_ref_oid: str = Field(alias="headRefOid")
    head_ref_name: str = Field(default="", alias="headRefName")
    merge_commit: MergeCommit | None = Field(default=None, alias="mergeCommit")


class GitHubUser(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: str | None = None


class IssueComment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    body: str | None = None


def run(*args: str, stdin: str | None = None):
    result = subprocess.run(args, capture_output=True, text=True, input=stdin)
    if result.returncode != 0:
        raise RuntimeError(f"{' '.join(args[:3])} failed: {result.stderr.strip() or result.stdout.strip()}")
    return result.stdout


def git(*args: str):
    return run("git", *args)


def gh[T: BaseModel](model: type[T], *args: str):
    raw = run("gh", *args)
    try:
        return model.model_validate_json(raw)
    except ValidationError as error:
        raise RuntimeError(f"gh {' '.join(args[:2])} returned an unexpected shape: {error.error_count()} problems") from error


def event_from_env(env: dict[str, str]):
    if not env.get("PR_NUMBER"):
        raise SystemExit("PR_NUMBER is not set. Pass --pr <n> to run locally.")
    try:
        return Event(
            number=int(env["PR_NUMBER"]),
            action=env.get("PR_ACTION", "synchronize"),
            state=env.get("PR_STATE", "open"),
            merged=env.get("PR_MERGED", "false").lower() == "true",
            merge_commit_sha=env.get("PR_MERGE_COMMIT_SHA") or None,
            head_sha=env["PR_HEAD_SHA"],
            body=env.get("PR_BODY", ""),
            title=env.get("PR_TITLE", ""),
            branch=env.get("PR_BRANCH", ""),
            author=env.get("PR_AUTHOR", ""),
            repo=env.get("GH_REPO") or env.get("GITHUB_REPOSITORY") or DEFAULT_REPO,
        )
    except (KeyError, ValueError, ValidationError) as error:
        raise SystemExit(f"The pull request event in the environment is incomplete: {error}") from error


def event_from_gh(number: int, repo: str):
    view = gh(
        PullRequestView,
        "pr", "view", str(number), "-R", repo,
        "--json", "number,state,body,title,author,headRefOid,headRefName,mergeCommit,mergedAt",
    )
    closed = view.state in ("MERGED", "CLOSED")
    return Event(
        number=view.number,
        action="closed" if closed else "opened",
        state="closed" if closed else "open",
        merged=view.state == "MERGED",
        merge_commit_sha=view.merge_commit.oid if view.merge_commit else None,
        head_sha=view.head_ref_oid,
        body=view.body or "",
        title=view.title,
        branch=view.head_ref_name,
        author=view.author.login,
        repo=repo,
    )


def fetch(event: Event):
    git("fetch", "--quiet", "origin", "main")
    git("fetch", "--quiet", "origin", f"refs/pull/{event.number}/head")


def base_for(event: Event):
    base_ref = f"{event.merge_commit_sha}^1" if event.merged and event.merge_commit_sha else "origin/main"
    return git("merge-base", base_ref, event.head_sha).strip()


def git_reader(revision: str, path: str):
    result = subprocess.run(["git", "show", f"{revision}:{path}"], capture_output=True, text=True)
    return result.stdout if result.returncode == 0 else None


def first_author(root: Path, path: str):
    """The name on the commit that added a file, or None if git does not know."""
    result = subprocess.run(
        ["git", "-C", str(root), "log", "--diff-filter=A", "--follow", "--format=%an", "--", path],
        capture_output=True,
        text=True,
    )
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    return lines[-1].strip() if result.returncode == 0 and lines else None


def github_display_name(login: str):
    if not login:
        return None
    try:
        return gh(GitHubUser, "api", f"users/{login}").name
    except RuntimeError:
        return None


def existing_comment(event: Event):
    raw = run("gh", "api", "--paginate", "--slurp", f"repos/{event.repo}/issues/{event.number}/comments")
    try:
        pages = json.loads(raw)
    except ValueError as error:
        raise RuntimeError("gh api comments returned something that is not JSON") from error
    for page in pages if isinstance(pages, list) else []:
        for item in page if isinstance(page, list) else []:
            try:
                comment = IssueComment.model_validate(item)
            except ValidationError:
                continue
            remembered = read_marker(comment.body or "")
            if remembered is not None:
                return comment.id, remembered
    return None, dict[str, str]()


def post_comment(event: Event, comment_id: int | None, body: str):
    payload = json.dumps({"body": body})
    if comment_id is None:
        run("gh", "api", "-X", "POST", f"repos/{event.repo}/issues/{event.number}/comments", "--input", "-", stdin=payload)
    else:
        run("gh", "api", "-X", "PATCH", f"repos/{event.repo}/issues/comments/{comment_id}", "--input", "-", stdin=payload)


def write_summary(text: str):
    """Show the report on the workflow run page, when there is one."""
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as summary:
            summary.write(text + "\n")


# --- one pull request ------------------------------------------------------------


def unused_link_warning(plan: Plan):
    if not plan.notion_id or any(s.notion_id for s in plan.skills):
        return None
    if plan.skill_name:
        return (
            f"The Notion link was not used: the **Skill name:** line says `{plan.skill_name}`, "
            "which is not a skill this pull request touches. Every skill was searched by name."
        )
    return (
        "The Notion link was not used because the pull request has no **Skill name:** line. "
        "Every skill was searched by name."
    )


def add_body(api: Registry, page_id: str, skill: SkillChange, repo: str, only_if_empty: bool):
    """Write the documentation headings. Returns True if they were written."""
    if skill.head_path is None:
        return False
    if only_if_empty and api.has_content(page_id):
        return False
    api.append_blocks(page_id, body.template(skill.name, repo, skill.head_path))
    return True


def sync(event: Event, plan: Plan, api: Registry, data_source_id: str, remembered: dict[str, str], marketplace: str):
    report = Report(
        skills=[],
        skipped=list(plan.skipped),
        dry_run=api.dry_run,
        merged=event.closed and event.merged,
        closed=event.closed,
    )
    if (warning := unused_link_warning(plan)) is not None:
        report.warnings.append(warning)
    owner_cache = dict[str, str | None]()
    for skill in plan.skills:
        warnings = list[str]()
        remembered_status = remembered.get(skill.name)
        if remembered_status is None and skill.base_name:
            remembered_status = remembered.get(skill.base_name)
        try:
            row = find_row(api, data_source_id, skill, warnings)
            owner_id = None
            if row is None and skill.mode != "removed":
                if event.author not in owner_cache:
                    owner_cache[event.author] = api.find_user(github_display_name(event.author))
                owner_id = owner_cache[event.author]
            decision = decide(skill, row, event, remembered_status, owner_id, marketplace)
            url = row.url if row else None
            outcome = decision.outcome
            if decision.create is not None:
                page = api.create_page(data_source_id, decision.create)
                url = None if page.id == notion.DRY_RUN_ID else page.link
                if add_body(api, page.id, skill, event.repo, only_if_empty=False):
                    outcome += " The documentation headings were added to the page."
            elif decision.update is not None and row is not None:
                api.update_page(row.id, decision.update)
                if add_body(api, row.id, skill, event.repo, only_if_empty=True):
                    outcome += " The page was empty, so the documentation headings were added."
            if decision.remember is not None:
                report.remembered[skill.name] = decision.remember
            report.skills.append(SkillResult(skill.name, skill.mode, outcome, url, warnings + decision.warnings))
        except Ambiguous as error:
            report.failures.append(str(error))
            report.skills.append(SkillResult(skill.name, skill.mode, "Nothing was written.", None, warnings))
        except NotionError as error:
            report.failures.append(f"`{skill.name}`: {error}. Re-run once the cause is fixed.")
            report.skills.append(SkillResult(skill.name, skill.mode, "Nothing was written.", None, warnings))
    return report


def is_dry_run(args: argparse.Namespace):
    return bool(args.dry_run) or os.environ.get("DRY_RUN", "").lower() in ("1", "true", "yes")


def run_sync(args: argparse.Namespace):
    dry_run = is_dry_run(args)
    event = event_from_gh(args.pr, args.repo) if args.pr else event_from_env(dict(os.environ))
    marketplace = marketplace_for(event.repo)
    print(f"PR #{event.number} {event.action} state={event.state} merged={event.merged} head={event.head_sha[:7]} dry_run={dry_run} marketplace={marketplace}")
    fetch(event)
    base = base_for(event)
    diff = git("diff", "--name-status", "--find-renames", base, event.head_sha)
    print(f"base={base[:7]} diff:\n{diff.rstrip() or '(empty)'}")
    plan = classify(diff, event.body, base, event.head_sha, git_reader)
    if not plan.skills and not plan.skipped:
        print("no skills touched")
        return 0
    for skill in plan.skills:
        print(f"skill {skill.name}: {skill.mode} plugin={skill.plugin} group={skill.user_group} notion_id={skill.notion_id} base_name={skill.base_name}")
    for note in plan.skipped:
        print(f"skipped {note}")

    comment_id, remembered = existing_comment(event)
    try:
        api = Notion(os.environ.get("NOTION_TOKEN", ""), dry_run=dry_run)
    except NotionError:
        report = Report(skills=[], skipped=list(plan.skipped), dry_run=dry_run, merged=event.closed and event.merged, closed=event.closed)
        report.failures.append(
            "NOTION_TOKEN is not set. Add the repository secret (or put it in a git-ignored .env for local runs). Nothing was read or written."
        )
    else:
        report = sync(event, plan, api, args.data_source, remembered, marketplace)
    body_text = render(report)
    print("--- comment ---")
    print(body_text)
    write_summary(body_text)
    if dry_run:
        print(f"DRY RUN {'PATCH' if comment_id else 'POST'} comment on PR #{event.number}")
    elif args.pr and not args.post_comment:
        print("comment not posted (pass --post-comment)")
    else:
        post_comment(event, comment_id, body_text)
    for failure in report.failures:
        print(f"FAILED: {failure}", file=sys.stderr)
    return 1 if report.failures else 0


# --- the whole repository --------------------------------------------------------


def run_reconcile(args: argparse.Namespace):
    dry_run = is_dry_run(args)
    marketplace = marketplace_for(args.repo)
    root = Path(args.root).resolve()
    print(f"reconcile {args.repo} at {root} dry_run={dry_run} marketplace={marketplace}")
    try:
        api = Notion(os.environ.get("NOTION_TOKEN", ""), dry_run=dry_run)
    except NotionError:
        print("FAILED: NOTION_TOKEN is not set. Add the repository secret (or put it in a git-ignored .env for local runs).", file=sys.stderr)
        return 1
    owner_cache = dict[str, str | None]()

    def owner_for(skill: reconcile.RepoSkill):
        name = first_author(root, skill.path)
        if name is None:
            return None
        if name not in owner_cache:
            owner_cache[name] = api.find_user(name)
        return owner_cache[name]

    report = reconcile.reconcile(api, args.data_source, root, args.repo, marketplace, owner_for)
    text = render_reconcile(report)
    print("--- report ---")
    print(text)
    write_summary(text)
    for failure in report.failures:
        print(f"FAILED: {failure}", file=sys.stderr)
    return 1 if report.failures else 0


# --- the registry as telemetry -------------------------------------------------------


def run_export(args: argparse.Namespace):
    """Write ``telemetry/casper-skills.json`` and send one log record per skill to Logfire."""
    dry_run = is_dry_run(args)
    root = Path(args.root).resolve()
    out_dir = root / args.out
    snapshot = export.snapshot_id(root)
    rows, skipped = export.build_rows(root, args.repo, snapshot)
    ambiguous = export.ambiguous_names(rows)
    print(f"export {args.repo} at {root} snapshot={snapshot[:7]} rows={len(rows)} ambiguous={ambiguous} dry_run={dry_run}")
    for note in skipped:
        print(f"skipped {note}")
    for row in rows:
        if not row.frontmatter_ok:
            print(f"warning: `{row.path}` has no readable frontmatter; the folder name `{row.folder}` is used as the skill name")
    if args.check:
        problem = export.check_json(rows, ambiguous, out_dir)
        if problem:
            print(f"FAILED: {problem}", file=sys.stderr)
            return 1
        print(f"{out_dir / export.OUTPUT_JSON} is current")
        return 0
    target = export.write_json(rows, ambiguous, out_dir)
    print(f"wrote {target}")
    body_json = export.payload(rows, ambiguous, snapshot, args.repo)
    count = len(body_json["resourceLogs"][0]["scopeLogs"][0]["logRecords"])
    base_url = export.base_url_from_env(dict(os.environ))
    if dry_run:
        print(f"DRY RUN would send {count} records to {base_url}{export.LOGS_PATH}")
        return 0
    token = os.environ.get("LOGFIRE_WRITE_TOKEN", "")
    if not token:
        print("FAILED: LOGFIRE_WRITE_TOKEN is not set. Add the repository secret (or put it in a git-ignored .env for local runs).", file=sys.stderr)
        return 1
    status = export.send(body_json, token, base_url, export.UrllibTransport())
    summary = f"Registry export: {count} records for snapshot `{snapshot[:7]}` sent to Logfire (HTTP {status})."
    print(summary)
    write_summary(summary)
    return 0


# --- main ------------------------------------------------------------------------


def add_shared_arguments(parser: argparse.ArgumentParser):
    parser.add_argument("--repo", default=os.environ.get("GH_REPO") or DEFAULT_REPO)
    parser.add_argument("--dry-run", action="store_true", help="print every write, send nothing (also DRY_RUN=1)")
    parser.add_argument(
        "--data-source",
        default=os.environ.get("REGISTRY_DATA_SOURCE_ID") or DATA_SOURCE_ID,
        help="Notion data source ID; point at a scratch copy for a live test",
    )


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    operations = parser.add_subparsers(dest="operation", required=True)
    run_parser = operations.add_parser("run", help="sync one pull request")
    run_parser.add_argument("--pr", type=int, help="pull request number; reads it with gh instead of the event env")
    add_shared_arguments(run_parser)
    run_parser.add_argument("--post-comment", action="store_true", help="with --pr: post the comment (never in a dry run)")
    reconcile_parser = operations.add_parser("reconcile", help="compare every skill in the checkout with the registry")
    add_shared_arguments(reconcile_parser)
    reconcile_parser.add_argument("--root", default=".", help="repository checkout to read (default: current directory)")
    export_parser = operations.add_parser("export", help="write telemetry/casper-skills.json and send the registry to Logfire")
    export_parser.add_argument("--repo", default=os.environ.get("GH_REPO") or DEFAULT_REPO)
    export_parser.add_argument("--root", default=".", help="repository checkout to read (default: current directory)")
    export_parser.add_argument("--out", default="telemetry", help="folder for casper-skills.json, relative to --root")
    export_parser.add_argument("--dry-run", action="store_true", help="write the file, send nothing (also DRY_RUN=1)")
    export_parser.add_argument("--check", action="store_true", help="fail if casper-skills.json is missing or stale; writes and sends nothing")
    operations.add_parser("test", help="run the unit tests beside these scripts")
    return parser


def main(argv: list[str] | None = None):
    args = build_parser().parse_args(argv)
    if args.operation == "test":
        suite = unittest.defaultTestLoader.discover(str(Path(__file__).resolve().parent), pattern="*_test.py")
        result = unittest.TextTestRunner(verbosity=1).run(suite)
        return 0 if result.wasSuccessful() else 1
    if args.operation == "reconcile":
        return run_reconcile(args)
    if args.operation == "export":
        return run_export(args)
    return run_sync(args)


if __name__ == "__main__":
    sys.exit(main())

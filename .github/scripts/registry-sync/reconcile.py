"""Compare every skill on disk with the registry and fix the differences. Never deletes."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

import body
import notion
from classify import SKILL_PATH, USER_GROUPS, FrontmatterError, parse_frontmatter
from notion import NotionError
from registry import DEPRECATED_STATUS, LEAVE_ALONE, MERGED_STATUS, NEW_STATUS, Registry, Row, new_row_properties, row_from
from render import ReconcileReport, ReconcileResult


@dataclass
class RepoSkill:
    """One skill folder on disk."""

    folder: str
    category: str
    plugin: str
    path: str
    name: str
    description: str | None = None
    error: str | None = None

    @property
    def user_group(self):
        return USER_GROUPS[self.category]


@dataclass
class Action:
    result: ReconcileResult
    skill: RepoSkill | None = None
    row: Row | None = None
    create: dict[str, object] | None = None
    update: dict[str, object] | None = None


@dataclass
class ReconcilePlan:
    actions: list[Action] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    unchanged: int = 0


type OwnerLookup = Callable[[RepoSkill], str | None]

# A row in one of these states may belong to a pull request that is not merged yet.
IN_FLIGHT = {*LEAVE_ALONE, "Not Created"}


# --- the repository ---------------------------------------------------------------


def repo_skills(root: Path):
    """Every ``plugins/<category>/<plugin>/skills/<folder>/SKILL.md`` under ``root``."""
    skills = list[RepoSkill]()
    skipped = list[str]()
    for md in sorted(root.glob("plugins/*/*/skills/*/SKILL.md")):
        path = md.relative_to(root).as_posix()
        match = SKILL_PATH.match(path)
        if match is None:
            continue
        category, plugin, folder = match["category"], match["plugin"], match["folder"]
        if category not in USER_GROUPS:
            skipped.append(f"`{path}`: unknown category `{category}`. Add it to USER_GROUPS in classify.py.")
            continue
        skill = RepoSkill(folder=folder, category=category, plugin=plugin, path=path, name=folder)
        try:
            frontmatter = parse_frontmatter(md.read_text(encoding="utf-8"))
        except (FrontmatterError, OSError, UnicodeDecodeError) as error:
            skill.error = str(error)
        else:
            skill.name = frontmatter.name
            skill.description = frontmatter.description
        skills.append(skill)
    return skills, skipped


def command_names(root: Path):
    """Names of the commands in every plugin. Their rows are left alone."""
    return {md.stem for md in root.glob("plugins/*/*/commands/*.md")}


# --- the plan ---------------------------------------------------------------------


def plan(skills: list[RepoSkill], commands: set[str], rows: list[Row], marketplace: str, owner_for: OwnerLookup):
    """What to write. No network."""
    by_name = dict[str, list[Row]]()
    for row in rows:
        by_name.setdefault(row.name, []).append(row)
    result = ReconcilePlan()

    for skill in skills:
        warnings = list[str]()
        if skill.error:
            warnings.append(
                f"The frontmatter at `{skill.path}` could not be read ({skill.error}), "
                "so the folder name was used as the skill name."
            )
        matches = by_name.get(skill.name, [])
        if len(matches) > 1:
            result.failures.append(
                f"Two or more registry rows are named `{skill.name}`. Merge them into one by hand, then re-run the sync."
            )
            result.actions.append(Action(ReconcileResult(skill.name, "Nothing was written.", None, warnings), skill=skill))
            continue
        if not matches:
            if skill.description is None:
                result.actions.append(
                    Action(
                        ReconcileResult(
                            skill.name, "No row. None was created, because the description could not be read. Fix the frontmatter first.", None, warnings
                        ),
                        skill=skill,
                    )
                )
                continue
            props = new_row_properties(
                skill.name, skill.description, NEW_STATUS, marketplace, skill.user_group, skill.plugin, owner_for(skill)
            )
            result.actions.append(
                Action(ReconcileResult(skill.name, f"No row. Row created with Status {NEW_STATUS}.", None, warnings), skill=skill, create=props)
            )
            continue
        row = matches[0]
        update = dict[str, object]()
        parts = list[str]()
        if row.plugin != skill.plugin:
            update["Plugin"] = notion.select(skill.plugin)
            parts.append(f"Plugin {row.plugin or 'empty'} to {skill.plugin}")
        if row.user_group != skill.user_group:
            update["User Group"] = notion.select(skill.user_group)
            parts.append(f"User Group {row.user_group or 'empty'} to {skill.user_group}")
        if row.marketplace != marketplace:
            update["Marketplace"] = notion.select(marketplace)
            parts.append(f"Marketplace {row.marketplace or 'empty'} to {marketplace}")
        if row.status == DEPRECATED_STATUS:
            update["Status"] = notion.status(MERGED_STATUS)
            parts.append(f"Status {DEPRECATED_STATUS} to {MERGED_STATUS}, because the skill is on main")
        if not update and not warnings:
            result.unchanged += 1
            continue
        outcome = "Matches the repo. Nothing changed." if not update else f"Fixed: {'; '.join(parts)}."
        result.actions.append(Action(ReconcileResult(skill.name, outcome, row.url, warnings), skill=skill, row=row, update=update or None))

    names = {skill.name for skill in skills}
    for row in rows:
        if row.marketplace != marketplace or row.name in names:
            continue
        if row.name in commands:
            result.actions.append(Action(ReconcileResult(row.name, "A command, not a skill. Left alone.", row.url), row=row))
            continue
        if row.status == DEPRECATED_STATUS:
            result.unchanged += 1
            continue
        if row.status in IN_FLIGHT:
            result.actions.append(
                Action(
                    ReconcileResult(row.name, f"No folder on main, but the row is {row.status}. Left alone: the skill may be in an open pull request.", row.url),
                    row=row,
                )
            )
            continue
        result.actions.append(
            Action(
                ReconcileResult(row.name, f"No folder in the repo. Status set to {DEPRECATED_STATUS}.", row.url),
                row=row,
                update={"Status": notion.status(DEPRECATED_STATUS)},
            )
        )
    return result


# --- doing it ---------------------------------------------------------------------


def reconcile(api: Registry, data_source_id: str, root: Path, repo: str, marketplace: str, owner_for: OwnerLookup):
    skills, skipped = repo_skills(root)
    commands = command_names(root)
    report = ReconcileReport(results=[], skipped=skipped, dry_run=api.dry_run, marketplace=marketplace, skills=len(skills))
    try:
        rows = [row_from(page) for page in api.query_all(data_source_id) if not page.archived and not page.in_trash]
    except NotionError as error:
        report.failures.append(f"{error}. Re-run once the cause is fixed.")
        return report
    report.rows = sum(1 for row in rows if row.marketplace == marketplace)
    planned = plan(skills, commands, rows, marketplace, owner_for)
    report.failures.extend(planned.failures)
    report.unchanged = planned.unchanged
    for action in planned.actions:
        result = action.result
        try:
            if action.create is not None and action.skill is not None:
                page = api.create_page(data_source_id, action.create)
                result.url = None if page.id == notion.DRY_RUN_ID else page.link
                api.append_blocks(page.id, body.template(action.skill.name, repo, action.skill.path))
                result.outcome += " The documentation headings were added to the page."
            elif action.update is not None and action.row is not None:
                api.update_page(action.row.id, action.update)
                if action.skill is not None and not api.has_content(action.row.id):
                    api.append_blocks(action.row.id, body.template(action.skill.name, repo, action.skill.path))
                    result.outcome += " The page was empty, so the documentation headings were added."
        except NotionError as error:
            report.failures.append(f"`{result.name}`: {error}. Re-run once the cause is fixed.")
            result.outcome = "Nothing was written."
        report.results.append(result)
    return report

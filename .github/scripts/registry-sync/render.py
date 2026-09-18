"""The pull request comment. One per pull request, found by a marker, edited in place."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from pydantic import BaseModel, ConfigDict, ValidationError

from classify import Mode, unhandled_mode

MARKER = re.compile(r"<!-- registry-sync (?P<json>\{.*?\}) -->", re.DOTALL)


class Marker(BaseModel):
    """The Status each row had before this pull request touched it."""

    model_config = ConfigDict(extra="ignore")

    remembered: dict[str, str] = {}


@dataclass
class SkillResult:
    name: str
    mode: Mode
    outcome: str
    url: str | None = None
    warnings: list[str] = field(default_factory=list)


@dataclass
class Report:
    skills: list[SkillResult]
    skipped: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    remembered: dict[str, str] = field(default_factory=dict)
    dry_run: bool = False
    merged: bool = False
    closed: bool = False


@dataclass
class ReconcileResult:
    name: str
    outcome: str
    url: str | None = None
    warnings: list[str] = field(default_factory=list)


@dataclass
class ReconcileReport:
    results: list[ReconcileResult]
    skipped: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    dry_run: bool = False
    marketplace: str = ""
    skills: int = 0
    rows: int = 0
    unchanged: int = 0


def mode_words(mode: Mode):
    match mode:
        case "new":
            return "new skill"
        case "update":
            return "updated skill"
        case "rename":
            return "renamed or moved skill"
        case "removed":
            return "removed skill"
        case _:
            return unhandled_mode(mode)


def marker(remembered: dict[str, str]):
    return f"<!-- registry-sync {Marker(remembered=dict(sorted(remembered.items()))).model_dump_json()} -->"


def read_marker(comment_body: str):
    """The marker data from an earlier comment, or None if the comment is not ours."""
    match = MARKER.search(comment_body)
    if match is None:
        return None
    try:
        return Marker.model_validate_json(match.group("json")).remembered
    except ValidationError:
        return dict[str, str]()


def render(report: Report):
    lines = [marker(report.remembered), "### Skill Registry", ""]
    if report.dry_run:
        lines += ["_Dry run. Nothing was written to Notion._", ""]
    for skill in report.skills:
        line = f"- **{skill.name}** ({mode_words(skill.mode)}): {skill.outcome}"
        if skill.url:
            line += f" [Open the Notion page]({skill.url})."
        for warning in skill.warnings:
            line += f" ⚠️ {warning}"
        lines.append(line)
    for note in report.skipped:
        lines.append(f"- ⚠️ Skipped {note}")
    for warning in report.warnings:
        lines.append(f"- ⚠️ {warning}")
    for failure in report.failures:
        lines.append(f"- ❌ {failure}")
    lines.append("")
    lines.append(f"**Next step:** {next_step(report)}")
    return "\n".join(lines) + "\n"


def next_step(report: Report):
    if report.failures:
        return (
            "Nothing for you to do. The sync failed on its own side. "
            "The sync owner fixes it and runs it again. "
            "Your pull request can still be reviewed and merged."
        )
    if report.merged:
        return "Nothing. The registry matches main."
    if report.closed:
        return "Nothing. The pull request is closed."
    if all(s.mode == "removed" for s in report.skills):
        return "Nothing now. When this pull request is merged, the row is set to Deprecated."
    return "Open the Notion page and finish the documentation before this is merged."


def render_reconcile(report: ReconcileReport):
    lines = ["### Skill Registry reconcile", ""]
    if report.dry_run:
        lines += ["_Dry run. Nothing was written to Notion._", ""]
    lines.append(f"{report.skills} skills in the repository, {report.rows} {report.marketplace} rows in the registry.")
    if report.unchanged:
        lines.append(f"{report.unchanged} already match. Not listed.")
    lines.append("")
    for result in report.results:
        line = f"- **{result.name}**: {result.outcome}"
        if result.url:
            line += f" [Open the Notion page]({result.url})."
        for warning in result.warnings:
            line += f" ⚠️ {warning}"
        lines.append(line)
    for note in report.skipped:
        lines.append(f"- ⚠️ Skipped {note}")
    for failure in report.failures:
        lines.append(f"- ❌ {failure}")
    lines.append("")
    if report.failures:
        lines.append("**Next step:** The sync owner fixes the cause and runs the reconcile again.")
    elif any("Row created" in r.outcome for r in report.results):
        lines.append("**Next step:** Open each new Notion page and finish the documentation.")
    else:
        lines.append("**Next step:** Nothing. The registry matches main.")
    return "\n".join(lines) + "\n"

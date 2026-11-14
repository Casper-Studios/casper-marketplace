"""Turn a pull request diff and body into one plan entry per skill. No network."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Literal, Never, Protocol

import yaml
from pydantic import BaseModel, ConfigDict, ValidationError

type Mode = Literal["new", "update", "rename", "removed"]

SKILL_PATH = re.compile(
    r"^plugins/(?P<category>[^/]+)/(?P<plugin>[^/]+)/skills/(?P<folder>[^/]+)/(?P<rest>.+)$"
)
LOOSE_SKILL_PATH = re.compile(r"^plugins/(?:.*/)?(?P<plugin>[^/]+)/skills/(?P<folder>[^/]+)/")
NOTION_LINE = re.compile(r"^\*\*Notion page:\*\*(?P<rest>.*)$", re.MULTILINE)
SKILL_NAME_LINE = re.compile(r"^\*\*Skill name:\*\*(?P<rest>.*)$", re.MULTILINE)
NOTION_URL = re.compile(
    r"https?://(?:[\w.-]+\.)?(?:notion\.so|notion\.com|notion\.site)/[^\s<>)\"']*", re.IGNORECASE
)
HEX32 = re.compile(r"[0-9a-f]{32}", re.IGNORECASE)
CHECKBOX = re.compile(r"^\s*[-*]\s*\[(?P<mark>[xX ])\]\s*(?P<label>.+?)\s*$", re.MULTILINE)
FRONTMATTER = re.compile(r"\A---\r?\n(?P<yaml>.*?)\r?\n(?:---|\.\.\.)[ \t]*(?:\r?\n|\Z)", re.DOTALL)

# Category folder under plugins/ to the User Group option in the registry.
USER_GROUPS = {
    "bizdev": "BizDev",
    "design": "Design",
    "engineering": "Engineering",
    "governance": "Governance",
    "hr": "HR",
    "ops": "Ops",
    "product": "Product",
    "project-management": "Project Management",
}

CHECKBOX_MODES: dict[str, Mode] = {
    "Add a new skill": "new",
    "Update an existing skill": "update",
    "Rename or move a skill": "rename",
    "Deprecate or remove a skill": "removed",
}


def describe_mode(mode: Mode):
    match mode:
        case "new":
            return "adds a new skill"
        case "update":
            return "updates an existing skill"
        case "rename":
            return "renames or moves a skill"
        case "removed":
            return "removes a skill"
        case _:
            return unhandled_mode(mode)


def unhandled_mode(value: Never) -> Never:
    raise RuntimeError(f"Unhandled skill mode: {value!r}")


class Reader(Protocol):
    """A file's text at a revision, or None if it is not there."""

    def __call__(self, revision: str, path: str) -> str | None: ...


class FrontmatterError(ValueError):
    """The frontmatter is missing or unreadable."""


class Frontmatter(BaseModel):
    """The keys the registry needs. Other keys are ignored."""

    model_config = ConfigDict(extra="ignore", strict=True)

    name: str
    description: str


@dataclass
class SkillChange:
    name: str
    mode: Mode
    category: str
    plugin: str
    folder: str
    head_path: str | None
    base_path: str | None
    description: str | None = None
    base_name: str | None = None
    base_description: str | None = None
    notion_id: str | None = None
    warnings: list[str] = field(default_factory=list)

    @property
    def user_group(self):
        return USER_GROUPS[self.category]

    @property
    def search_names(self):
        """Names to search by, base name first if it changed."""
        names = list[str]()
        if self.base_name and self.base_name != self.name:
            names.append(self.base_name)
        names.append(self.name)
        return names


@dataclass
class Plan:
    skills: list[SkillChange]
    notion_id: str | None
    notion_line: str | None
    skill_name: str | None
    ticked: list[str]
    skipped: list[str] = field(default_factory=list)


# --- frontmatter -----------------------------------------------------------------


def parse_frontmatter(text: str):
    """Read ``name`` and ``description`` from a SKILL.md's frontmatter.

    Raises ``FrontmatterError`` if the block is missing, is not YAML, or lacks either key.
    """
    match = FRONTMATTER.match(text)
    if match is None:
        raise FrontmatterError("no frontmatter block")
    try:
        data = yaml.safe_load(match.group("yaml"))
    except yaml.YAMLError as error:
        raise FrontmatterError(f"frontmatter is not valid YAML: {_first_line(str(error))}") from error
    if not isinstance(data, dict):
        raise FrontmatterError("frontmatter is not a mapping")
    try:
        parsed = Frontmatter.model_validate(data)
    except ValidationError as error:
        missing = ", ".join(str(item["loc"][0]) for item in error.errors())
        raise FrontmatterError(f"frontmatter needs string name and description ({missing})") from error
    if not parsed.name.strip():
        raise FrontmatterError("frontmatter name is empty")
    return Frontmatter(name=parsed.name.strip(), description=parsed.description.strip())


def _first_line(text: str):
    return text.strip().splitlines()[0] if text.strip() else text


# --- the body --------------------------------------------------------------------


def notion_line(body: str):
    match = NOTION_LINE.search(body)
    return match.group("rest").strip() if match else None


def notion_page_id(body: str):
    """The 32-hex page ID from the first Notion link on the ``**Notion page:**`` line."""
    line = notion_line(body)
    if not line:
        return None
    url = NOTION_URL.search(line)
    if url is None:
        return None
    path = url.group(0).split("?", 1)[0].split("#", 1)[0].replace("-", "")
    found = HEX32.findall(path)
    return found[-1].lower() if found else None


def skill_name_line(body: str):
    match = SKILL_NAME_LINE.search(body)
    if match is None:
        return None
    value = match.group("rest").strip().strip("`")
    return value or None


def ticked_boxes(body: str):
    return [match.group("label") for match in CHECKBOX.finditer(body) if match.group("mark").lower() == "x"]


# --- the diff --------------------------------------------------------------------


@dataclass
class DiffEntry:
    status: str
    path: str
    old_path: str | None = None


def parse_diff(text: str):
    entries = list[DiffEntry]()
    for line in text.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        status = parts[0][0]
        if status in "RC" and len(parts) >= 3:
            entries.append(DiffEntry(status, parts[2], parts[1]))
        elif len(parts) >= 2:
            entries.append(DiffEntry(status, parts[1]))
    return entries


def _loose_parts(path: str):
    match = LOOSE_SKILL_PATH.match(path)
    return (match.group("plugin"), match.group("folder")) if match else None


type SkillKey = tuple[str, str, str]


def classify(diff: str, body: str, base: str, head: str, read: Reader):
    entries = parse_diff(diff)
    groups = dict[SkillKey, list[DiffEntry]]()
    removed_groups = dict[SkillKey, list[DiffEntry]]()
    for entry in entries:
        match = SKILL_PATH.match(entry.path)
        if match is None:
            continue
        key = (match["category"], match["plugin"], match["folder"])
        target = removed_groups if entry.status == "D" else groups
        target.setdefault(key, []).append(entry)

    skipped = list[str]()
    skills = list[SkillChange]()

    for (category, plugin, folder), group in groups.items():
        head_md = f"plugins/{category}/{plugin}/skills/{folder}/SKILL.md"
        if category not in USER_GROUPS:
            skipped.append(f"`{head_md}`: unknown category `{category}`. Add it to USER_GROUPS in classify.py.")
            continue
        md_entry = next((entry for entry in group if entry.path == head_md), None)
        base_md = md_entry.old_path if md_entry and md_entry.old_path else head_md
        head_text = read(head, head_md)
        if head_text is None:
            # No SKILL.md at head: removed, or never a skill.
            removed_groups.setdefault((category, plugin, folder), []).extend(group)
            continue
        moved = False
        if md_entry and md_entry.old_path and md_entry.old_path != head_md:
            old = SKILL_PATH.match(md_entry.old_path)
            if old:
                moved = (old["plugin"], old["folder"]) != (plugin, folder)
            else:
                moved = _loose_parts(md_entry.old_path) != (plugin, folder)
        _append(skills, skipped, (category, plugin, folder), head_md, base_md, head_text, read(base, base_md), moved)

    for (category, plugin, folder), group in removed_groups.items():
        base_md = f"plugins/{category}/{plugin}/skills/{folder}/SKILL.md"
        if category not in USER_GROUPS:
            skipped.append(f"`{base_md}`: unknown category `{category}`. Add it to USER_GROUPS in classify.py.")
            continue
        head_text = read(head, base_md)
        if head_text is not None:
            # SKILL.md still exists: an update.
            if not any(s.head_path == base_md for s in skills):
                _append(skills, skipped, (category, plugin, folder), base_md, base_md, head_text, read(base, base_md), False)
            continue
        base_text = read(base, base_md)
        if base_text is None:
            continue
        try:
            base_fm = parse_frontmatter(base_text)
        except FrontmatterError as error:
            skipped.append(f"`{base_md}` (removed): {error}. The row, if any, was left alone.")
            continue
        twin = next((s for s in skills if s.mode == "new" and s.name == base_fm.name), None)
        if twin is not None:
            twin.mode = "rename"
            twin.base_path = base_md
            twin.base_name = base_fm.name
            twin.base_description = base_fm.description
            continue
        skills.append(
            SkillChange(
                name=base_fm.name,
                mode="removed",
                category=category,
                plugin=plugin,
                folder=folder,
                head_path=None,
                base_path=base_md,
                base_name=base_fm.name,
                base_description=base_fm.description,
            )
        )

    skills.sort(key=lambda s: s.name)
    page_id = notion_page_id(body)
    named = skill_name_line(body)
    if page_id and named:
        for skill in skills:
            if named in (skill.name, skill.base_name):
                skill.notion_id = page_id
                break
    ticked = ticked_boxes(body)
    ticked_modes = {CHECKBOX_MODES[label] for label in ticked if label in CHECKBOX_MODES}
    if ticked_modes:
        boxes = " and ".join(f"'{label}'" for label in ticked if label in CHECKBOX_MODES)
        for skill in skills:
            if skill.mode not in ticked_modes:
                skill.warnings.append(
                    f"You ticked {boxes}, but this pull request {describe_mode(skill.mode)}. The diff decides."
                )
    return Plan(
        skills=skills,
        notion_id=page_id,
        notion_line=notion_line(body),
        skill_name=named,
        ticked=ticked,
        skipped=skipped,
    )


def _append(
    skills: list[SkillChange],
    skipped: list[str],
    key: SkillKey,
    head_path: str,
    base_path: str,
    head_text: str,
    base_text: str | None,
    moved: bool,
):
    try:
        fm = parse_frontmatter(head_text)
    except FrontmatterError as error:
        skipped.append(f"`{head_path}`: {error}. Fix the frontmatter and push again.")
        return
    warnings = list[str]()
    base_fm = _read_base(base_text, base_path, warnings)
    category, plugin, folder = key
    mode: Mode = "new" if base_text is None else "rename" if moved else "update"
    skills.append(
        SkillChange(
            name=fm.name,
            mode=mode,
            category=category,
            plugin=plugin,
            folder=folder,
            head_path=head_path,
            base_path=None if base_text is None else base_path,
            description=fm.description,
            base_name=base_fm.name if base_fm else None,
            base_description=base_fm.description if base_fm else None,
            warnings=warnings,
        )
    )


def _read_base(text: str | None, path: str, warnings: list[str]):
    if text is None:
        return None
    try:
        return parse_frontmatter(text)
    except FrontmatterError as error:
        warnings.append(f"The frontmatter at `{path}` before this pull request could not be read ({error}), so the old name is unknown.")
        return None

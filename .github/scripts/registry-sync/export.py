"""Publish the skill registry as telemetry: one Logfire log record per skill, per snapshot.

The Notion sync keeps people informed; this keeps Logfire informed. The dashboard in the
``claude-telemtery`` project joins ``skill_activated`` events to the newest snapshot to decide
whether a skill is Casper's. Nothing here is typed by hand: the rows come from the same
``repo_skills`` walk the reconcile uses.

Records are sent as OTLP/HTTP JSON with the standard library only, so the locked script
dependencies do not change and the sender can be tested with a fake transport.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal, Protocol

from classify import USER_GROUPS
from reconcile import repo_skills
from registry import MARKETPLACES

SERVICE_NAME = "casper-skill-registry"
SCOPE_NAME = "casper.skill_registry"
DEFAULT_BASE_URL = "https://logfire-us.pydantic.dev"
LOGS_PATH = "/v1/logs"

# Bare skill names that are too generic to attribute when they arrive without a plugin name.
AMBIGUOUS_NAMES = frozenset({"commit", "data-analysis"})

OUTPUT_JSON = "casper-skills.json"

type Kind = Literal["skill", "command"]
type Origin = Literal["casper", "client"]


@dataclass(frozen=True)
class RegistryRow:
    """One skill or command, as the dashboard needs to see it."""

    snapshot_id: str
    repo: str
    marketplace: str  # the label the Notion registry uses, or the marketplace.json name for client repos
    marketplace_name: str  # .claude-plugin/marketplace.json "name"; what /plugin install uses
    plugin: str
    plugin_version: str | None
    skill: str  # frontmatter name; the folder name when the frontmatter cannot be read
    folder: str
    kind: Kind
    category: str
    user_group: str
    path: str
    origin: Origin
    frontmatter_ok: bool


class Transport(Protocol):
    def post(self, url: str, headers: dict[str, str], payload: bytes) -> int: ...


# --- reading a checkout -------------------------------------------------------------


def marketplace_name(root: Path):
    """The ``name`` in ``.claude-plugin/marketplace.json``; the folder name if there is none."""
    manifest = root / ".claude-plugin" / "marketplace.json"
    try:
        return str(json.loads(manifest.read_text(encoding="utf-8"))["name"])
    except (OSError, ValueError, KeyError, TypeError):
        return root.resolve().name


def plugin_versions(root: Path):
    """``plugin name -> version`` from every ``plugins/*/*/.claude-plugin/plugin.json``."""
    versions = dict[str, str | None]()
    for manifest in sorted(root.glob("plugins/*/*/.claude-plugin/plugin.json")):
        folder = manifest.parent.parent.name
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
            versions[str(data.get("name") or folder)] = data.get("version")
        except (OSError, ValueError):
            versions[folder] = None
    return versions


def client_plugins(root: Path):
    """Plugin names listed in ``telemetry/client-plugins.json``: engagement plugins that live outside the org repos."""
    listing = root / "telemetry" / "client-plugins.json"
    if not listing.exists():
        return list[str]()
    data = json.loads(listing.read_text(encoding="utf-8"))
    return sorted(str(name) for name in data)


def snapshot_id(root: Path):
    """The checkout's commit SHA, or ``unknown`` outside git."""
    try:
        completed = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return completed.stdout.strip() or "unknown"


def build_rows(root: Path, repo: str, snapshot: str):
    """Every skill and command in ``root`` as registry rows, plus the reconcile's skipped notes."""
    label = MARKETPLACES.get(repo)
    name = marketplace_name(root)
    origin: Origin = "casper" if label else "client"
    versions = plugin_versions(root)
    skills, skipped = repo_skills(root)
    rows = list[RegistryRow]()
    for skill in skills:
        rows.append(
            RegistryRow(
                snapshot_id=snapshot,
                repo=repo,
                marketplace=label or name,
                marketplace_name=name,
                plugin=skill.plugin,
                plugin_version=versions.get(skill.plugin),
                skill=skill.name,
                folder=skill.folder,
                kind="skill",
                category=skill.category,
                user_group=skill.user_group,
                path=skill.path,
                origin=origin,
                frontmatter_ok=skill.error is None,
            )
        )
    for md in sorted(root.glob("plugins/*/*/commands/*.md")):
        rel = md.relative_to(root).as_posix()
        category, plugin = md.parts[-4], md.parts[-3]
        rows.append(
            RegistryRow(
                snapshot_id=snapshot,
                repo=repo,
                marketplace=label or name,
                marketplace_name=name,
                plugin=plugin,
                plugin_version=versions.get(plugin),
                skill=md.stem,
                folder=md.stem,
                kind="command",
                category=category,
                user_group=_user_group(category),
                path=rel,
                origin=origin,
                frontmatter_ok=True,
            )
        )
    for plugin in client_plugins(root):
        rows.append(
            RegistryRow(
                snapshot_id=snapshot,
                repo=repo,
                marketplace="client",
                marketplace_name="",
                plugin=plugin,
                plugin_version=None,
                skill="*",
                folder="*",
                kind="skill",
                category="client",
                user_group="Client",
                path="telemetry/client-plugins.json",
                origin="client",
                frontmatter_ok=True,
            )
        )
    rows.sort(key=lambda row: (row.repo, row.plugin, row.kind, row.skill))
    return rows, skipped


def _user_group(category: str):
    return USER_GROUPS.get(category, category)


def ambiguous_names(rows: list[RegistryRow]):
    """Generic names, plus any bare skill name that exists under more than one plugin."""
    owners = dict[str, set[str]]()
    for row in rows:
        if row.skill != "*":
            owners.setdefault(row.skill, set()).add(f"{row.repo}:{row.plugin}")
    return sorted(AMBIGUOUS_NAMES | {name for name, plugins in owners.items() if len(plugins) > 1})


# --- files ---------------------------------------------------------------------------


def to_json(rows: list[RegistryRow], ambiguous: list[str]):
    """The review copy committed to the repo. The snapshot id is left out so it only changes when skills do."""
    return json.dumps(
        {
            "ambiguous": ambiguous,
            "rows": [{k: v for k, v in asdict(row).items() if k != "snapshot_id"} for row in rows],
        },
        indent=2,
        sort_keys=True,
    ) + "\n"


def write_json(rows: list[RegistryRow], ambiguous: list[str], out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / OUTPUT_JSON
    target.write_text(to_json(rows, ambiguous), encoding="utf-8")
    return target


def check_json(rows: list[RegistryRow], ambiguous: list[str], out_dir: Path):
    """``None`` when the committed file matches; otherwise what to do about it."""
    target = out_dir / OUTPUT_JSON
    expected = to_json(rows, ambiguous)
    try:
        current = target.read_text(encoding="utf-8")
    except OSError:
        return f"`{target}` is missing. Run `sync.py export` and commit the result."
    if current != expected:
        return f"`{target}` is out of date. Run `sync.py export` and commit the result."
    return None


# --- sending -------------------------------------------------------------------------


def _attr(key: str, value: object):
    if isinstance(value, bool):
        return {"key": key, "value": {"boolValue": value}}
    if isinstance(value, int):
        return {"key": key, "value": {"intValue": str(value)}}
    return {"key": key, "value": {"stringValue": "" if value is None else str(value)}}


def _record(body: str, attributes: dict[str, object], now_ns: int):
    return {
        "timeUnixNano": str(now_ns),
        "observedTimeUnixNano": str(now_ns),
        "severityNumber": 9,
        "severityText": "INFO",
        "body": {"stringValue": body},
        "attributes": [_attr(k, v) for k, v in attributes.items()],
    }


def payload(rows: list[RegistryRow], ambiguous: list[str], snapshot: str, repo: str, now_ns: int | None = None):
    """The OTLP/HTTP JSON body: one ``registry.skill`` record per row, one per ambiguous name, one snapshot summary."""
    now_ns = now_ns or time.time_ns()
    records = [_record("registry.skill", {f"registry.{k}": v for k, v in asdict(row).items()}, now_ns) for row in rows]
    records += [_record("registry.ambiguous", {"registry.snapshot_id": snapshot, "registry.repo": repo, "registry.skill": name}, now_ns) for name in ambiguous]
    records.append(
        _record(
            "registry.snapshot",
            {
                "registry.snapshot_id": snapshot,
                "registry.repo": repo,
                "registry.rows": len(rows),
                "registry.skills": sum(1 for r in rows if r.kind == "skill" and r.skill != "*"),
                "registry.commands": sum(1 for r in rows if r.kind == "command"),
                "registry.client_plugins": sum(1 for r in rows if r.skill == "*"),
                "registry.ambiguous": len(ambiguous),
            },
            now_ns,
        )
    )
    return {
        "resourceLogs": [
            {
                "resource": {
                    "attributes": [
                        _attr("service.name", SERVICE_NAME),
                        _attr("service.version", snapshot[:12]),
                        _attr("registry.repo", repo),
                    ]
                },
                "scopeLogs": [{"scope": {"name": SCOPE_NAME}, "logRecords": records}],
            }
        ]
    }


class UrllibTransport:
    def post(self, url: str, headers: dict[str, str], payload: bytes):
        request = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return int(response.status)
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", "replace")[:300]
            raise SystemExit(f"Logfire rejected the registry ({error.code}): {detail}") from None
        except urllib.error.URLError as error:
            raise SystemExit(f"Logfire could not be reached: {error.reason}") from None


def send(body: dict[str, object], token: str, base_url: str, transport: Transport):
    url = base_url.rstrip("/") + LOGS_PATH
    headers = {"Authorization": token, "Content-Type": "application/json", "User-Agent": "casper-registry-sync"}
    return transport.post(url, headers, json.dumps(body).encode("utf-8"))


def base_url_from_env(env: dict[str, str]):
    return env.get("LOGFIRE_BASE_URL") or DEFAULT_BASE_URL

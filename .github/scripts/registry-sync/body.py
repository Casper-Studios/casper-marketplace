"""The page body written to a new registry row: the documentation headings, empty."""

from __future__ import annotations

HEADINGS = [
    ("heading_2", "Why it’s useful"),
    ("heading_2", "Samples this skill produces"),
    ("heading_2", "Use this skill when"),
    ("heading_2", "How to use it"),
    ("heading_3", "Inputs"),
    ("heading_2", "What happens behind the scenes"),
    ("heading_2", "Tips for better results"),
    ("heading_2", "Limitations and access"),
    ("heading_2", "Related skills"),
]


def template(name: str, repo: str, skill_md_path: str):
    """Blocks for one skill: how to install, the headings, and a link to its SKILL.md."""
    blocks = [
        _heading("heading_2", "How to Install"),
        _code(f"npx skills add https://github.com/{repo} --skill {name}"),
    ]
    blocks += [_heading(kind, text) for kind, text in HEADINGS]
    blocks += [
        _heading("heading_2", "Source"),
        _link("View the skill’s SKILL.md", f"https://github.com/{repo}/blob/main/{skill_md_path}"),
    ]
    return blocks


def _text(content: str, url: str | None = None) -> dict[str, object]:
    text: dict[str, object] = {"content": content}
    if url:
        text["link"] = {"url": url}
    return {"type": "text", "text": text}


def _heading(kind: str, text: str) -> dict[str, object]:
    return {"object": "block", "type": kind, kind: {"rich_text": [_text(text)]}}


def _code(command: str) -> dict[str, object]:
    return {"object": "block", "type": "code", "code": {"rich_text": [_text(command)], "language": "bash"}}


def _link(label: str, url: str) -> dict[str, object]:
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [_text(label, url)]}}

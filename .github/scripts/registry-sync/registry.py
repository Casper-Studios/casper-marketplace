"""What the sync knows about one registry row, and what it needs from Notion."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import notion
from notion import Page

DATA_SOURCE_ID = "39ce373e-28c6-806c-a81c-000b11e50a5a"
DEFAULT_REPO = "Casper-Studios/casper-secret-sauce"

# Repository to the Marketplace option its rows carry.
MARKETPLACES = {
    "Casper-Studios/casper-secret-sauce": "Secret Sauce",
    "Casper-Studios/casper-marketplace": "Public Marketplace",
}

NEW_STATUS = "Needs Documentation"
REVIEW_STATUS = "For Review"
MERGED_STATUS = "Beta"
DEPRECATED_STATUS = "Deprecated"
LEAVE_ALONE = {REVIEW_STATUS, NEW_STATUS}


def marketplace_for(repo: str):
    try:
        return MARKETPLACES[repo]
    except KeyError:
        known = ", ".join(MARKETPLACES)
        raise SystemExit(f"{repo} is not a repository the sync knows. Known: {known}.") from None


@dataclass
class Row:
    id: str
    url: str
    status: str | None
    name: str
    marketplace: str | None = None
    plugin: str | None = None
    user_group: str | None = None


def row_from(page: Page):
    return Row(
        id=page.id,
        url=page.link,
        status=page.status,
        name=page.title,
        marketplace=page.marketplace,
        plugin=page.plugin,
        user_group=page.user_group,
    )


class Ambiguous(Exception):
    """Two or more registry rows share one name. A person has to merge them."""


class Registry(Protocol):
    """What the sync needs from Notion."""

    dry_run: bool

    def get_page(self, page_id: str) -> Page | None: ...
    def query_by_name(self, data_source_id: str, name: str) -> list[Page]: ...
    def query_all(self, data_source_id: str) -> list[Page]: ...
    def find_user(self, display_name: str | None) -> str | None: ...
    def create_page(self, data_source_id: str, properties: dict[str, object]) -> Page: ...
    def update_page(self, page_id: str, properties: dict[str, object]) -> Page: ...
    def has_content(self, page_id: str) -> bool: ...
    def append_blocks(self, page_id: str, blocks: list[dict[str, object]]) -> None: ...


def new_row_properties(
    name: str,
    description: str,
    status_name: str,
    marketplace: str,
    user_group: str,
    plugin: str,
    owner_id: str | None,
):
    props: dict[str, object] = {
        "Name": notion.title(name),
        "Description": notion.rich_text(description),
        "Status": notion.status(status_name),
        "Marketplace": notion.select(marketplace),
        "User Group": notion.select(user_group),
        "Plugin": notion.select(plugin),
    }
    if owner_id:
        props["Owner"] = notion.people(owner_id)
    return props


def find_by_name(api: Registry, data_source_id: str, names: list[str]):
    """The one row named by the first name that matches. None if no name matches."""
    for name in names:
        pages = api.query_by_name(data_source_id, name)
        if len(pages) > 1:
            raise Ambiguous(f"Two or more registry rows are named `{name}`. Merge them into one by hand, then re-run the sync.")
        if pages:
            return row_from(pages[0])
    return None

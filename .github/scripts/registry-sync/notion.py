"""Notion REST client: auth, retries, dry run.

Reads always go out. With ``dry_run`` set, writes print the method, URL and
body and send nothing.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field, ValidationError

API = "https://api.notion.com"
VERSION = "2026-03-11"
MAX_TRIES = 6
TEXT_CHUNK = 2000  # Notion limit per rich text object
DRY_RUN_ID = "00000000-0000-0000-0000-000000000000"


class NotionError(Exception):
    def __init__(self, status: int | None, message: str):
        super().__init__(f"Notion {status or 'request'} failed: {message}")
        self.status = status
        self.message = message


def normalize_id(value: str):
    return value.replace("-", "").lower()


# --- response shapes ---


class Loose(BaseModel):
    model_config = ConfigDict(extra="ignore")


class ErrorPayload(Loose):
    message: str | None = None


class Named(Loose):
    name: str


class TextPart(Loose):
    plain_text: str = ""


class TitleProperty(Loose):
    title: list[TextPart] = []


class StatusProperty(Loose):
    status: Named | None = None


class SelectProperty(Loose):
    select: Named | None = None


class PageProperties(Loose):
    name: TitleProperty = Field(default_factory=TitleProperty, alias="Name")
    status: StatusProperty = Field(default_factory=StatusProperty, alias="Status")
    marketplace: SelectProperty = Field(default_factory=SelectProperty, alias="Marketplace")
    plugin: SelectProperty = Field(default_factory=SelectProperty, alias="Plugin")
    user_group: SelectProperty = Field(default_factory=SelectProperty, alias="User Group")


class Parent(Loose):
    data_source_id: str | None = None
    database_id: str | None = None


class Page(Loose):
    id: str
    url: str | None = None
    archived: bool = False
    in_trash: bool = False
    parent: Parent = Field(default_factory=Parent)
    properties: PageProperties = Field(default_factory=PageProperties)

    @property
    def title(self):
        return "".join(part.plain_text for part in self.properties.name.title)

    @property
    def status(self):
        return self.properties.status.status.name if self.properties.status.status else None

    @property
    def marketplace(self):
        return self.properties.marketplace.select.name if self.properties.marketplace.select else None

    @property
    def plugin(self):
        return self.properties.plugin.select.name if self.properties.plugin.select else None

    @property
    def user_group(self):
        return self.properties.user_group.select.name if self.properties.user_group.select else None

    @property
    def parent_id(self):
        value = self.parent.data_source_id or self.parent.database_id
        return normalize_id(value) if value else None

    @property
    def link(self):
        return self.url or f"https://www.notion.so/{normalize_id(self.id)}"


class QueryResult(Loose):
    results: list[Page] = []
    has_more: bool = False
    next_cursor: str | None = None


class BlockList(Loose):
    results: list[dict[str, object]] = []


class User(Loose):
    id: str
    type: str | None = None
    name: str | None = None


class UserList(Loose):
    results: list[User] = []
    has_more: bool = False
    next_cursor: str | None = None


class Response(Protocol):
    """What ``urlopen`` returns."""

    status: int

    def read(self) -> bytes: ...
    def __enter__(self) -> Response: ...
    def __exit__(self, *args: object) -> bool | None: ...


class Transport(Protocol):
    def __call__(self, request: urllib.request.Request, /, *, timeout: float) -> Response: ...


class Readable(Protocol):
    def read(self) -> bytes: ...


class Notion:
    def __init__(
        self,
        token: str,
        dry_run: bool = False,
        opener: Transport = urllib.request.urlopen,
        sleep: Callable[[float], None] = time.sleep,
        log: Callable[[str], None] = print,
    ):
        if not token:
            raise NotionError(None, "NOTION_TOKEN is not set")
        self.token = token
        self.dry_run = dry_run
        self.opener = opener
        self.sleep = sleep
        self.log = log

    # --- transport ---

    def request(self, method: str, path: str, body: dict[str, object] | None = None):
        """Send one request. Retries on 429, 5xx and network errors."""
        url = API + path
        data = json.dumps(body).encode("utf-8") if body is not None else None
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": VERSION,
            "Content-Type": "application/json",
        }
        last = "no attempts made"
        for attempt in range(MAX_TRIES):
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            try:
                with self.opener(req, timeout=30) as resp:
                    return resp.status, _read_json(resp)
            except urllib.error.HTTPError as error:
                payload = _read_json(error)
                if error.code == 429 or error.code >= 500:
                    last = f"{error.code} {_message(payload)}".strip()
                    self.sleep(_retry_after(error.headers.get("Retry-After"), attempt))
                    continue
                return error.code, payload
            except (urllib.error.URLError, TimeoutError, OSError) as error:
                last = str(error)
                self.sleep(_retry_after(None, attempt))
        raise NotionError(None, f"gave up after {MAX_TRIES} tries on {method} {path}: {last}")

    def _write(self, method: str, path: str, body: dict[str, object]):
        if self.dry_run:
            self.log(f"DRY RUN {method} {API}{path}")
            self.log(json.dumps(body, indent=2, ensure_ascii=False))
            return Page(id=DRY_RUN_ID)
        status, payload = self.request(method, path, body)
        if status >= 400:
            raise NotionError(status, f"{method} {path}: {_message(payload)}")
        return _validate(Page, payload, f"{method} {path}")

    # --- reads ---

    def get_page(self, page_id: str):
        path = f"/v1/pages/{normalize_id(page_id)}"
        status, payload = self.request("GET", path)
        if status == 404:
            return None
        if status >= 400:
            raise NotionError(status, f"GET {path}: {_message(payload)}")
        return _validate(Page, payload, f"GET {path}")

    def query_by_name(self, data_source_id: str, name: str):
        body: dict[str, object] = {"filter": {"property": "Name", "title": {"equals": name}}}
        return self._query(data_source_id, body).results

    def query_all(self, data_source_id: str):
        """Every row, in pages of 100."""
        pages = list[Page]()
        cursor = None
        while True:
            body: dict[str, object] = {"page_size": 100}
            if cursor:
                body["start_cursor"] = cursor
            result = self._query(data_source_id, body)
            pages.extend(result.results)
            if not result.has_more or not result.next_cursor:
                return pages
            cursor = result.next_cursor

    def _query(self, data_source_id: str, body: dict[str, object]):
        path = f"/v1/data_sources/{data_source_id}/query"
        status, payload = self.request("POST", path, body)
        if status == 404:
            raise NotionError(
                404,
                f"data source {data_source_id} was not found. Connect the registry-sync "
                "connection to the Skill Registry database in Notion.",
            )
        if status >= 400:
            raise NotionError(status, f"POST {path}: {_message(payload)}")
        return _validate(QueryResult, payload, f"POST {path}")

    def has_content(self, page_id: str):
        """True if the page body has at least one block."""
        path = f"/v1/blocks/{normalize_id(page_id)}/children?page_size=1"
        status, payload = self.request("GET", path)
        if status >= 400:
            raise NotionError(status, f"GET {path}: {_message(payload)}")
        return bool(_validate(BlockList, payload, f"GET {path}").results)

    def list_users(self):
        users = list[User]()
        cursor = None
        while True:
            path = "/v1/users?page_size=100" + (f"&start_cursor={cursor}" if cursor else "")
            status, payload = self.request("GET", path)
            if status >= 400:
                raise NotionError(status, f"GET /v1/users: {_message(payload)}")
            page = _validate(UserList, payload, "GET /v1/users")
            users.extend(page.results)
            if not page.has_more or not page.next_cursor:
                return users
            cursor = page.next_cursor

    def find_user(self, display_name: str | None):
        """The one person with this display name, case-insensitive. None if zero or several."""
        if display_name is None or not display_name.strip():
            return None
        wanted = display_name.strip().casefold()
        hits = [
            user.id
            for user in self.list_users()
            if user.type == "person" and user.name is not None and user.name.strip().casefold() == wanted
        ]
        return hits[0] if len(hits) == 1 else None

    # --- writes ---

    def create_page(self, data_source_id: str, properties: dict[str, object]):
        body: dict[str, object] = {
            "parent": {"type": "data_source_id", "data_source_id": data_source_id},
            "properties": properties,
        }
        return self._write("POST", "/v1/pages", body)

    def update_page(self, page_id: str, properties: dict[str, object]):
        return self._write("PATCH", f"/v1/pages/{normalize_id(page_id)}", {"properties": properties})

    def append_blocks(self, page_id: str, blocks: list[dict[str, object]]):
        """Add blocks to the end of a page body."""
        path = f"/v1/blocks/{normalize_id(page_id)}/children"
        body: dict[str, object] = {"children": blocks}
        if self.dry_run:
            self.log(f"DRY RUN PATCH {API}{path}")
            self.log(json.dumps(body, indent=2, ensure_ascii=False))
            return
        status, payload = self.request("PATCH", path, body)
        if status >= 400:
            raise NotionError(status, f"PATCH {path}: {_message(payload)}")


# --- property shapes ---


def title(text: str) -> dict[str, object]:
    return {"title": _chunks(text)}


def rich_text(text: str) -> dict[str, object]:
    return {"rich_text": _chunks(text)}


def status(name: str) -> dict[str, object]:
    return {"status": {"name": name}}


def clear_status() -> dict[str, object]:
    return {"status": None}


def select(name: str) -> dict[str, object]:
    return {"select": {"name": name}}


def people(user_id: str) -> dict[str, object]:
    return {"people": [{"object": "user", "id": user_id}]}


def _chunks(text: str):
    return [{"text": {"content": text[i : i + TEXT_CHUNK]}} for i in range(0, max(len(text), 1), TEXT_CHUNK)]


# --- helpers ---


def _validate[T: BaseModel](model: type[T], payload: dict[str, object], where: str):
    try:
        return model.model_validate(payload)
    except ValidationError as error:
        raise NotionError(None, f"{where} returned an unexpected shape: {error.error_count()} problems") from error


def _message(payload: dict[str, object]):
    try:
        return ErrorPayload.model_validate(payload).message or ""
    except ValidationError:
        return ""


def _read_json(response: Readable) -> dict[str, object]:
    try:
        raw = response.read()
    except OSError:
        return {}
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except ValueError:
        return {"message": raw.decode("utf-8", "replace")[:200]}
    return data if isinstance(data, dict) else {}


def _retry_after(header: str | None, attempt: int):
    if header:
        try:
            return max(float(header), 0.0)
        except ValueError:
            pass
    return float(2**attempt)

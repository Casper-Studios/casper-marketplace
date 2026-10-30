# Yield Async Pages Lazily

Use an async generator when a remote API paginates.

```python
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class InvoicePage:
    items: list[str]
    next_cursor: str | None


# BAD: the transport layer forces every consumer to fetch every page.
async def fetch_all_pages(fetch_page: Callable[[str | None], Awaitable[InvoicePage]]):
    pages: list[InvoicePage] = []
    cursor: str | None = None
    while True:
        page = await fetch_page(cursor)
        pages.append(page)
        if page.next_cursor is None:
            return pages
        cursor = page.next_cursor


# GOOD: consumers choose whether to stop, flatten, or retain page boundaries.
async def iter_pages(
    fetch_page: Callable[[str | None], Awaitable[InvoicePage]],
) -> AsyncIterator[InvoicePage]:
    cursor: str | None = None
    while True:
        page = await fetch_page(cursor)
        yield page

        if page.next_cursor is None:
            return
        cursor = page.next_cursor
```

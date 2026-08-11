# Own Async Resource Lifetimes

Expose an async context manager when a resource needs cleanup. Construct a fully valid resource before yielding it, and release it in the same scope that acquired it.

```python
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import httpx


# BAD: this object can escape before it is valid and relies on manual cleanup.
class ApiClientManager:
    client: httpx.AsyncClient | None = None

    async def init(self):
        self.client = httpx.AsyncClient(base_url="https://api.example.com")

    async def close(self):
        if self.client is not None:
            await self.client.aclose()


# GOOD: a yielded client is immediately valid and cleanup has one owner.
@asynccontextmanager
async def open_api_client() -> AsyncGenerator[httpx.AsyncClient]:
    async with httpx.AsyncClient(base_url="https://api.example.com") as client:
        yield client
```

Do not expose a manager that requires a later `init`, setter, or activation call. Close dependent resources before their dependencies by nesting contexts in acquisition order.

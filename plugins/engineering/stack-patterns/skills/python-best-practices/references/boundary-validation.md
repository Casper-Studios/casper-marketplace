# Validate Serialized Boundaries

Treat JSON, HTTP bodies, webhooks, TOML, environment-derived structured values, and untyped database JSON as untrusted. Parse them once at the first controlled boundary, then pass typed internal values onward.

```python
import json

from pydantic import BaseModel


class WebhookEvent(BaseModel):
    event_id: str
    kind: str


# BAD: untrusted decoded data leaks into the application as a mapping.
def decode_event_unvalidated(body: bytes):
    return json.loads(body)


# GOOD: validate once at the serialized boundary.
def decode_event(body: bytes):
    return WebhookEvent.model_validate_json(body)
```

Authentication does not prove payload shape. Do not return unvalidated `dict[str, object]` from an integration boundary.

# Validate Serialized Boundaries

Validate serialized input into a typed model at the boundary that decodes it. Do not decode it into a mapping first.

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

Do not return unvalidated `dict[str, object]` from an integration boundary.

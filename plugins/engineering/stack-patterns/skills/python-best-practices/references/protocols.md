# Protocols for Behavioral Contracts

Use a `Protocol` when a consumer needs behavior, not a particular concrete class. Keep the protocol limited to the operations the consumer actually invokes.

```python
from typing import Protocol


# BAD: a lower layer depends on a concrete vendor client and its unrelated API.
class SendGridClient:
    async def send(self, recipient: str, body: str): ...


async def notify_with_vendor_client(sender: SendGridClient, recipient: str):
    await sender.send(recipient, "Your report is ready.")


# GOOD: declare only the capability the consumer uses.
class MessageSender(Protocol):
    async def send(self, recipient: str, body: str) -> None: ...


async def notify(sender: MessageSender, recipient: str):
    await sender.send(recipient, "Your report is ready.")
```

Do not accept a vendor client only because it happens to supply `send`. A small protocol prevents a lower layer from depending on unrelated construction, configuration, or vendor APIs.

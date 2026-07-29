# Define Explicit Public Exports

Keep `__init__.py` empty unless it provides a deliberate, inert public API. Use `__all__` in a public module when it clarifies the supported names.

```python
# BAD: importing a package root validates configuration as a side effect.
# acme_mail/__init__.py
from .config import MAIL_API_KEY


# GOOD: the package root stays inert and the public module names its export.
# acme_mail/errors.py
__all__ = ["DeliveryError"]


class DeliveryError(Exception):
    """A provider rejected a delivery request."""
```

Do not import configuration, construct clients, register routers, or validate environment variables from a package root. Consumers should import the explicit owning module, such as `acme_mail.errors`.

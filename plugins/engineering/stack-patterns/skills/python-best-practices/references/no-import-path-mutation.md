# Do Not Mutate Import Paths

Install the project or run it through its package manager. Do not mutate `sys.path`, set `PYTHONPATH`, or execute a source file by path to make imports work.

```python
# BAD: makes checkout layout part of runtime import resolution.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


# GOOD: imports the installed distribution.
from acme_mail.client import MailClient
```

```bash
uv run --package acme-mail python -m acme_mail.sync
```

Path mutation hides missing package metadata and undeclared dependencies. The standard `src` layout plus an installed editable workspace member makes import failures visible before deployment.

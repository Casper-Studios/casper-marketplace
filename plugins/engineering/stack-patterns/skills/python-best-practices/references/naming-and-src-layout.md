# Name Distributions, Packages, and Modules Clearly

Use a distribution name for packaging and a valid identifier for imports. Use the standard `src` layout so tests and tools import the installed distribution instead of the checkout by accident.

```text
acme-mail/ # distribution project
├── pyproject.toml # name = "acme-mail"
└── src/
    └── acme_mail/ # import acme_mail
        └── client.py
```

Use concise lowercase module names with underscores only when needed for readability. `src` is a build-discovery directory, never an import namespace: write `from acme_mail.client import MailClient`, not `from src.acme_mail.client import MailClient`.

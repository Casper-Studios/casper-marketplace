# Executable Scripts

Default the deterministic work to scripts. Delegate parsing, validation, normalization, selection, transformation, file generation, and repeatable checks whenever exact inputs and outputs can be specified. Use model reasoning only when the work requires judgment that cannot be encoded as a deterministic procedure.

Before writing a script, inspect the target repository and runtime for existing helpers and built-in standard-library modules or functions. Prefer those primitives over third-party dependencies and manual reimplementations.

Default the standalone skill scripts to Python because its standard library covers most scripting needs without an installation step. When the script genuinely needs a third-party dependency, declare it with [PEP 723](https://peps.python.org/pep-0723/) inline metadata and lock it with `uv`. For example, use `pydantic` when decoded JSON enters Python as `Any` and must be parsed into a trusted contract:

```shell
uv add --script script.py pydantic
uv lock --script script.py
uv run --locked script.py
```

Commit the adjacent `script.py.lock` with the script. Follow the [`uv` script guide](https://docs.astral.sh/uv/guides/scripts/) for the workflow and [`uv` storage documentation](https://docs.astral.sh/uv/reference/storage/) for its writable cache. uv creates the dedicated script environment in that cache rather than beside the skill, so the packaged script and lockfile can remain on a read-only mount without requiring a mutable `.venv` there.

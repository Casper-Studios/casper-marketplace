# Recursive Ownership

Derive the directory tree from the production import graph. A vertical module is an import-closure container, not a folder that groups related names.

Start with the capability visible to a caller. Place its complete private implementation beneath that capability, including presentation, state, queries, actions, transformations, utilities, and leaf-specific tests. Repeat the same analysis for each child operation.

```text
# BAD: one capability is scattered across global technical layers.
components/
  task-board
hooks/
  use-tasks
schemas/
  task
actions/
  update-task
```

```text
# GOOD: one feature owns the complete capability.
features/
  task-board/
    index
    filter/
      index
      state
      state.test
      query
      action
    edit/
      index
      title/
        index
        form
        mutation
```

The first placement pass puts task-board behavior under one feature. The next pass puts filter-only dependencies under `filter`. The analysis repeats under `edit`, where the title form and mutation belong to the `title` operation. Stop only when no private dependency can move closer to its narrowest production consumer.

Nested directories alone do not establish ownership:

```text
# BAD: child operations exist, but their private dependencies leak into the parent.
task-board/
  index
  query
  action
  filter/
    index
  edit/
    index
```

```text
# GOOD: each child owns the dependencies used only to complete its operation.
task-board/
  index
  filter/
    index
    query
    action
  edit/
    index
```

Keep a small helper in its only consumer. Extract a private utility when it owns meaningful sans-I/O behavior and needs a focused colocated test, even with one production consumer. This does not make the utility shared.

A directory requires an owned operation or concept with a deliberate boundary. Do not create a directory only to collect files with common prefixes. Name operation-owning subsystems with verbs and domain concepts or infrastructure with nouns when the repository convention permits that distinction.

Technical top-level modules remain valid for genuinely shared infrastructure, external protocols, persistence, and framework runtime boundaries. Do not force feature colocation across separate languages, deployments, packages, or processes.

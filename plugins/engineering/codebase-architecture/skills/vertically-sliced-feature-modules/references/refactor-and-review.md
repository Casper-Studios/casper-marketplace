# Refactor and Review

Write the intended ownership tree before moving files. Every directory must have a named owner, entry point, consumer set, and dependency direction.

Use this placement test:

- Which capability changes when this code changes?
- Which entry point imports and composes it?
- Does another feature consume the same stable behavior today?
- Can callers target a public capability instead of a private leaf?
- Does the placement reduce navigation and unrelated coupling?
- Does a separate package insulate a real dependency or runtime closure?

Move existing files instead of recreating them. Preserve behavior, tests, public contracts, resource ownership, and framework entry points while changing structure. Delete obsolete paths only after import and test discovery proves that no consumer remains.

Reject these review smells:

- One feature requires edits across distant technical-layer directories.
- A route or registry contains reusable business behavior.
- A shared module has only one real consumer.
- A feature imports another feature.
- Sibling implementation folders have no owning entry point.
- Internal code imports its own module's entry point.
- A package exists only to mirror a feature folder.
- Tests live far from the behavior they protect.

# Refactor and Review

Analyze ownership to a fixed point before declaring a structural refactor complete.

1. Inventory production imports and existing build, runtime, and framework boundaries.
2. Identify the complete operation exposed to each external consumer.
3. Record every file's direct production consumers.
4. Move exclusive dependencies beneath their narrowest consumer.
5. Place multi-consumer dependencies at their lowest common owning ancestor.
6. Repeat steps 2 through 5 inside every newly formed subsystem.
7. Verify that external callers import operational entries and do not bypass them for private leaves.
8. Stop when another analysis pass produces no ownership move.

Write the intended ownership tree before moving files. Every directory must have a named owner, an operation or concept, an entry when external callers need one, a consumer set, and a dependency direction.

Move existing files instead of recreating them. Preserve behavior, tests, public contracts, resource ownership, and framework entry points while changing structure. Delete obsolete paths only after import and test discovery proves that no consumer remains. Do not redesign business behavior under cover of a structural move.

Keep meaningful tests with the behavior they protect. Do not treat a test caller as a reason to promote production code.

Audit the final import graph, not only the directory tree. Reject these conditions:

- One capability requires edits across distant technical-role directories.
- Files with a common prefix imitate a subsystem without owning an operation.
- A child operation's private action, query, state, view, or utility leaks into its parent or sibling.
- A child imports an ancestor-private or sibling-private implementation file.
- A route or registry contains reusable business behavior.
- A feature imports another feature.
- A broadly shared module has one real production consumer.
- A subsystem has no operational entry, or its entry only re-exports implementation leaves.
- Internal code imports its own entry or module root.
- A package exists only to mirror a feature directory.
- Tests live outside the narrowest owner of the behavior they protect.

Run the repository's normal static checks and relevant tests after moving files. Search for retired import paths and direct external imports of private leaves. Tooling can prove that imports resolve; the ownership audit must still prove that they point in the correct direction.

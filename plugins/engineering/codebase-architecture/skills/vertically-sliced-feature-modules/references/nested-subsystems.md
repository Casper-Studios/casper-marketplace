# Nested Subsystems

Prefer a deeper owned hierarchy over a broad sibling namespace when only one parent consumes the subsystem.

```text
# BAD: prefixes simulate ownership in one flat directory.
timeline/
  registration-drawer
  registration-drawer-loader
  registration-drawer-content
  registration-drawer-table

# GOOD: the capability owns its private leaves.
timeline/
  registration/
    draftees-drawer/
      index
      loader
      content
      table
```

Use the nested entry to own trigger composition, state, and private children. Keep query loading behind the on-demand surface when the child should exist only while a dialog, drawer, tab, or comparable capability is active.

Parent modules can select among child phases or protocol variants. Children can import downward or sideways within their subtree, but must not traverse upward into parent internals.

When two siblings need the same concept, first ask whether their parent domain owns it. Promote it beyond the parent only when consumers outside that subtree require the same stable behavior.

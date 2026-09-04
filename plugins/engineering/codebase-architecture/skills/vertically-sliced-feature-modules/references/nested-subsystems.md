# Nested Subsystems

Prefer a deeper owned hierarchy over a broad sibling namespace when one parent consumes the subsystem. Keep its complete private implementation closure under that owner.

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

Use the nested entry to own the complete operation: trigger composition, state, and private children. Keep query loading behind the on-demand surface when the child should exist only while a dialog, drawer, tab, or comparable capability is active.

Keep a small helper with the file that has one consumer. Extract a private utility when it owns meaningful sans-I/O behavior and needs a focused colocated test, even with one production consumer. Keep the utility and test inside the nearest subsystem; a directory still requires a genuine multi-file module with a deliberate owner.

Parent modules can select among child phases or protocol variants. Children can import downward or sideways within their subtree, but must not traverse upward into parent internals.

When two siblings need the same concept, first ask whether their parent domain owns it. Promote it beyond the parent only when consumers outside that subtree require the same stable behavior.

# Plugin Structure

Expose one public skill or several independently useful public skills. Shared collection, normalization, validation, rendering, and other implementation capabilities remain private skills with `user-invocable: false`.

Public skills own consumer-facing outcomes. Private skills own reusable implementation details. A public skill coordinates private capabilities without requiring consumers to understand or invoke the internal stages.

Do not expose a private stage merely because it is implemented as a skill. Promote it only when consumers can request it as a coherent capability of its own.

Keep skill directories as flat siblings under the plugin's skill root. Visibility and responsibility establish the boundary; directory depth does not.

```text
# BAD: consumers must understand and invoke implementation stages.
skills/
├── collect-email-context/
├── classify-email-priority/
├── write-email-digest/
└── render-email-digest/

# GOOD: the plugin exposes its consumer capability and hides shared details.
skills/
├── compile-morning-emails/  # Public entry point
├── collect-email-context/   # user-invocable: false
├── classify-email-priority/ # user-invocable: false
├── write-email-digest/      # user-invocable: false
└── render-email-digest/     # user-invocable: false
```

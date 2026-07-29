# Schema Defaults

Use a schema default only when the domain contract assigns that exact meaning to an absent value.

A default belongs in the schema when absence itself has a defined domain meaning. Do not use a default to reinterpret malformed input or avoid handling a validation failure.

# Do Not Fabricate Defaults

Do not use `or` to supply a value for missing required data. `or` replaces every falsy operand, so it also overwrites valid values such as `0`, `False`, and `""`.

```python
# BAD: changes missing data into a misleading valid-looking value.
def email_receipt_with_default(email: str | None):
    send_email(email or "")


# GOOD: the owning operation rejects absence explicitly.
def email_receipt(email: str | None):
    if email is None:
        raise ValueError("A receipt requires an email address.")

    send_email(email)
```

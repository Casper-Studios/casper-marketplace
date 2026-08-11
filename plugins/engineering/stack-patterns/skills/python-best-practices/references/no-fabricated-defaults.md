# Do Not Fabricate Defaults

Do not replace missing required data with an invented value solely to satisfy a type checker. Preserve absence or raise at the operation boundary.

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

An empty address changes the meaning of the failure and sends an invalid value into another layer.

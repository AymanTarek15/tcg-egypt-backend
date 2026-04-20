import hashlib
import hmac
from typing import Any

from django.conf import settings


def _stringify(value: Any) -> str:
    if value is None:
        return ""

    if isinstance(value, bool):
        return "true" if value else "false"

    return str(value)


def _get_nested(data: dict, *keys: str) -> Any:
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def verify_paymob_hmac(payload: dict) -> bool:
    """
    Verifies Paymob transaction processed callback HMAC.

    Expected shape:
    {
        "type": "...",
        "obj": { ... transaction data ... },
        "hmac": "..."
    }

    Note:
    - This implementation targets the transaction callback / processed callback shape.
    - Paymob's docs say to concatenate the callback values in the documented order
      and hash with SHA-512 using your HMAC secret. The exact callback fields depend
      on the callback type. This list matches the transaction callback fields commonly
      used in Paymob transaction callbacks.
    """
    received_hmac = payload.get("hmac")
    obj = payload.get("obj", {})

    if not received_hmac or not isinstance(obj, dict):
        return False

    # Transaction callback field order
    fields = [
        _get_nested(obj, "amount_cents"),
        _get_nested(obj, "created_at"),
        _get_nested(obj, "currency"),
        _get_nested(obj, "error_occured"),
        _get_nested(obj, "has_parent_transaction"),
        _get_nested(obj, "id"),
        _get_nested(obj, "integration_id"),
        _get_nested(obj, "is_3d_secure"),
        _get_nested(obj, "is_auth"),
        _get_nested(obj, "is_capture"),
        _get_nested(obj, "is_refunded"),
        _get_nested(obj, "is_standalone_payment"),
        _get_nested(obj, "is_voided"),
        _get_nested(obj, "order", "id"),
        _get_nested(obj, "owner"),
        _get_nested(obj, "pending"),
        _get_nested(obj, "source_data", "pan"),
        _get_nested(obj, "source_data", "sub_type"),
        _get_nested(obj, "source_data", "type"),
        _get_nested(obj, "success"),
    ]

    concatenated = "".join(_stringify(value) for value in fields)

    calculated_hmac = hmac.new(
        key=settings.PAYMOB_HMAC_SECRET.encode("utf-8"),
        msg=concatenated.encode("utf-8"),
        digestmod=hashlib.sha512,
    ).hexdigest()

    return hmac.compare_digest(calculated_hmac, str(received_hmac))
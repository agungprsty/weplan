"""Central enums — single source for activity & domains.

StrEnum keeps DB string compatible while giving type-safety.
"""

from __future__ import annotations

from enum import StrEnum


class ActivityAction(StrEnum):
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    STATUS_CHANGED = "status_changed"
    AUTO_GENERATED = "auto_generated"


class EntityType(StrEnum):
    WEDDING = "wedding"
    GUEST = "guest"
    GIFT = "gift"
    CHECKLIST = "checklist"
    VENDOR = "vendor"
    KUA_DOCUMENT = "kua_document"
    MAHAR_ITEM = "mahar_item"
    CORTAGE = "cortage"
    TRANSACTION = "transaction"
    SAVINGS_TARGET = "savings_target"
    ORDER = "order"
    # backwards compat
    BRIDESMAID = "bridesmaid"

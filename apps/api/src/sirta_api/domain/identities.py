from enum import StrEnum


class Role(StrEnum):
    ANALYST = "analyst"
    VALIDATOR = "validator"
    COLLECTOR = "collector"
    TECH_ADMIN = "tech_admin"


FISCAL_ROLES = frozenset({Role.ANALYST, Role.VALIDATOR, Role.COLLECTOR})

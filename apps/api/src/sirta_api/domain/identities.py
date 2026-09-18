from enum import StrEnum


class Role(StrEnum):
    ANALYST = "analyst"
    VALIDATOR = "validator"
    COLLECTOR = "collector"
    DEBT_OFFICER = "debt_officer"
    TECH_ADMIN = "tech_admin"


FISCAL_ROLES = frozenset({Role.ANALYST, Role.VALIDATOR, Role.COLLECTOR, Role.DEBT_OFFICER})

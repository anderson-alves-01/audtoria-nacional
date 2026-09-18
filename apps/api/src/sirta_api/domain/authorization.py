from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sirta_api.domain.errors import ForbiddenError, NotVisibleError
from sirta_api.domain.identities import FISCAL_ROLES, Role


@dataclass(frozen=True)
class AccessContext:
    user_id: UUID
    tenant_id: UUID
    territory_id: UUID
    purpose_id: UUID
    role: Role
    purpose_expires_at: datetime | None
    username: str = ""

    def ensure_purpose_active(self, now: datetime) -> None:
        if self.purpose_expires_at is not None and self.purpose_expires_at <= now:
            raise ForbiddenError("Access purpose is expired")

    def ensure_territory_allowed(self, allowed: set[UUID]) -> None:
        if self.territory_id not in allowed:
            raise ForbiddenError("Territory is not allowed for this user")

    def ensure_fiscal_read(self) -> None:
        if self.role == Role.TECH_ADMIN:
            raise ForbiddenError("Technical administrator cannot access fiscal content")
        if self.role not in FISCAL_ROLES:
            raise ForbiddenError("Insufficient role")

    def ensure_fiscal_write(self) -> None:
        self.ensure_fiscal_read()

    def ensure_same_tenant(self, resource_tenant_id: UUID) -> None:
        if resource_tenant_id != self.tenant_id:
            raise NotVisibleError()

    def ensure_same_territory(self, resource_territory_id: UUID) -> None:
        if resource_territory_id != self.territory_id:
            raise NotVisibleError()

    def ensure_matching_request(
        self, tenant_id: UUID, territory_id: UUID, purpose_id: UUID
    ) -> None:
        if tenant_id != self.tenant_id:
            raise ForbiddenError("Tenant in the request does not match the access context")
        if territory_id != self.territory_id:
            raise ForbiddenError("Territory in the request does not match the access context")
        if purpose_id != self.purpose_id:
            raise ForbiddenError("Access purpose in the request does not match the access context")

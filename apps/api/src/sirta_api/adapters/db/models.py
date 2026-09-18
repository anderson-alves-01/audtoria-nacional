from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(128), nullable=False)


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)


class Territory(Base):
    __tablename__ = "territories"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    subject: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(128), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    territories: Mapped[list[Territory]] = relationship(
        secondary="user_territories",
        lazy="selectin",
    )


class UserTerritory(Base):
    __tablename__ = "user_territories"
    __table_args__ = (UniqueConstraint("user_id", "territory_id"),)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    territory_id: Mapped[UUID] = mapped_column(ForeignKey("territories.id"), primary_key=True)


class AccessPurpose(Base):
    __tablename__ = "access_purposes"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(String(256), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class TaxCredit(Base):
    __tablename__ = "tax_credits"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    territory_id: Mapped[UUID] = mapped_column(ForeignKey("territories.id"), nullable=False)
    purpose_id: Mapped[UUID] = mapped_column(ForeignKey("access_purposes.id"), nullable=False)
    taxpayer_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    tax_type: Mapped[str] = mapped_column(String(16), nullable=False)
    competence: Mapped[str] = mapped_column(String(7), nullable=False)
    source_id: Mapped[str] = mapped_column(String(128), nullable=False)
    principal_amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    additional_amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="BRL")
    calculation_memory: Mapped[str] = mapped_column(Text, nullable=False)
    enforceability_status: Mapped[str] = mapped_column(String(32), nullable=False)
    validation_status: Mapped[str] = mapped_column(String(32), nullable=False, default="IDENTIFIED")
    collection_status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="NOT_STARTED"
    )
    payment_status: Mapped[str] = mapped_column(String(32), nullable=False, default="OPEN")
    version: Mapped[int] = mapped_column(nullable=False, default=1)
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)


class Evidence(Base):
    __tablename__ = "evidences"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    source: Mapped[str] = mapped_column(String(128), nullable=False)
    media_type: Mapped[str] = mapped_column(String(64), nullable=False, default="text/plain")


class TaxCreditEvidence(Base):
    __tablename__ = "tax_credit_evidences"
    __table_args__ = (UniqueConstraint("credit_id", "evidence_id"),)

    credit_id: Mapped[UUID] = mapped_column(ForeignKey("tax_credits.id"), primary_key=True)
    evidence_id: Mapped[UUID] = mapped_column(ForeignKey("evidences.id"), primary_key=True)


class CreditValidation(Base):
    __tablename__ = "credit_validations"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    credit_id: Mapped[UUID] = mapped_column(ForeignKey("tax_credits.id"), nullable=False)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    actor_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    decision: Mapped[str] = mapped_column(String(32), nullable=False)
    checklist_version: Mapped[str] = mapped_column(String(64), nullable=False)
    checklist_items: Mapped[list] = mapped_column(JSONB, nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    resulting_status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class IdempotencyRecord(Base):
    __tablename__ = "idempotency_records"
    __table_args__ = (UniqueConstraint("tenant_id", "key"),)

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    key: Mapped[str] = mapped_column(String(128), nullable=False)
    route: Mapped[str] = mapped_column(String(256), nullable=False)
    request_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    response_body: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class CollectionCase(Base):
    __tablename__ = "collection_cases"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    credit_id: Mapped[UUID] = mapped_column(ForeignKey("tax_credits.id"), nullable=False)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    territory_id: Mapped[UUID] = mapped_column(ForeignKey("territories.id"), nullable=False)
    actor_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="ADMINISTRATIVE")
    sla_due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    timeline: Mapped[list] = mapped_column(JSONB, nullable=False)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    actor_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    territory_id: Mapped[UUID | None] = mapped_column(ForeignKey("territories.id"), nullable=True)
    purpose_id: Mapped[UUID | None] = mapped_column(ForeignKey("access_purposes.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    route: Mapped[str] = mapped_column(String(256), nullable=False)
    outcome: Mapped[str] = mapped_column(String(32), nullable=False)
    resource_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    resource_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)

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


class DataLoadRun(Base):
    __tablename__ = "data_load_runs"
    __table_args__ = (UniqueConstraint("tenant_id", "checksum", "layout_version"),)

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    territory_id: Mapped[UUID] = mapped_column(ForeignKey("territories.id"), nullable=False)
    source_id: Mapped[str] = mapped_column(String(128), nullable=False)
    layout_version: Mapped[str] = mapped_column(String(64), nullable=False)
    competence: Mapped[str] = mapped_column(String(7), nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    received_count: Mapped[int] = mapped_column(Integer, nullable=False)
    silver_count: Mapped[int] = mapped_column(Integer, nullable=False)
    quarantined_count: Mapped[int] = mapped_column(Integer, nullable=False)
    published: Mapped[bool] = mapped_column(nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class DataLoadRow(Base):
    __tablename__ = "data_load_rows"
    __table_args__ = (UniqueConstraint("run_id", "row_id"),)

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    run_id: Mapped[UUID] = mapped_column(ForeignKey("data_load_runs.id"), nullable=False)
    row_id: Mapped[str] = mapped_column(String(64), nullable=False)
    layer: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    reason: Mapped[str | None] = mapped_column(String(256), nullable=True)


class GoldFunnel(Base):
    __tablename__ = "gold_funnels"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    territory_id: Mapped[UUID] = mapped_column(ForeignKey("territories.id"), nullable=False)
    run_id: Mapped[UUID] = mapped_column(ForeignKey("data_load_runs.id"), nullable=False)
    published: Mapped[bool] = mapped_column(nullable=False, default=True)
    identified_count: Mapped[int] = mapped_column(Integer, nullable=False)
    validated_count: Mapped[int] = mapped_column(Integer, nullable=False)
    in_collection_count: Mapped[int] = mapped_column(Integer, nullable=False)
    silver_row_count: Mapped[int] = mapped_column(Integer, nullable=False)
    methodology_version: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class TransferOccurrence(Base):
    __tablename__ = "transfer_occurrences"
    __table_args__ = (
        UniqueConstraint("tenant_id", "transfer_type", "competence", "official_source"),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    territory_id: Mapped[UUID] = mapped_column(ForeignKey("territories.id"), nullable=False)
    transfer_type: Mapped[str] = mapped_column(String(32), nullable=False)
    competence: Mapped[str] = mapped_column(String(7), nullable=False)
    official_source: Mapped[str] = mapped_column(String(128), nullable=False)
    expected_amount: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    received_amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    classification: Mapped[str] = mapped_column(
        String(64), nullable=False, default="OCCURRENCE_NOT_TAX_CREDIT"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class RegulatoryItem(Base):
    __tablename__ = "regulatory_items"
    __table_args__ = (UniqueConstraint("tenant_id", "territory_id", "code"),)

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    territory_id: Mapped[UUID] = mapped_column(ForeignKey("territories.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    source: Mapped[str] = mapped_column(String(256), nullable=False)
    version: Mapped[str] = mapped_column(String(32), nullable=False)
    kind: Mapped[str] = mapped_column(String(32), nullable=False)
    affected_system: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    binding: Mapped[bool] = mapped_column(nullable=False, default=False)
    notes: Mapped[str] = mapped_column(Text, nullable=False)


class SourceRegistry(Base):
    __tablename__ = "source_registry"
    __table_args__ = (UniqueConstraint("tenant_id", "territory_id", "source_id"),)

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    territory_id: Mapped[UUID] = mapped_column(ForeignKey("territories.id"), nullable=False)
    source_id: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    maintainer: Mapped[str] = mapped_column(String(128), nullable=False)
    official_url: Mapped[str] = mapped_column(String(512), nullable=False)
    source_role: Mapped[str] = mapped_column(String(32), nullable=False)
    access_classification: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    purpose: Mapped[str] = mapped_column(String(256), nullable=False)
    legal_basis: Mapped[str] = mapped_column(String(256), nullable=False)
    license_terms: Mapped[str] = mapped_column(String(256), nullable=False)
    layout_version: Mapped[str] = mapped_column(String(64), nullable=False)
    fixture_kind: Mapped[str] = mapped_column(String(32), nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=False)


class GoldEnrichment(Base):
    __tablename__ = "gold_enrichments"
    __table_args__ = (UniqueConstraint("run_id", "source_id"),)

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    territory_id: Mapped[UUID] = mapped_column(ForeignKey("territories.id"), nullable=False)
    run_id: Mapped[UUID] = mapped_column(ForeignKey("data_load_runs.id"), nullable=False)
    source_id: Mapped[str] = mapped_column(String(64), nullable=False)
    source_role: Mapped[str] = mapped_column(String(32), nullable=False)
    published: Mapped[bool] = mapped_column(nullable=False, default=True)
    indicator_count: Mapped[int] = mapped_column(Integer, nullable=False)
    silver_row_count: Mapped[int] = mapped_column(Integer, nullable=False)
    methodology_version: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class GoldOfficial(Base):
    __tablename__ = "gold_officials"
    __table_args__ = (UniqueConstraint("run_id", "indicator"),)

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    territory_id: Mapped[UUID] = mapped_column(ForeignKey("territories.id"), nullable=False)
    run_id: Mapped[UUID] = mapped_column(ForeignKey("data_load_runs.id"), nullable=False)
    source_id: Mapped[str] = mapped_column(String(64), nullable=False)
    source_role: Mapped[str] = mapped_column(String(32), nullable=False)
    dataset: Mapped[str] = mapped_column(String(128), nullable=False)
    maintainer: Mapped[str] = mapped_column(String(128), nullable=False)
    official_url: Mapped[str] = mapped_column(String(512), nullable=False)
    indicator: Mapped[str] = mapped_column(String(128), nullable=False)
    formula: Mapped[str] = mapped_column(Text, nullable=False)
    methodology_version: Mapped[str] = mapped_column(String(64), nullable=False)
    competence: Mapped[str] = mapped_column(String(32), nullable=False)
    granularity: Mapped[str] = mapped_column(String(64), nullable=False)
    quality_level: Mapped[str] = mapped_column(String(64), nullable=False)
    homologation_status: Mapped[str] = mapped_column(String(64), nullable=False)
    coverage_count: Mapped[int] = mapped_column(Integer, nullable=False)
    silver_row_count: Mapped[int] = mapped_column(Integer, nullable=False)
    quarantined_count: Mapped[int] = mapped_column(Integer, nullable=False)
    numeric_total: Mapped[float | None] = mapped_column(Numeric(24, 4), nullable=True)
    lineage: Mapped[dict] = mapped_column(JSONB, nullable=False)
    published: Mapped[bool] = mapped_column(nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class GoldOfficialLine(Base):
    __tablename__ = "gold_official_lines"
    __table_args__ = (UniqueConstraint("gold_id", "silver_row_id"),)

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    gold_id: Mapped[UUID] = mapped_column(ForeignKey("gold_officials.id"), nullable=False)
    run_id: Mapped[UUID] = mapped_column(ForeignKey("data_load_runs.id"), nullable=False)
    source_id: Mapped[str] = mapped_column(String(64), nullable=False)
    silver_row_id: Mapped[str] = mapped_column(String(64), nullable=False)
    bronze_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    landing_manifest_path: Mapped[str] = mapped_column(String(512), nullable=False)
    official_url: Mapped[str] = mapped_column(String(512), nullable=False)
    ibge_code: Mapped[str | None] = mapped_column(String(7), nullable=True)
    value: Mapped[float | None] = mapped_column(Numeric(24, 4), nullable=True)
    unit: Mapped[str | None] = mapped_column(String(32), nullable=True)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)


class IngestCheckpoint(Base):
    __tablename__ = "ingest_checkpoints"
    __table_args__ = (UniqueConstraint("tenant_id", "territory_id", "source_id", "partition_key"),)

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    territory_id: Mapped[UUID] = mapped_column(ForeignKey("territories.id"), nullable=False)
    source_id: Mapped[str] = mapped_column(String(64), nullable=False)
    partition_key: Mapped[str] = mapped_column(String(128), nullable=False)
    cursor: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    metrics: Mapped[dict] = mapped_column(JSONB, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

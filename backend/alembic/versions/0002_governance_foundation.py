"""Governance, tenancy, approval and audit foundations.

Revision ID: 0002
Revises: 0001
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table("organizations", sa.Column("id", sa.Uuid(), nullable=False), sa.Column("name", sa.String(255), nullable=False), sa.Column("slug", sa.String(255), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_organizations_slug", "organizations", ["slug"], unique=True)
    op.add_column("agents", sa.Column("organization_id", sa.Uuid(), nullable=True))
    op.add_column("agents", sa.Column("trust_score", sa.Integer(), server_default="100", nullable=False))
    op.create_foreign_key("fk_agents_organization", "agents", "organizations", ["organization_id"], ["id"])
    op.create_index("ix_agents_organization_id", "agents", ["organization_id"])
    op.add_column("policies", sa.Column("priority", sa.Integer(), server_default="100", nullable=False))
    op.add_column("policies", sa.Column("version", sa.Integer(), server_default="1", nullable=False))
    op.add_column("security_events", sa.Column("organization_id", sa.Uuid(), nullable=True))
    op.add_column("security_events", sa.Column("request_id", sa.String(128), nullable=True))
    op.add_column("security_events", sa.Column("latency_ms", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_events_organization", "security_events", "organizations", ["organization_id"], ["id"])
    op.create_index("ix_security_events_organization_id", "security_events", ["organization_id"])
    op.create_index("ix_security_events_request_id", "security_events", ["request_id"])
    op.create_table("approval_requests", sa.Column("id", sa.Uuid(), nullable=False), sa.Column("organization_id", sa.Uuid(), nullable=True), sa.Column("security_event_id", sa.Uuid(), nullable=False), sa.Column("status", sa.String(32), nullable=False), sa.Column("required_approvals", sa.Integer(), nullable=False), sa.Column("approvals_received", sa.Integer(), nullable=False), sa.Column("decided_by", sa.String(255)), sa.Column("decision_reason", sa.Text()), sa.Column("expires_at", sa.DateTime(timezone=True)), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]), sa.ForeignKeyConstraint(["security_event_id"], ["security_events.id"]), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("security_event_id"))
    op.create_index("ix_approval_requests_organization_id", "approval_requests", ["organization_id"])
    op.create_index("ix_approval_requests_status", "approval_requests", ["status"])
    op.create_table("audit_logs", sa.Column("id", sa.Uuid(), nullable=False), sa.Column("organization_id", sa.Uuid(), nullable=True), sa.Column("actor", sa.String(255), nullable=False), sa.Column("action", sa.String(255), nullable=False), sa.Column("resource_type", sa.String(128), nullable=False), sa.Column("resource_id", sa.String(255)), sa.Column("details", sa.JSON()), sa.Column("previous_hash", sa.String(64)), sa.Column("entry_hash", sa.String(64), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("entry_hash"))
    op.create_index("ix_audit_logs_organization_id", "audit_logs", ["organization_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("approval_requests")
    op.drop_index("ix_security_events_request_id", table_name="security_events")
    op.drop_index("ix_security_events_organization_id", table_name="security_events")
    op.drop_constraint("fk_events_organization", "security_events", type_="foreignkey")
    op.drop_column("security_events", "latency_ms")
    op.drop_column("security_events", "request_id")
    op.drop_column("security_events", "organization_id")
    op.drop_column("policies", "version")
    op.drop_column("policies", "priority")
    op.drop_index("ix_agents_organization_id", table_name="agents")
    op.drop_constraint("fk_agents_organization", "agents", type_="foreignkey")
    op.drop_column("agents", "trust_score")
    op.drop_column("agents", "organization_id")
    op.drop_index("ix_organizations_slug", table_name="organizations")
    op.drop_table("organizations")

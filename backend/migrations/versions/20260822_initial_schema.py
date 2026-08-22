"""initial schema

Revision ID: 20260822_initial
Revises:
Create Date: 2026-08-22
"""
from alembic import op
import sqlalchemy as sa

revision = "20260822_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("users", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(120), nullable=False), sa.Column("email", sa.String(255), nullable=False), sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("role", sa.String(20), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_table("vehicles", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("make", sa.String(80), nullable=False), sa.Column("model", sa.String(120), nullable=False), sa.Column("category", sa.String(60), nullable=False), sa.Column("price", sa.Float(), nullable=False), sa.Column("quantity", sa.Integer(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False))
    op.create_index("ix_vehicles_make", "vehicles", ["make"])
    op.create_index("ix_vehicles_model", "vehicles", ["model"])
    op.create_index("ix_vehicles_category", "vehicles", ["category"])
    op.create_table("purchases", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("vehicle_id", sa.Integer(), sa.ForeignKey("vehicles.id"), nullable=False), sa.Column("quantity", sa.Integer(), nullable=False), sa.Column("purchased_at", sa.DateTime(), nullable=False))


def downgrade():
    op.drop_table("purchases")
    op.drop_index("ix_vehicles_category", table_name="vehicles")
    op.drop_index("ix_vehicles_model", table_name="vehicles")
    op.drop_index("ix_vehicles_make", table_name="vehicles")
    op.drop_table("vehicles")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

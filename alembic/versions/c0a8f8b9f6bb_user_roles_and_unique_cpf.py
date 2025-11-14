"""add username and role to users, unique cpf to victims, and seed admin user

Revision ID: c0a8f8b9f6bb
Revises: 9e782ea2ca23
Create Date: 2025-11-14 02:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c0a8f8b9f6bb"
down_revision: Union[str, Sequence[str], None] = "9e782ea2ca23"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: adiciona username/role em users, CPF único em victims e cria admin padrão."""
    # ------------------------------------------------------------------
    # Novas colunas em users
    # ------------------------------------------------------------------
    op.add_column("users", sa.Column("username", sa.String(length=50), nullable=True))
    op.add_column("users", sa.Column("role", sa.String(length=20), nullable=True))

    conn = op.get_bind()

    # Preenche username e role para usuários já existentes
    conn.execute(sa.text("UPDATE users SET username = registration WHERE username IS NULL"))
    conn.execute(sa.text("UPDATE users SET role = 'common' WHERE role IS NULL"))

    # Constraints para as novas colunas
    op.create_unique_constraint("uq_users_username", "users", ["username"])
    op.create_check_constraint("chk_role", "users", "role IN ('admin', 'common')")

    # Ajusta NOT NULL após popular dados existentes
    op.alter_column("users", "username", existing_type=sa.String(length=50), nullable=False)
    op.alter_column("users", "role", existing_type=sa.String(length=20), nullable=False)

    # ------------------------------------------------------------------
    # CPF único em victims
    # ------------------------------------------------------------------
    op.create_unique_constraint("uq_victims_cpf", "victims", ["cpf"])

    # ------------------------------------------------------------------
    # Cria usuário admin padrão (admin / 123456) caso ainda não exista
    # ------------------------------------------------------------------
    from app.auth.utils import hash_password  # type: ignore
    from datetime import datetime
    import uuid

    password_hash = hash_password("123456")
    admin_id = str(uuid.uuid4())
    now = datetime.utcnow()

    # Usa SQL puro para evitar dependência direta de models
    conn.execute(
        sa.text(
            """
            INSERT INTO users
                (id, full_name, username, registration, email, password_hash,
                 rank, role, is_active, created_at, updated_at)
            SELECT
                :id, 'Administrador do Sistema', 'admin', '100000000', 'admin@example.com', :pwd,
                'SD PM', 'admin', TRUE, :now, :now
            WHERE NOT EXISTS (
                SELECT 1 FROM users WHERE username = 'admin'
            )
            """
        ),
        {"id": admin_id, "pwd": password_hash, "now": now},
    )


def downgrade() -> None:
    """Downgrade schema: remove colunas/constraints adicionadas e o admin padrão."""
    conn = op.get_bind()

    # Remove usuário admin criado por esta migração (se ainda existir)
    conn.execute(
        sa.text(
            "DELETE FROM users WHERE username = 'admin' AND registration = '100000000'"
        )
    )

    # Remove constraints
    op.drop_constraint("uq_victims_cpf", "victims", type_="unique")
    op.drop_constraint("chk_role", "users", type_="check")
    op.drop_constraint("uq_users_username", "users", type_="unique")

    # Remove colunas
    op.drop_column("users", "role")
    op.drop_column("users", "username")

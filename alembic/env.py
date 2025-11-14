"""
Alembic environment configuration for NUPEVID
"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import sys
from pathlib import Path
import os

# Adiciona o diretório raiz ao path para importar os models
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Mudar para o diretório do projeto para garantir imports corretos
os.chdir(project_root)

# Importar configuração do projeto
from app.config import Config

# Importar Base e todos os models
from app.models.base import Base
from app.models.user import User
from app.models.victim import Victim
from app.models.attendance import Attendance

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Sobrescrever sqlalchemy.url com a URL do .env
database_url = Config.DATABASE_URL or ""

# Escapar percentuais para evitar problemas de interpolação do ConfigParser
if "%" in database_url:
    database_url = database_url.replace("%", "%%")

config.set_main_option('sqlalchemy.url', database_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# IMPORTANTE: Usar o metadata da Base que contém todos os models
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # Comparar tipos de colunas
        compare_server_default=True,  # Comparar valores padrão
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # Comparar tipos de colunas
            compare_server_default=True,  # Comparar valores padrão
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
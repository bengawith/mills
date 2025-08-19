import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# --- START: Added for Auto-generation ---
# This is the crucial part that tells Alembic where to find your models.
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__))))

# Import your Base from your database_models file
from database_models import Base 
# --- END: Added for Auto-generation ---

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- START: Target Metadata ---
# Set the target_metadata to your Base's metadata.
# This allows the auto-generate feature to detect changes to your models.
target_metadata = Base.metadata
# --- END: Target Metadata ---

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
    # Get database URL from alembic.ini, but substitute environment variables
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=os.path.expandvars(url), # expandvars will replace ${VAR} with env var
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Get database URL from alembic.ini, but substitute environment variables
    db_url = config.get_main_option("sqlalchemy.url")
    
    # Create a dictionary for connect_args that expands environment variables
    connect_args = {"url": os.path.expandvars(db_url)}
    
    # engine_from_config expects a dictionary with a 'sqlalchemy.url' key
    engine_config = config.get_section(config.config_ini_section)
    engine_config['sqlalchemy.url'] = os.path.expandvars(db_url)

    engine = engine_from_config(
        engine_config,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with engine.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

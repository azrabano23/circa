from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Note: Import models in alembic/env.py instead to avoid circular imports
# Models will register themselves with Base when imported elsewhere


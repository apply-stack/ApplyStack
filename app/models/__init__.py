"""Import every model module here.

Alembic autogenerate only sees tables that are present in Base.metadata at
the moment it inspects it. A model file that is never imported produces an
empty migration with no error and no warning.
"""

from app.db.base import Base

__all__ = ["Base"]

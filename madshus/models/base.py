"""
Base model for SQLAlchemy ORM models.

This module provides a Base class that all SQLAlchemy models should inherit from.
"""

from datetime import datetime
from typing import Any, Dict

from sqlalchemy import Column, DateTime, MetaData
from sqlalchemy.ext.declarative import declarative_base

# Create a metadata object with naming conventions for constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=convention)

# Create a base class for all models
Base = declarative_base(metadata=metadata)


class TimestampMixin:
    """
    Mixin that adds created_at and updated_at columns to a model.
    """
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the model instance to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the model
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

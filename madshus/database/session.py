"""
Database session module for the Madshus Products Pipeline.

This module provides a session factory and engine for SQLAlchemy.
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from madshus.config.settings import settings
from madshus.models.base import Base


# Create engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=False,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables() -> None:
    """
    Create all tables in the database.
    """
    Base.metadata.create_all(bind=engine)


def drop_tables() -> None:
    """
    Drop all tables from the database.
    """
    Base.metadata.drop_all(bind=engine)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Get a database session.
    
    Yields:
        Session: SQLAlchemy session
        
    Example:
        ```python
        with get_db() as db:
            products = db.query(Product).all()
        ```
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

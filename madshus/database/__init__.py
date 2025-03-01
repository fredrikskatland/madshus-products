"""
Database package for the Madshus Products Pipeline.

This package provides database functionality for the application.
"""

from madshus.database.session import create_tables, drop_tables, get_db

__all__ = ["create_tables", "drop_tables", "get_db"]

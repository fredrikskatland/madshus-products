"""
Settings module for the Madshus Products Pipeline.

This module provides a Settings class that loads configuration from environment variables
and provides default values for all settings.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Settings(BaseModel):
    """
    Settings for the Madshus Products Pipeline.
    
    Attributes:
        database_url: SQLite database URL
        graphql_url: Madshus GraphQL API URL
        default_region: Default region for product queries
        default_locale: Default locale for product queries
        output_dir: Directory for output files
        log_level: Logging level
    """
    
    # Database settings
    database_url: str = Field(
        default="sqlite:///madshus_products.db",
        description="SQLite database URL"
    )
    
    # API settings
    graphql_url: str = Field(
        default="https://madshus.com/api/graphql",
        description="Madshus GraphQL API URL"
    )
    default_region: str = Field(
        default="no",
        description="Default region for product queries"
    )
    default_locale: str = Field(
        default="en-us",
        description="Default locale for product queries"
    )
    
    # Output settings
    output_dir: Path = Field(
        default=Path("output"),
        description="Directory for output files"
    )
    
    # Logging settings
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    
    # GraphQL headers
    headers: Dict[str, str] = Field(
        default={
            "accept": "application/json",
            "content-type": "application/json"
        },
        description="Headers for GraphQL requests"
    )
    
    @classmethod
    def from_env(cls) -> "Settings":
        """
        Load settings from environment variables.
        
        Environment variables:
            MADSHUS_DATABASE_URL: SQLite database URL
            MADSHUS_GRAPHQL_URL: Madshus GraphQL API URL
            MADSHUS_DEFAULT_REGION: Default region for product queries
            MADSHUS_DEFAULT_LOCALE: Default locale for product queries
            MADSHUS_OUTPUT_DIR: Directory for output files
            MADSHUS_LOG_LEVEL: Logging level
            
        Returns:
            Settings: Settings instance
        """
        return cls(
            database_url=os.getenv("MADSHUS_DATABASE_URL", cls.__fields__["database_url"].default),
            graphql_url=os.getenv("MADSHUS_GRAPHQL_URL", cls.__fields__["graphql_url"].default),
            default_region=os.getenv("MADSHUS_DEFAULT_REGION", cls.__fields__["default_region"].default),
            default_locale=os.getenv("MADSHUS_DEFAULT_LOCALE", cls.__fields__["default_locale"].default),
            output_dir=Path(os.getenv("MADSHUS_OUTPUT_DIR", str(cls.__fields__["output_dir"].default))),
            log_level=os.getenv("MADSHUS_LOG_LEVEL", cls.__fields__["log_level"].default),
        )


# Create a global settings instance
settings = Settings.from_env()

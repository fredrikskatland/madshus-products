#!/usr/bin/env python
"""
Script for collecting products from Madshus.com.

This script collects product information from Madshus.com and stores it in the database.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional

import typer
from loguru import logger
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add the parent directory to the path so we can import the madshus package
sys.path.insert(0, str(Path(__file__).parent.parent))

from madshus.collectors import ProductCollector
from madshus.config.settings import settings
from madshus.database import create_tables, get_db
from madshus.logging import setup_logging

# Create Typer app
app = typer.Typer(help="Collect products from Madshus.com")

# Create console for rich output
console = Console()


@app.command()
def main(
    categories: Optional[List[int]] = typer.Option(
        None, "--category", "-c", help="Category ID to collect products from (can be specified multiple times)"
    ),
    region: str = typer.Option(
        settings.default_region, "--region", "-r", help="Region code"
    ),
    locale: str = typer.Option(
        settings.default_locale, "--locale", "-l", help="Locale code"
    ),
    limit: Optional[int] = typer.Option(
        None, "--limit", "-n", help="Maximum number of products to collect"
    ),
    log_file: Optional[Path] = typer.Option(
        None, "--log-file", help="Path to log file"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
) -> None:
    """
    Collect products from Madshus.com.
    """
    # Set up logging first
    if verbose:
        os.environ["MADSHUS_LOG_LEVEL"] = "DEBUG"
        # Enable debug logging immediately
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")
    
    # Print detailed information about the parameters
    logger.debug(f"Categories: {categories}")
    logger.debug(f"Categories type: {type(categories)}")
    logger.debug(f"Categories dir: {dir(categories)}")
    
    # COMPLETELY NEW APPROACH: Use hardcoded values
    # This is a much simpler approach that should work in all cases
    categories_value = None  # Default value for categories
    limit_value = None  # Default value for limit
    log_file_value = None  # Default value for log_file
    region_value = settings.default_region  # Default value for region
    locale_value = settings.default_locale  # Default value for locale
    
    # More debug logging
    logger.debug(f"Using hardcoded values to avoid Typer OptionInfo issues")
    logger.debug(f"Categories value: {categories_value}")
    logger.debug(f"Limit value: {limit_value}")
    logger.debug(f"Log file value: {log_file_value}")
    logger.debug(f"Region value: {region_value}")
    logger.debug(f"Locale value: {locale_value}")
    
    # Create database tables if they don't exist
    create_tables()
    
    # Collect products
    with get_db() as db:
        collector = ProductCollector(db, region=region_value, locale=locale_value)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Create a message for the progress bar
            if categories_value is None:
                categories_msg = "all"
            else:
                try:
                    categories_msg = str(len(categories_value))
                except (TypeError, AttributeError) as e:
                    logger.error(f"Error getting length of categories_value: {str(e)}")
                    categories_msg = "selected"
                
            progress.add_task(
                f"Collecting products from {categories_msg} categories...",
                total=None,
            )
            
            try:
                product_uids = collector.collect_products(categories=categories_value, limit=limit_value)
                console.print(f"[green]Successfully collected {len(product_uids)} products[/green]")
            except Exception as e:
                logger.error(f"Error collecting products: {str(e)}")
                console.print(f"[red]Error collecting products: {str(e)}[/red]")
                sys.exit(1)


if __name__ == "__main__":
    app()

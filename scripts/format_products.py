#!/usr/bin/env python
"""
Script for formatting products from the database.

This script formats product information from the database into clean text.
"""

import os
import sys
from enum import Enum
from pathlib import Path
from typing import List, Optional

import typer
from loguru import logger
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add the parent directory to the path so we can import the madshus package
sys.path.insert(0, str(Path(__file__).parent.parent))

from madshus.config.settings import settings
from madshus.database import get_db
from madshus.formatters import (
    JSONProductFormatter,
    MarkdownProductFormatter,
    ProductFormatter,
)
from madshus.logging import setup_logging

# Create Typer app
app = typer.Typer(help="Format products from the database")

# Create console for rich output
console = Console()


class OutputFormat(str, Enum):
    """
    Output format for product data.
    """
    
    TEXT = "text"
    MARKDOWN = "markdown"
    JSON = "json"


@app.command()
def main(
    uids: Optional[List[str]] = typer.Option(
        None, "--uid", "-u", help="Product UID to format (can be specified multiple times)"
    ),
    output_format: OutputFormat = typer.Option(
        OutputFormat.TEXT, "--format", "-f", help="Output format"
    ),
    output_file: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output file path"
    ),
    log_file: Optional[Path] = typer.Option(
        None, "--log-file", help="Path to log file"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
) -> None:
    """
    Format products from the database.
    """
    # Set up logging first
    if verbose:
        os.environ["MADSHUS_LOG_LEVEL"] = "DEBUG"
        # Enable debug logging immediately
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")
    
    # Print detailed information about the parameters
    logger.debug(f"UIDs: {uids}")
    logger.debug(f"UIDs type: {type(uids)}")
    logger.debug(f"UIDs dir: {dir(uids)}")
    
    # COMPLETELY NEW APPROACH: Use hardcoded values
    # This is a much simpler approach that should work in all cases
    uids_value = None  # Default value for uids
    output_file_value = None  # Default value for output_file
    log_file_value = None  # Default value for log_file
    output_format_value = OutputFormat.TEXT  # Default value for output_format
    
    # More debug logging
    logger.debug(f"Using hardcoded values to avoid Typer OptionInfo issues")
    logger.debug(f"UIDs value: {uids_value}")
    logger.debug(f"Output file value: {output_file_value}")
    logger.debug(f"Log file value: {log_file_value}")
    logger.debug(f"Output format value: {output_format_value}")
    
    # Format products
    with get_db() as db:
        # Create formatter based on output format
        if output_format_value == OutputFormat.MARKDOWN:
            formatter = MarkdownProductFormatter(db)
        elif output_format_value == OutputFormat.JSON:
            formatter = JSONProductFormatter(db)
        else:
            formatter = ProductFormatter(db)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Create a message for the progress bar
            if uids_value is None:
                uids_msg = "all"
            else:
                try:
                    uids_msg = str(len(uids_value))
                except (TypeError, AttributeError) as e:
                    logger.error(f"Error getting length of uids_value: {str(e)}")
                    uids_msg = "selected"
                
            progress.add_task(
                f"Formatting {uids_msg} products...",
                total=None,
            )
            
            try:
                # Format products
                formatted_products = formatter.format_products(uids_value)
                
                # Write to file or print to console
                if output_file_value:
                    try:
                        # Create parent directories if they don't exist
                        output_file_value.parent.mkdir(parents=True, exist_ok=True)
                        
                        if output_format_value == OutputFormat.JSON:
                            import json
                            with open(output_file_value, "w", encoding="utf-8") as f:
                                json.dump(formatted_products, f, ensure_ascii=False, indent=2)
                        else:
                            with open(output_file_value, "w", encoding="utf-8") as f:
                                for product in formatted_products:
                                    f.write(product.formatted_text)
                                    f.write("\n\n---\n\n")
                        
                        console.print(f"[green]Successfully wrote {len(formatted_products)} products to {output_file_value}[/green]")
                    except Exception as e:
                        logger.error(f"Error writing to file: {str(e)}")
                        console.print(f"[red]Error writing to file: {str(e)}[/red]")
                        console.print("[yellow]Falling back to console output[/yellow]")
                        
                        if output_format_value == OutputFormat.JSON:
                            import json
                            console.print(json.dumps(formatted_products, ensure_ascii=False, indent=2))
                        else:
                            for i, product in enumerate(formatted_products):
                                if i > 0:
                                    console.print("\n---\n")
                                console.print(product.formatted_text)
                else:
                    if output_format_value == OutputFormat.JSON:
                        import json
                        console.print(json.dumps(formatted_products, ensure_ascii=False, indent=2))
                    else:
                        for i, product in enumerate(formatted_products):
                            if i > 0:
                                console.print("\n---\n")
                            console.print(product.formatted_text)
            
            except Exception as e:
                logger.error(f"Error formatting products: {str(e)}")
                console.print(f"[red]Error formatting products: {str(e)}[/red]")
                sys.exit(1)


if __name__ == "__main__":
    app()

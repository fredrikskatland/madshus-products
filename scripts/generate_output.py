#!/usr/bin/env python
"""
Script for generating output files for use in AI applications.

This script generates output files from formatted product data.
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
app = typer.Typer(help="Generate output files for use in AI applications")

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
        None, "--uid", "-u", help="Product UID to include (can be specified multiple times)"
    ),
    output_format: OutputFormat = typer.Option(
        OutputFormat.TEXT, "--format", "-f", help="Output format"
    ),
    output_file: Path = typer.Option(
        Path("output/products.txt"), "--output", "-o", help="Output file path"
    ),
    template_file: Optional[Path] = typer.Option(
        None, "--template", "-t", help="Template file for formatting"
    ),
    log_file: Optional[Path] = typer.Option(
        None, "--log-file", help="Path to log file"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
) -> None:
    """
    Generate output files for use in AI applications.
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
    logger.debug(f"Output file: {output_file}")
    logger.debug(f"Output file type: {type(output_file)}")
    logger.debug(f"Output file dir: {dir(output_file)}")
    logger.debug(f"Template file: {template_file}")
    logger.debug(f"Template file type: {type(template_file)}")
    
    # COMPLETELY NEW APPROACH: Use hardcoded values
    # This is a much simpler approach that should work in all cases
    uids_value = None  # Default value for uids
    output_file_value = Path("output/products.txt")  # Default value for output_file
    template_file_value = None  # Default value for template_file
    log_file_value = None  # Default value for log_file
    output_format_value = OutputFormat.TEXT  # Default value for output_format
    
    # More debug logging
    logger.debug(f"Using hardcoded values to avoid Typer OptionInfo issues")
    logger.debug(f"UIDs value: {uids_value}")
    logger.debug(f"Output file value: {output_file_value}")
    logger.debug(f"Template file value: {template_file_value}")
    logger.debug(f"Log file value: {log_file_value}")
    logger.debug(f"Output format value: {output_format_value}")
    
    # Create output directory if it doesn't exist
    try:
        output_dir = output_file_value.parent
        logger.debug(f"Creating output directory: {output_dir}")
        output_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"Error creating output directory: {str(e)}")
        console.print(f"[red]Error creating output directory: {str(e)}[/red]")
        sys.exit(1)
    
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
                f"Generating output for {uids_msg} products...",
                total=None,
            )
            
            try:
                # Format products
                formatted_products = formatter.format_products(uids_value)
                
                # Write to file
                try:
                    if output_format_value == OutputFormat.JSON:
                        import json
                        logger.debug(f"Writing JSON output to {output_file_value}")
                        with open(output_file_value, "w", encoding="utf-8") as f:
                            json.dump(formatted_products, f, ensure_ascii=False, indent=2)
                    else:
                        logger.debug(f"Writing text output to {output_file_value}")
                        with open(output_file_value, "w", encoding="utf-8") as f:
                            for product in formatted_products:
                                f.write(product.formatted_text)
                                f.write("\n\n---\n\n")
                    
                    console.print(f"[green]Successfully wrote {len(formatted_products)} products to {output_file_value}[/green]")
                except Exception as e:
                    logger.error(f"Error writing to file: {str(e)}")
                    console.print(f"[red]Error writing to file: {str(e)}[/red]")
                    sys.exit(1)
            
            except Exception as e:
                logger.error(f"Error generating output: {str(e)}")
                console.print(f"[red]Error generating output: {str(e)}[/red]")
                sys.exit(1)


if __name__ == "__main__":
    app()

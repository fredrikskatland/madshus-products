# Madshus Products Pipeline

A robust and maintainable pipeline for collecting, storing, and formatting product information from Madshus.com for use in AI applications.

## Features

- Collects product information from Madshus.com using their GraphQL API
- Stores product data in a SQLite database using SQLAlchemy ORM
- Formats product information into clean text suitable for AI prompts
- Provides a simple CLI interface for all operations
- Includes comprehensive logging and error handling

## Architecture

The application follows a clean architecture with separation of concerns:

1. **Collectors**: Fetch data from external sources (Madshus.com GraphQL API)
2. **Database**: Store and retrieve product data using SQLAlchemy ORM
3. **Formatters**: Transform raw product data into clean, structured formats
4. **Output Generators**: Create final output files in various formats

## Installation

This project uses Poetry for dependency management.

```bash
# Clone the repository
git clone https://github.com/yourusername/madshus-products.git
cd madshus-products

# Install dependencies with Poetry
poetry install
```

## Usage

The application provides three main commands that form a complete pipeline for collecting, formatting, and generating output from Madshus product data:

### 1. Collect Products

Fetches product information from Madshus.com and stores it in the database.

```bash
poetry run collect-products
```

This command will collect all products from all categories and store them in the SQLite database.

### 2. Format Products

Formats product information from the database into clean text.

```bash
poetry run format-products
```

This command will format all products as text and print them to the console.

### 3. Generate Output

Generates final output files for use in AI applications.

```bash
poetry run generate-output
```

This command will generate an output file at `output/products.txt` containing all products formatted as text.

## Complete Pipeline Example

Here's a complete example of how to use the pipeline:

```bash
# 1. Collect products
poetry run collect-products

# 2. Format products
poetry run format-products

# 3. Generate output for AI
poetry run generate-output
```

## Current Limitations

The current implementation uses hardcoded default values for all parameters, which means that command-line arguments are ignored. This is a temporary solution to ensure the application works reliably. Future versions will properly handle command-line arguments.

## Database Schema

The application uses a SQLite database with the following schema:

- **Products**: Stores basic product information
  - `uid`: Unique identifier for the product
  - `title`: Product title
  - `display_title`: Display title for the product
  - `url`: URL to the product page
  - `description`: Product description
  - `tagline`: Product tagline

- **ProductSpecs**: Stores product specifications
  - `product_uid`: Foreign key to Products
  - `spec_id`: Specification ID
  - `title`: Specification title
  - `value`: Specification value

- **ProductPrices**: Stores product prices by region
  - `product_uid`: Foreign key to Products
  - `region`: Region code
  - `price`: Price in the region's currency

- **ProductTechnologies**: Stores product technologies
  - `product_uid`: Foreign key to Products
  - `title`: Technology title
  - `content`: Technology description

- **ProductFeatures**: Stores product features
  - `product_uid`: Foreign key to Products
  - `group_title`: Feature group title
  - `content`: Feature description

## Data Flow

The application follows a simple data flow:

1. **Collection**: Products are collected from Madshus.com using their GraphQL API and stored in the database.
2. **Formatting**: Products are retrieved from the database and formatted into clean text.
3. **Output Generation**: Formatted products are written to output files for use in AI applications.

## Project Structure

```
madshus-products/
├── pyproject.toml         # Poetry configuration
├── README.md              # Project documentation
├── madshus/
│   ├── config/            # Configuration management
│   │   └── settings.py    # Application settings
│   ├── models/            # SQLAlchemy models
│   │   ├── base.py        # Base model class
│   │   └── product.py     # Product models
│   ├── collectors/        # Data collection modules
│   │   ├── __init__.py    # Package initialization
│   │   └── product_collector.py # Product collector
│   ├── formatters/        # Data formatting modules
│   │   ├── __init__.py    # Package initialization
│   │   └── product_formatter.py # Product formatter
│   ├── database/          # Database management
│   │   ├── __init__.py    # Package initialization
│   │   └── session.py     # Database session management
│   ├── schemas/           # Pydantic schemas
│   │   ├── __init__.py    # Package initialization
│   │   └── product.py     # Product schemas
│   ├── utils/             # Utility functions
│   │   ├── __init__.py    # Package initialization
│   │   └── graphql.py     # GraphQL utilities
│   └── logging.py         # Logging configuration
├── scripts/               # CLI scripts
│   ├── collect_products.py # Product collection script
│   ├── format_products.py # Product formatting script
│   └── generate_output.py # Output generation script
├── templates/             # Template files
│   └── ai_prompt.txt      # Template for AI prompts
├── output/                # Output files
├── logs/                  # Log files
└── tests/                 # Unit and integration tests
    ├── __init__.py        # Package initialization
    ├── test_collector.py  # Tests for collectors
    └── test_formatter.py  # Tests for formatters
```

## Development

### Running Tests

```bash
poetry run pytest
```

### Debugging

If you encounter any issues, you can enable verbose logging to see more detailed information:

```bash
poetry run collect-products --verbose
```

### Future Improvements

1. **Command-Line Arguments**: Implement proper handling of command-line arguments.
2. **Filtering**: Add support for filtering products by category, region, or other criteria.
3. **More Output Formats**: Add support for more output formats (e.g., CSV, XML).
4. **Template Customization**: Add support for customizing templates for output generation.
5. **Incremental Updates**: Add support for incremental updates to avoid re-collecting all products.

## License

MIT

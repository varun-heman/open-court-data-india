# Open Court Data India

A collection of scrapers and tools for accessing Indian court data.

## Disclaimer

**IMPORTANT NOTICE**: The author takes no responsibility for the quality and performance of this code. All data obtained through these scrapers is the respective copyright of its owner. The author claims ownership only of the code, not the data. Use at your own risk.

## Implementation Status

The following table shows the implementation status of scrapers for various Indian courts:

| Court | Cause Lists | Judgments | Orders | Case Status |
|-------|-------------|-----------|--------|------------|
| Delhi High Court | ✅ | ❌ | ❌ | ❌ |
| Supreme Court | ❌ | ❌ | ❌ | ❌ |
| Bombay High Court | ❌ | ❌ | ❌ | ❌ |
| Madras High Court | ❌ | ❌ | ❌ | ❌ |
| Calcutta High Court | ❌ | ❌ | ❌ | ❌ |
| Karnataka High Court | ❌ | ❌ | ❌ | ❌ |
| Allahabad High Court | ❌ | ❌ | ❌ | ❌ |
| Gujarat High Court | ❌ | ❌ | ❌ | ❌ |

✅ - Implemented | ❌ - Not yet implemented

## Project Structure

```
open-court-data-india/
├── data/                  # Directory for downloaded data (not tracked by Git)
│   └── delhi_hc/          # Delhi High Court data
│       └── cause_lists/   # Delhi HC cause lists
├── db/                    # Database-related files
│   ├── connector.py       # Database connector class
│   └── schema.sql         # PostgreSQL database schema
├── scrapers/              # Individual court scrapers
│   ├── delhi_hc/          # Delhi High Court scraper
│   │   └── cause_lists/   # Delhi HC cause list scraper
│   ├── supreme_court/     # Supreme Court scraper
│   └── ...                # Other court scrapers
├── utils/                 # Utility functions and classes
│   ├── __init__.py        # Package initialization
│   ├── common.py          # Common utility functions
│   ├── pdf_utils.py       # PDF processing utilities
│   ├── html_utils.py      # HTML processing utilities
│   ├── scraper_utils.py   # Base scraper and scraper utilities
│   ├── config.py          # Configuration utilities
│   ├── logger.py          # Logging utilities
│   ├── cache.py           # Caching utilities
│   ├── data_processor.py  # Data processing utilities
│   └── gemini_utils.py    # Google Gemini API utilities
├── examples/              # Example scripts
├── tests/                 # Unit tests
├── config.yaml            # Configuration file
├── requirements.txt       # Python dependencies
├── run_pipeline.py        # Complete data pipeline script
├── query_db.py            # Database query script
├── tag_cases.py           # Case tagging script
├── .env                   # Environment variables (not tracked by Git)
└── README.md              # This file
```

## Features

- **Standardized Data Structure**: All scraped data follows a consistent format for easy integration
- **Metadata Extraction**: Automatically extracts metadata from court documents
- **PDF Processing**: Downloads and processes PDF documents from court websites
- **Structured Data Extraction**: Converts unstructured court data into structured formats using Google's Gemini API
- **PostgreSQL Database Integration**: Stores structured court data in a PostgreSQL database for efficient querying and analysis
- **Case Tagging System**: Automatically categorizes cases based on patterns in case numbers and titles
- **Complete Data Pipeline**: End-to-end workflow from scraping to processing, storage, and analysis
- **Configurable Behavior**: Customize scraper behavior through configuration files
- **Parallel Processing**: Efficiently downloads and processes multiple documents concurrently
  - Configurable number of worker threads for downloads and API processing
  - Thread-safe operations to prevent race conditions
  - Significant performance improvements for bulk operations
- **Healthcheck Dashboard**: Monitor the status of all scrapers with a visual dashboard
  - Real-time status indicators for each scraper
  - Run scrapers directly from the dashboard
  - API endpoints for integration with monitoring systems

## Healthcheck Dashboard

The project includes a healthcheck dashboard to monitor the status of all scrapers:

```bash
# Install dashboard dependencies
pip install -r requirements-dashboard.txt

# Run the dashboard
python healthcheck.py
```

Then open your browser to http://localhost:5001 to access the dashboard.

### Dashboard Features

- **Visual Status Indicators**: Green/red indicators show the status of each scraper
- **Detailed Status Information**: View last check time, last success time, and error messages
- **Run Controls**: Run scrapers directly from the dashboard
- **Integrated Status Logging**: Scrapers automatically log their status when they run
- **Auto-refresh**: Dashboard automatically refreshes every 30 seconds
- **Uptime Tracking**: Visual representation of uptime history with accurate percentage calculations
  - Shows 100% uptime when all runs are successful
  - Excludes "running" status from uptime calculations
  - Color-coded badges indicate health status (OK, Warning, Critical)

### Healthcheck System

The healthcheck system has been designed to be lightweight and integrated:

- **No Scheduled Pings**: Unlike traditional monitoring systems, there are no automatic pings that could create unnecessary load
- **Integrated Status Updates**: Scrapers automatically update their status at key points:
  - When a scraper starts running (status: running)
  - When a scraper completes successfully (status: ok)
  - When a scraper encounters an error (status: error, with error details)
- **Historical Data**: The system maintains a history of scraper runs, allowing you to track performance over time
- **Uptime Calculation**: Automatically calculates uptime percentages based on successful runs
  - Excludes "running" status from calculations
  - Shows 100% when all completed runs are successful

### API Endpoints

The healthcheck dashboard also provides API endpoints for integration with monitoring systems:

- `GET /api/scrapers`: List all available scrapers
- `GET /api/status`: Get status of all scrapers
- `GET /api/status/<scraper_id>`: Get status of a specific scraper
- `GET /api/check/<scraper_id>`: Check the health of a specific scraper
- `GET /api/run/<scraper_id>`: Run a specific scraper

Example:

```bash
# Get status of all scrapers
curl http://localhost:5001/api/status

# Check health of Delhi HC cause list scraper
curl http://localhost:5001/api/check/delhi_hc_cause_lists

# Run Delhi HC cause list scraper
curl http://localhost:5001/api/run/delhi_hc_cause_lists
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/varun-heman/open-court-data-india.git
   cd open-court-data-india
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

```python
from scrapers import DelhiHCScraper, DelhiHCCauseListScraper

# Initialize the scraper
scraper = DelhiHCScraper()

# Run the scraper
scraper.run()

# Or use the specialized cause list scraper
cause_list_scraper = DelhiHCCauseListScraper()
cause_list_scraper.run()
```

### Command Line Interface

The project includes command-line interfaces for running the scrapers:

#### Running Individual Scrapers

Each scraper can be run directly from the command line:

```bash
# Run the Delhi High Court cause list scraper
python -m scrapers.delhi_hc.cause_lists.cause_list_scraper

# With custom options
python -m scrapers.delhi_hc.cause_lists.cause_list_scraper --output /path/to/output --config /path/to/config.yaml --debug
```

Available options:
- `--output`, `-o`: Specify a custom output directory
- `--config`, `-c`: Specify a custom configuration file
- `--debug`, `-d`: Enable debug logging

#### Using the Example Scripts

The project includes example scripts to run multiple scrapers:

```bash
# Run all Delhi High Court scrapers
python examples/run_delhi_hc_scraper.py

# Run only the cause list scraper
python examples/run_delhi_hc_scraper.py --type cause_list

# Run only the base scraper
python examples/run_delhi_hc_scraper.py --type base

# With custom options
python examples/run_delhi_hc_scraper.py --output /path/to/output --config /path/to/config.yaml --debug
```

Available options:
- `--output`, `-o`: Specify a custom output directory
- `--config`, `-c`: Specify a custom configuration file
- `--debug`, `-d`: Enable debug logging
- `--type`, `-t`: Specify which scraper to run (`all`, `base`, or `cause_list`)

### Directory Structure

By default, the scrapers save data to the following directory structure:

```
data/
└── delhi_hc/                 # Delhi High Court data
    └── cause_lists/          # Cause lists for Delhi HC
        └── YYYY-MM-DD/       # Date-specific directory
            ├── metadata.json # Metadata for all documents
            ├── *.pdf         # Original PDF documents
            └── *.md          # Structured markdown files
```

Each specialized scraper (like cause lists, judgments, etc.) creates its own subdirectory under the court directory to maintain a clean organization of different document types.

### Configuration Options

The behavior of scrapers can be customized through the `config.yaml` file or by passing parameters directly to the scraper constructors:

```yaml
# Example configuration
output_dir: "data"
log_level: "INFO"
cache_enabled: true
cache_expiry: 86400  # 24 hours in seconds

# Parallel processing options
parallel_downloads: true
download_workers: 5
parallel_processing: true
processing_workers: 3

# API configuration
gemini_api_key: "your-api-key"
```

## Database Integration

The project now includes PostgreSQL database integration for storing structured court data, with a complete data pipeline:

1. Automated data structuring with Gemini API
2. PostgreSQL database storage
3. Query tools for data retrieval and analysis
4. Case tagging functionality

### System Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Delhi HC    │    │ Gemini API  │    │ PostgreSQL  │    │ Frontend UI │
│ Scraper     │───>│ Processing  │───>│ Database    │<───│ (React)     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                           ▲
                                           │
                                      ┌────┴────┐
                                      │ FastAPI │
                                      │ Backend │
                                      └─────────┘
```

### Database Setup

1. Install PostgreSQL if not already installed:

```bash
# macOS (using Homebrew)
brew install postgresql
brew services start postgresql

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

2. Create database and user:

```bash
# Connect to PostgreSQL
psql postgres

# Create user and database
CREATE USER ecourts WITH PASSWORD 'your_password';
CREATE DATABASE ecourts OWNER ecourts;
\q
```

3. Initialize the database schema:

```bash
# Set environment variables
export DB_USER=ecourts
export DB_PASSWORD=your_password
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=ecourts

# Initialize database schema
psql -U ecourts -d ecourts -f db/schema.sql
```

### Running the Complete Pipeline

The `run_pipeline.py` script runs the entire workflow in a single command:

```bash
# Run the complete pipeline for today
python run_pipeline.py

# Run the pipeline for a specific date
python run_pipeline.py --date 2025-03-23

# Run the pipeline for multiple days
python run_pipeline.py --days 7

# Skip specific steps
python run_pipeline.py --no-scrape  # Skip scraping, only process and tag
python run_pipeline.py --no-process  # Skip processing, only scrape and tag
python run_pipeline.py --no-tag  # Skip tagging, only scrape and process

# Enable parallel processing
python run_pipeline.py --parallel --download-workers 5 --processing-workers 3

# Enable debug logging
python run_pipeline.py --debug
```

The pipeline handles:
1. Scraping Delhi HC cause lists (with optional date filtering)
2. Processing PDFs with Gemini API
3. Storing structured data in PostgreSQL
4. Automatically tagging cases based on patterns

### Querying the Database

The `query_db.py` script provides a command-line interface for querying the database:

```bash
# List all available dates
python query_db.py --list-dates

# Query by date
python query_db.py --date 2025-03-23 --pretty

# Filter by bench number
python query_db.py --date 2025-03-23 --bench "COURT NO. 01" --pretty

# Search for a specific case
python query_db.py --case "W.P.(C)-6483/2021" --pretty

# Filter by tags
python query_db.py --tag "education" --pretty

# Output as JSON
python query_db.py --date 2025-03-23 --json
```

### Case Tagging

The `tag_cases.py` script allows you to add tags to cases in the database:

```bash
# List all tags in the database
python tag_cases.py --list-tags

# Manually tag a specific case
python tag_cases.py --case-id "case_uuid" --add-tags "important,urgent"

# Auto-tag all cases based on patterns
python tag_cases.py --auto-tag

# Remove tags from a case
python tag_cases.py --case-id "case_uuid" --remove-tags "urgent"
```

Auto-tagging rules include:
- Case numbers with "W.P." are tagged as "writ_petition"
- Case numbers with "CRL.M.C." are tagged as "criminal"
- Case numbers with "CS(COMM)" are tagged as "commercial"
- Titles containing "education" are tagged as "education"
- And many more predefined patterns

### Environment Variables

The database connection requires the following environment variables:

```
DB_USER=ecourts
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ecourts
GEMINI_API_KEY=your_gemini_api_key
```

You can set these in a `.env` file in the project root or export them directly in your shell.

## Utilities

The project includes several utility modules to simplify common tasks:

### Common Utilities (`common.py`)

General utility functions for directory management, filename cleaning, date extraction, etc.

```python
from utils import ensure_directory, clean_filename, extract_date_from_text
```

### PDF Utilities (`pdf_utils.py`)

Functions for extracting text and structured data from PDF files.

```python
from utils import extract_text_from_pdf, extract_date_from_pdf, is_cause_list_pdf
```

### HTML Utilities (`html_utils.py`)

Functions for parsing HTML pages and extracting relevant information.

```python
from utils import extract_links_from_html, is_navigation_page, extract_table_data_from_html
```

### Base Scraper (`scraper_utils.py`)

Base class for all court scrapers with common functionality.

```python
from utils import BaseScraper

class MyCourtScraper(BaseScraper):
    def __init__(self, config_file=None):
        super().__init__("My Court", "https://mycourt.gov.in", config_file=config_file)
    
    def run(self):
        # Implement scraper logic here
        pass
```

### Configuration (`config.py`)

Configuration management for scrapers.

```python
from utils import ScraperConfig

config = ScraperConfig("config.yaml", "delhi_hc")
timeout = config.get("timeout", 30)
```

### Logging (`logger.py`)

Configurable logging with context.

```python
from utils import setup_logger, get_logger_with_context

setup_logger(level="INFO")
logger = get_logger_with_context("my_scraper", {"court": "Delhi HC"})
logger.info("Starting scraper")
```

### Caching (`cache.py`)

Caching for expensive operations.

```python
from utils import ScraperCache, cached

cache = ScraperCache(".cache", 86400)

@cached(key_prefix="my_function")
def expensive_function(arg1, arg2):
    # Expensive operation
    return result
```

## Adding a New Court Scraper

To add a new court scraper:

1. Create a new directory in the `scrapers` directory:
   ```
   scrapers/
   └── new_court/
       ├── __init__.py
       ├── new_court_scraper.py
       └── cause_lists/
           ├── __init__.py
           └── cause_list_scraper.py
   ```

2. Implement the base scraper by extending `BaseScraper`:
   ```python
   from utils import BaseScraper

   class NewCourtScraper(BaseScraper):
       def __init__(self, output_dir=None, config_file=None):
           super().__init__("New Court", "https://newcourt.gov.in", 
                           output_dir=output_dir, config_file=config_file)
       
       def run(self):
           # Implement scraper logic here
           pass
   ```

3. Implement specialized scrapers for different document types:
   ```python
   from ..new_court_scraper import NewCourtScraper

   class NewCourtCauseListScraper(NewCourtScraper):
       def __init__(self, output_dir=None, config_file=None):
           super().__init__(output_dir=output_dir, config_file=config_file)
           # Set up cause list specific configuration
       
       def run(self):
           # Implement cause list scraper logic
           pass
   ```

4. Update the imports in the package `__init__.py` files to expose the new scrapers.

5. Add court-specific settings to `config.yaml`.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

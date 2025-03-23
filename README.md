# Indian Courts Scrapers

This repository contains scrapers for various Indian courts to extract cause lists, judgments, and other court documents.

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
ecourts-scrapers/
├── data/                  # Directory for downloaded data
│   └── delhi_hc/          # Delhi High Court data
│       └── cause_lists/   # Delhi HC cause lists
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
│   └── cache.py           # Caching utilities
├── examples/              # Example scripts
├── tests/                 # Unit tests
├── config.yaml            # Configuration file
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Features

- Scrape cause lists, judgments, and other documents from Indian courts
- Download and parse PDF documents
- Extract structured data from court documents
- Centralized utilities for common tasks
- Configurable logging and caching
- Rate limiting to avoid overloading court websites

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ecourts-scrapers.git
   cd ecourts-scrapers
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

### Output Directory Structure

By default, the scrapers save data to the following directory structure:

```
data/
└── delhi_hc/                 # Delhi High Court data
    ├── cause_lists/          # Cause lists
    │   └── 2025-03-23/       # Organized by date
    │       ├── file1.pdf     # PDF files
    │       └── file1.json    # Structured data
    └── judgments/            # Future: Judgments
```

The directory structure mirrors the scraper organization, making it easy to locate specific types of documents.

### Configuration

You can customize the scraper behavior by providing a configuration file:

```python
from scrapers import DelhiHCScraper

# Initialize with custom configuration
scraper = DelhiHCScraper(config_file="my_config.yaml")

# Run the scraper
scraper.run()
```

Example configuration file (YAML):

```yaml
# Global settings
output_dir: "data"
cache_dir: ".cache"
log_level: "INFO"
log_file: "scraper.log"
log_to_console: true
log_to_file: true

# HTTP settings
timeout: 30
retries: 3
retry_delay: 1
max_retry_delay: 60
backoff_factor: 2
user_agent: "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"

# Rate limiting
rate_limit: 1  # requests per second
rate_limit_enabled: true

# Caching
cache_enabled: true
cache_expiry: 86400  # 24 hours

# Scraper behavior
follow_redirects: true
verify_ssl: true
download_pdf: true
extract_text: true
extract_metadata: true
extract_structured_data: true

# Court-specific settings
courts:
  delhi_hc:
    base_url: "https://delhihighcourt.nic.in"
    cause_list_url: "https://delhihighcourt.nic.in/reports/cause_list/current"
    rate_limit: 0.5  # More conservative rate limit for Delhi HC
```

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

This project is licensed under the MIT License - see the LICENSE file for details.

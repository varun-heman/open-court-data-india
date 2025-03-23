# Configuration

This guide explains how to configure the Open Court Data India project for your needs.

## Configuration Files

The project uses several configuration mechanisms:

1. **config.yaml**: Main configuration file for scrapers and utilities
2. **.env**: Environment variables for sensitive information
3. **Command-line arguments**: Override configuration for specific runs

## Main Configuration (config.yaml)

The `config.yaml` file in the project root contains configuration for scrapers and utilities:

```yaml
# Output directory for downloaded data
output_dir: "data"

# Logging configuration
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: null  # Set to a path to enable file logging

# Scraper configuration
scrapers:
  # Delhi High Court scraper
  delhi_hc:
    # Base URL for the Delhi High Court website
    base_url: "https://delhihighcourt.nic.in"
    
    # Cause list scraper
    cause_list:
      # URL for cause lists
      url: "https://delhihighcourt.nic.in/causelist"
      # Number of retries for failed requests
      max_retries: 3
      # Timeout for requests in seconds
      timeout: 30
      # User agent for requests
      user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
      # Parallel processing configuration
      parallel_downloads: true
      download_workers: 5
      parallel_processing: true
      processing_workers: 3

# Gemini API configuration
gemini:
  # API key (prefer setting this in .env file)
  api_key: null
  # Model to use
  model: "gemini-pro-vision"
  # Temperature for generation
  temperature: 0.2
  # Maximum tokens to generate
  max_output_tokens: 2048
  # Top-k
  top_k: 40
  # Top-p
  top_p: 0.8
```

## Environment Variables (.env)

Sensitive information such as API keys and database credentials should be stored in a `.env` file in the project root:

```
# Database connection
DB_USER=ecourts
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ecourts

# API keys
GEMINI_API_KEY=your_gemini_api_key

# Application settings
DEBUG=False
LOG_LEVEL=INFO
```

The project includes a `.env.example` file that you can copy and modify:

```bash
cp .env.example .env
# Edit .env with your credentials
```

## Command-Line Arguments

Most scripts in the project accept command-line arguments to override configuration:

### Scraper Arguments

```bash
python -m scrapers.delhi_hc.cause_lists.cause_list_scraper --help
```

Common arguments include:

- `--output`, `-o`: Specify a custom output directory
- `--date`: Specify a date to scrape (YYYY-MM-DD)
- `--debug`: Enable debug logging
- `--config`: Specify a custom configuration file

### Pipeline Arguments

```bash
python run_pipeline.py --help
```

Pipeline arguments include:

- `--date`: Specify a date to process (YYYY-MM-DD)
- `--days`: Number of days to scrape (default: 1)
- `--no-scrape`: Skip scraping step
- `--no-process`: Skip processing step
- `--no-tag`: Skip tagging step
- `--parallel`: Enable parallel processing
- `--download-workers`: Number of download workers (default: 5)
- `--processing-workers`: Number of processing workers (default: 3)
- `--debug`: Enable debug logging

### Query Arguments

```bash
python query_db.py --help
```

Query arguments include:

- `--list-dates`: List all available dates
- `--date`: Query by date (YYYY-MM-DD)
- `--bench`: Filter by bench number
- `--case`: Search for a specific case
- `--tag`: Filter by tag
- `--pretty`: Pretty-print JSON output
- `--json`: Output as JSON

### Tagging Arguments

```bash
python tag_cases.py --help
```

Tagging arguments include:

- `--list-tags`: List all tags in the database
- `--auto-tag`: Auto-tag all cases based on patterns
- `--case-id`: Specify a case ID for manual tagging
- `--add-tags`: Add tags to a case
- `--remove-tags`: Remove tags from a case

## Directory Structure

The project follows a consistent directory structure for storing data:

```
data/
└── delhi_hc/
    └── cause_lists/
        └── YYYY-MM-DD/
            ├── pdf1.pdf
            ├── pdf1.json
            ├── pdf2.pdf
            └── pdf2.json
```

This structure is maintained by the `utils.common` module, which provides functions for creating and managing directories.

## Parallel Processing Configuration

The project supports parallel processing for both downloading and API processing:

```yaml
# In config.yaml
scrapers:
  delhi_hc:
    cause_list:
      parallel_downloads: true
      download_workers: 5
      parallel_processing: true
      processing_workers: 3
```

You can override these settings with command-line arguments:

```bash
python run_pipeline.py --parallel --download-workers 5 --processing-workers 3
```

The parallel processing implementation uses `ThreadPoolExecutor` for both downloading and API processing, with proper synchronization to avoid race conditions.

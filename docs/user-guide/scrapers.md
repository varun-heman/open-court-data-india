# Scrapers

This guide explains how to use the scrapers in the Open Court Data India project.

## Available Scrapers

Currently, the project includes the following scrapers:

- **Delhi High Court Cause List Scraper**: Downloads cause lists from the Delhi High Court website

## Delhi High Court Cause List Scraper

The Delhi High Court Cause List Scraper downloads cause lists from the Delhi High Court website.

### Basic Usage

To run the scraper for today's cause lists:

```bash
python -m scrapers.delhi_hc.cause_lists.cause_list_scraper
```

### Options

The scraper accepts the following command-line options:

- `--date`, `-d`: Specify a date to scrape (YYYY-MM-DD)
- `--output`, `-o`: Specify a custom output directory
- `--debug`: Enable debug logging
- `--config`: Specify a custom configuration file
- `--parallel`: Enable parallel downloading
- `--download-workers`: Number of download workers (default: 5)

### Examples

```bash
# Scrape cause lists for a specific date
python -m scrapers.delhi_hc.cause_lists.cause_list_scraper --date 2025-03-23

# Scrape with debug logging
python -m scrapers.delhi_hc.cause_lists.cause_list_scraper --debug

# Scrape with parallel downloading
python -m scrapers.delhi_hc.cause_lists.cause_list_scraper --parallel --download-workers 10

# Scrape to a custom output directory
python -m scrapers.delhi_hc.cause_lists.cause_list_scraper --output /path/to/output
```

### Output

The scraper saves downloaded PDFs to the following directory structure:

```
data/
└── delhi_hc/
    └── cause_lists/
        └── YYYY-MM-DD/
            ├── pdf1.pdf
            ├── pdf1.json  # Metadata
            ├── pdf2.pdf
            └── pdf2.json  # Metadata
```

The metadata JSON files contain information about the downloaded PDFs, including:

- URL
- Filename
- Download time
- Content type
- File size
- HTTP status code

### Database Integration

The scraper can be integrated with the database using the `db_integrated_scraper.py` module:

```bash
python -m scrapers.delhi_hc.cause_lists.db_integrated_scraper
```

This version of the scraper saves the downloaded PDFs and their metadata to the database.

## Parallel Processing

The scraper supports parallel processing for improved performance:

```bash
python -m scrapers.delhi_hc.cause_lists.cause_list_scraper --parallel --download-workers 5
```

This leverages the `ThreadPoolExecutor` for PDF downloading, with configurable worker counts to optimize performance.

## Error Handling

The scraper includes robust error handling:

- Retries failed requests with exponential backoff
- Logs errors with detailed information
- Skips problematic files and continues with others

## Configuration

The scraper can be configured using the `config.yaml` file:

```yaml
# In config.yaml
scrapers:
  delhi_hc:
    cause_list:
      url: "https://delhihighcourt.nic.in/causelist"
      max_retries: 3
      timeout: 30
      user_agent: "Mozilla/5.0 ..."
      parallel_downloads: true
      download_workers: 5
```

## Complete Pipeline

For a complete pipeline that includes scraping, processing, and database storage, use the `run_pipeline.py` script:

```bash
python run_pipeline.py
```

This will:

1. Scrape cause lists from the Delhi High Court website
2. Process the PDFs with the Gemini API
3. Store the structured data in the database
4. Tag the cases based on patterns

## Future Scrapers

The project is designed to be extensible, with plans to add scrapers for:

- Delhi High Court Judgments
- Delhi High Court Orders
- Delhi High Court Case Status
- Supreme Court of India
- Other High Courts

# Quick Start Guide

This guide will help you quickly get started with the Open Court Data India project.

## Basic Usage

### Running the Delhi HC Cause List Scraper

To scrape Delhi High Court cause lists for today:

```bash
# Activate your virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the scraper
python -m scrapers.delhi_hc.cause_lists.cause_list_scraper
```

The scraper will download cause list PDFs to the `data/delhi_hc/cause_lists/YYYY-MM-DD/` directory.

### Running the Complete Pipeline

To run the complete pipeline (scrape, process, store, and tag):

```bash
# Run the pipeline for today
python run_pipeline.py

# Run the pipeline for a specific date
python run_pipeline.py --date 2025-03-23
```

## Querying the Database

After running the pipeline, you can query the database:

```bash
# List all available dates
python query_db.py --list-dates

# Query by date
python query_db.py --date 2025-03-23 --pretty

# Search for a specific case
python query_db.py --case "W.P.(C)-6483/2021" --pretty

# Filter by tags
python query_db.py --tag "education" --pretty
```

## Tagging Cases

You can add tags to cases in the database:

```bash
# List all tags in the database
python tag_cases.py --list-tags

# Auto-tag all cases based on patterns
python tag_cases.py --auto-tag

# Manually tag a specific case
python tag_cases.py --case-id "case_uuid" --add-tags "important,urgent"
```

## Starting the API Server

To start the API server:

```bash
# Navigate to the api directory
cd api

# Start the server
uvicorn app:app --reload
```

The API will be available at http://localhost:8000.

## Starting the Frontend

To start the frontend development server:

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies (first time only)
npm install

# Start the development server
npm start
```

The frontend will be available at http://localhost:3000.

## Parallel Processing

The scraper and processor support parallel processing for improved performance:

```bash
# Run the pipeline with parallel processing
python run_pipeline.py --parallel --download-workers 5 --processing-workers 3
```

## Common Commands

Here are some common commands for reference:

```bash
# Scrape Delhi HC cause lists for a specific date
python -m scrapers.delhi_hc.cause_lists.cause_list_scraper --date 2025-03-23

# Process PDFs with Gemini API
python -m utils.data_processor --court delhi_hc --date 2025-03-23

# Query cases with a specific tag
python query_db.py --tag "writ_petition" --pretty

# Run the complete pipeline for multiple days
python run_pipeline.py --days 7
```

## Next Steps

- Read the [User Guide](../user-guide/overview.md) for more detailed information
- Explore the [API Documentation](../user-guide/api.md)
- Learn about the [Database Integration](../user-guide/database-integration.md)
- Check out the [Developer Guide](../developer-guide/architecture.md) if you want to contribute

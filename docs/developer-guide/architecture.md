# Architecture

This document provides an overview of the architecture of the Open Court Data India project.

## System Overview

The project follows a modular architecture with several key components:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Scrapers    │    │ Data        │    │ Database    │    │ API &       │
│ Module      │───>│ Processor   │───>│ Storage     │<───│ Frontend    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## Component Architecture

### Scrapers Module

The scrapers module is responsible for downloading court data from various sources. It follows a hierarchical structure:

```
scrapers/
├── base_scraper.py         # Base scraper class
├── delhi_hc/               # Delhi High Court scrapers
│   ├── __init__.py
│   ├── base_scraper.py     # Base Delhi HC scraper
│   └── cause_lists/        # Cause list scraper
│       ├── __init__.py
│       └── cause_list_scraper.py
└── ...                     # Other court scrapers
```

Key features:
- **Inheritance Hierarchy**: Specialized scrapers inherit from more general ones
- **Consistent Interface**: All scrapers implement a common interface
- **Parallel Processing**: Efficient downloading with ThreadPoolExecutor
- **Error Handling**: Robust error handling and retry mechanisms

### Data Processor

The data processor module converts unstructured court data into structured formats using the Gemini API:

```
utils/
├── data_processor.py       # Main data processor
└── gemini_utils.py         # Gemini API utilities
```

Key features:
- **Gemini API Integration**: Uses Google's Gemini API for PDF processing
- **Structured Data Extraction**: Converts PDFs to structured JSON
- **Parallel Processing**: Processes multiple PDFs concurrently
- **Error Handling**: Handles API errors and rate limiting

### Database Storage

The database module handles storing and retrieving court data:

```
db/
├── connector.py            # Database connector class
└── schema.sql              # Database schema
```

Key features:
- **PostgreSQL Integration**: Stores data in a PostgreSQL database
- **Object-Relational Mapping**: Maps database tables to Python objects
- **Query Interface**: Provides methods for querying the database
- **Transaction Management**: Ensures data consistency

### API and Frontend

The API and frontend modules provide a user interface for accessing court data:

```
api/
└── app.py                  # FastAPI application

frontend/
├── public/                 # Static assets
└── src/                    # React components
    ├── components/         # UI components
    └── services/           # API client
```

Key features:
- **REST API**: FastAPI backend with documented endpoints
- **React Frontend**: Modern UI with React and Tailwind CSS
- **API Client**: JavaScript client for the API
- **Responsive Design**: Mobile-friendly interface

## Utilities

The project includes several utility modules:

```
utils/
├── __init__.py             # Package initialization
├── common.py               # Common utility functions
├── pdf_utils.py            # PDF processing utilities
├── html_utils.py           # HTML processing utilities
├── scraper_utils.py        # Scraper utilities
├── data_processor.py       # Data processing utilities
└── gemini_utils.py         # Gemini API utilities
```

These utilities provide reusable functions for common tasks, following the centralized utilities structure established in the project.

## Data Flow

The data flows through the system as follows:

1. **Scraping**: The scrapers download PDFs from court websites and save them to the `data/` directory
2. **Processing**: The data processor extracts structured data from the PDFs using the Gemini API
3. **Storage**: The structured data is stored in the PostgreSQL database
4. **Retrieval**: The API and frontend retrieve data from the database and present it to the user

## Parallel Processing

The project implements parallel processing at two key points:

1. **PDF Downloading**: Uses ThreadPoolExecutor to download multiple PDFs concurrently
   - Configurable max_workers (default: 5)
   - Thread-safe operations to prevent race conditions

2. **Gemini API Processing**: Uses ThreadPoolExecutor to process PDFs with Gemini API concurrently
   - Configurable max_workers (default: 3)
   - Rate limiting to avoid API throttling

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

## Configuration

The project uses a combination of:

- **config.yaml**: Main configuration file
- **.env**: Environment variables for sensitive information
- **Command-line arguments**: Override configuration for specific runs

## Pipeline Integration

The `run_pipeline.py` script integrates all components into a complete workflow:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Scrape      │───>│ Process     │───>│ Store       │───>│ Tag         │
│ Cause Lists │    │ with Gemini │    │ in Database │    │ Cases       │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

This pipeline can be run with a single command:

```bash
python run_pipeline.py
```

## Future Architecture

The project is designed to be extensible, with plans to add:

- **More Court Scrapers**: Support for additional Indian courts
- **Additional Document Types**: Support for judgments, orders, and case status
- **Advanced Search**: Full-text search and filtering
- **Analytics Dashboard**: Visualizations and statistics
- **API Authentication**: Secure access to the API
- **Distributed Processing**: Scale to handle larger volumes of data

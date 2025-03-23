# Overview

The Open Court Data India project provides tools for scraping, processing, and analyzing data from various Indian courts. This user guide will help you understand how to use the various components of the project.

## Project Components

The project consists of several key components:

1. **Scrapers**: Download court data from various sources
2. **Data Processor**: Convert unstructured data to structured formats
3. **Database Integration**: Store and query court data
4. **API**: Access court data programmatically
5. **Frontend**: User interface for browsing court data
6. **Tagging System**: Categorize cases for easier analysis

## Workflow

The typical workflow for using the project is:

1. **Scrape Data**: Use the scrapers to download court data
2. **Process Data**: Convert the data to structured formats
3. **Store Data**: Save the structured data to the database
4. **Query Data**: Retrieve and analyze the data
5. **Tag Cases**: Categorize cases for easier analysis
6. **Access Data**: Use the API or frontend to access the data

## Available Scrapers

Currently, the project includes the following scrapers:

- **Delhi High Court Cause List Scraper**: Downloads cause lists from the Delhi High Court website

## Parallel Processing

The project supports parallel processing for improved performance:

- **Parallel Downloads**: Download multiple PDFs concurrently
- **Parallel Processing**: Process multiple PDFs with Gemini API concurrently

## Data Storage

The project uses PostgreSQL for structured data storage, with tables for:

- Courts
- Benches
- Cause Lists
- Cases
- Tags

## Tagging System

The project includes a tagging system for categorizing cases:

- **Auto-Tagging**: Automatically tag cases based on patterns
- **Manual Tagging**: Manually add or remove tags from cases

## API and Frontend

The project includes a REST API and web frontend for accessing court data:

- **API**: FastAPI backend with documented endpoints
- **Frontend**: React frontend with modern UI

## Next Steps

To get started with the project, see the following guides:

- [Installation](../getting-started/installation.md)
- [Configuration](../getting-started/configuration.md)
- [Quick Start](../getting-started/quick-start.md)

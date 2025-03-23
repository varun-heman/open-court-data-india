# Scrapers API Reference

This section provides detailed API documentation for the scraper classes and functions in the Open Court Data India project.

## Delhi High Court Scrapers

### Base Scraper

The base scraper provides common functionality for all Delhi High Court scrapers. It handles:

- Setting up the output directory structure
- Managing file paths and naming conventions
- Providing common utility methods

### Cause List Scraper

The Delhi High Court Cause List Scraper is responsible for:

- Downloading cause list PDFs from the Delhi High Court website
- Extracting text from the PDFs using PyPDF2
- Parsing the extracted text to identify cases, judges, and other metadata
- Saving the structured data to JSON files
- Optionally processing the data with the Gemini API for enhanced metadata extraction

## Parallel Processing

As noted in the project memories, the Delhi HC scraper has been enhanced with parallel processing capabilities:

1. **Parallel PDF Downloading**: 
   - Using `ThreadPoolExecutor` to download multiple PDFs concurrently
   - Configurable max_workers (default: 5) to control parallelism
   - Implemented proper synchronization to avoid race conditions

2. **Parallel Gemini API Processing**:
   - Using `ThreadPoolExecutor` to process PDFs with Gemini API concurrently
   - Separate processing phase after all downloads complete
   - Configurable max_workers (default: 3) to avoid API rate limiting

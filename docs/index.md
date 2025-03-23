# Open Court Data India

A collection of scrapers and tools for accessing Indian court data.

## Overview

The Open Court Data India project provides tools for scraping, processing, and analyzing data from various Indian courts. The project aims to make court data more accessible and usable for researchers, legal professionals, and the general public.

## Key Features

### Centralized Utilities Structure

The project has been refactored to use a centralized utilities structure:

- `common.py`: General utility functions (directory management, filename cleaning, date extraction)
- `pdf_utils.py`: PDF handling functions (text extraction, structured data parsing)
- `html_utils.py`: HTML processing functions (text extraction, navigation page detection)
- `scraper_utils.py`: Scraper-specific utilities (downloading, content type checking, metadata saving)

### Consistent Directory Structure

The Delhi High Court scrapers follow a consistent directory structure for saving data:

- Base path: `/Users/varunh/Documents/ecourts-scrapers/data/`
- Delhi HC base scraper: `/Users/varunh/Documents/ecourts-scrapers/data/delhi_hc/`
- Delhi HC cause list scraper: `/Users/varunh/Documents/ecourts-scrapers/data/delhi_hc/cause_lists/`

### Parallel Processing Capabilities

The Delhi HC scraper has been enhanced with parallel processing capabilities:

- **Parallel PDF Downloading**: Using ThreadPoolExecutor with configurable workers
- **Parallel Gemini API Processing**: For enhanced metadata extraction
- **Configurable Options**: Control parallelism and resource usage

### Database Integration

The project includes PostgreSQL database integration for storing and querying court data:

- Structured schema for courts, benches, judges, cause lists, and cases
- API for programmatic access to the database
- Tagging system for categorizing and filtering cases

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

## Getting Started

Check out the [Installation Guide](getting-started/installation.md) to get started with the project.

## Quick Links

- [Installation Guide](getting-started/installation.md)
- [Quick Start Guide](getting-started/quick-start.md)
- [Database Integration](user-guide/database-integration.md)
- [API Documentation](user-guide/api.md)
- [Developer Guide](developer-guide/architecture.md)

## Disclaimer

**IMPORTANT NOTICE**: The author takes no responsibility for the quality and performance of this code. All data obtained through these scrapers is the respective copyright of its owner. The author claims ownership only of the code, not the data. Use at your own risk.

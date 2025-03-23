# Open Court Data India

A collection of scrapers and tools for accessing Indian court data.

## Overview

The Open Court Data India project provides tools for scraping, processing, and analyzing data from various Indian courts. The project aims to make court data more accessible and usable for researchers, legal professionals, and the general public.

![Project Structure](assets/images/project-structure.png)

## Features

- **Standardized Data Structure**: All scraped data follows a consistent format for easy integration
- **Metadata Extraction**: Automatically extracts metadata from court documents
- **PDF Processing**: Downloads and processes PDF documents from court websites
- **Structured Data Extraction**: Converts unstructured court data into structured formats using Google's Gemini API
- **PostgreSQL Database Integration**: Stores structured court data in a PostgreSQL database for efficient querying and analysis
- **Case Tagging System**: Automatically categorizes cases based on patterns in case numbers and titles
- **Complete Data Pipeline**: End-to-end workflow from scraping to processing, storage, and analysis
- **Parallel Processing**: Efficiently downloads and processes multiple documents concurrently
- **API and Frontend**: Access court data through a REST API and web interface

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

## Quick Links

- [Installation Guide](getting-started/installation.md)
- [Quick Start Guide](getting-started/quick-start.md)
- [Database Integration](user-guide/database-integration.md)
- [API Documentation](user-guide/api.md)
- [Developer Guide](developer-guide/architecture.md)

## Disclaimer

**IMPORTANT NOTICE**: The author takes no responsibility for the quality and performance of this code. All data obtained through these scrapers is the respective copyright of its owner. The author claims ownership only of the code, not the data. Use at your own risk.

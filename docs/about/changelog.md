# Changelog

## v0.1.0 (2025-03-23)

Initial release of the Open Court Data India project.

### Features

- **Delhi HC Cause List Scraper**
  - Download cause lists from Delhi High Court website
  - Extract metadata from PDFs
  - Parallel processing for improved performance

- **Data Processing**
  - Integration with Google's Gemini API
  - Structured data extraction from PDFs
  - Parallel processing of PDFs

- **Database Integration**
  - PostgreSQL database schema
  - Database connector class
  - Query interface

- **Tagging System**
  - Auto-tagging based on patterns
  - Manual tagging interface
  - Tag-based filtering

- **API and Frontend**
  - FastAPI backend
  - React frontend
  - API client

- **Documentation**
  - MkDocs with Material theme
  - Comprehensive user and developer guides
  - API documentation

### Known Issues

- Limited to Delhi High Court cause lists only
- Gemini API processing may have limitations for complex PDFs
- Frontend has basic functionality only

### Future Plans

- Add support for more courts
- Add support for judgments, orders, and case status
- Improve data extraction accuracy
- Enhance frontend functionality
- Add analytics and visualization tools

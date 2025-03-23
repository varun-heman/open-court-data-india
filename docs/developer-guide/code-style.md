# Code Style Guide

This document outlines the coding standards and style guidelines for the Open Court Data India project. Following these guidelines ensures consistency across the codebase and makes it easier for contributors to understand and maintain the code.

## Python Style Guide

### General Guidelines

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide for Python code.
- Use 4 spaces for indentation (no tabs).
- Keep line length to a maximum of 100 characters.
- Use meaningful variable and function names.
- Add docstrings to all modules, classes, and functions.

### Imports

- Group imports in the following order:
  1. Standard library imports
  2. Related third-party imports
  3. Local application/library specific imports
- Within each group, imports should be sorted alphabetically.

```python
# Standard library imports
import os
import sys
from datetime import datetime

# Third-party imports
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Local imports
from utils.common import create_directory
from utils.pdf_utils import extract_text_from_pdf
```

### Docstrings

- Use Google-style docstrings for all modules, classes, and functions.
- Include type hints in function signatures.

```python
def extract_date_from_filename(filename: str) -> Optional[datetime]:
    """
    Extract date from a filename.
    
    Args:
        filename: The filename to extract date from
        
    Returns:
        A datetime object if date is found, None otherwise
        
    Raises:
        ValueError: If the filename format is not recognized
    """
    # Function implementation
```

### Error Handling

- Use specific exception types rather than catching all exceptions.
- Log exceptions with appropriate context.

```python
try:
    # Code that might raise an exception
    data = process_file(file_path)
except FileNotFoundError:
    logger.error(f"File not found: {file_path}")
    # Handle the error appropriately
except ValueError as e:
    logger.error(f"Invalid data in file {file_path}: {str(e)}")
    # Handle the error appropriately
```

## SQL Style Guide

- Use uppercase for SQL keywords (SELECT, INSERT, etc.).
- Use snake_case for table and column names.
- Include comments for complex queries.

```sql
-- Get all cases with a specific tag
SELECT c.id, c.case_number, c.title
FROM cases c
JOIN case_tags ct ON c.id = ct.case_id
JOIN tags t ON ct.tag_id = t.id
WHERE t.name = 'important';
```

## Git Commit Messages

- Use the imperative mood in the subject line.
- Limit the subject line to 50 characters.
- Capitalize the subject line.
- Do not end the subject line with a period.
- Separate subject from body with a blank line.
- Wrap the body at 72 characters.
- Use the body to explain what and why vs. how.

Example:
```
Add parallel processing to Delhi HC scraper

- Implement ThreadPoolExecutor for PDF downloads
- Add configuration options for controlling parallelism
- Ensure thread safety for shared resources
```

## Code Organization

- Keep modules focused on a single responsibility.
- Use classes to encapsulate related functionality.
- Separate utility functions into appropriate modules.
- Follow the project's directory structure conventions.

By following these guidelines, you'll help maintain a clean, consistent, and maintainable codebase for the Open Court Data India project.

# Database Integration

This guide explains how the Open Court Data India project integrates with PostgreSQL to store and retrieve court data.

## System Architecture

The database integration follows this architecture:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Delhi HC    │    │ Gemini API  │    │ PostgreSQL  │    │ Frontend UI │
│ Scraper     │───>│ Processing  │───>│ Database    │<───│ (React)     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                           ▲
                                           │
                                      ┌────┴────┐
                                      │ FastAPI │
                                      │ Backend │
                                      └─────────┘
```

## Database Schema

The PostgreSQL database uses the following schema:

```sql
-- Courts table
CREATE TABLE courts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,
    website VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Benches table
CREATE TABLE benches (
    id SERIAL PRIMARY KEY,
    court_id INTEGER REFERENCES courts(id),
    bench_number VARCHAR(50) NOT NULL,
    judges TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(court_id, bench_number)
);

-- Cause lists table
CREATE TABLE cause_lists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    court_id INTEGER REFERENCES courts(id),
    bench_id INTEGER REFERENCES benches(id),
    list_date DATE NOT NULL,
    pdf_path TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(court_id, bench_id, list_date)
);

-- Cases table
CREATE TABLE cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cause_list_id UUID REFERENCES cause_lists(id),
    case_number VARCHAR(255) NOT NULL,
    title TEXT,
    item_number VARCHAR(50),
    file_number VARCHAR(255),
    petitioner_adv TEXT,
    respondent_adv TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(cause_list_id, case_number)
);

-- Tags table
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Case tags junction table
CREATE TABLE case_tags (
    case_id UUID REFERENCES cases(id),
    tag_id INTEGER REFERENCES tags(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (case_id, tag_id)
);
```

## Database Connector

The `DBConnector` class in `db/connector.py` provides a simple interface for interacting with the database. It handles:

- Connecting to the database
- Creating and retrieving courts, benches, cause lists, and cases
- Managing tags and case-tag relationships
- Querying the database with various filters

### Basic Usage

```python
from db.connector import DBConnector

# Initialize the connector
db = DBConnector()

# Connect to the database
db.connect()

# Get or create a court
court_id = db.get_or_create_court("Delhi High Court", "delhi_hc")

# Get or create a bench
bench_id = db.get_or_create_bench(court_id, "COURT NO. 01", "HON'BLE CHIEF JUSTICE")

# Create a cause list
cause_list_id = db.create_cause_list(court_id, bench_id, "2025-03-23", "path/to/pdf")

# Create a case
case_id = db.create_case(
    cause_list_id,
    "W.P.(C)-6483/2021",
    title="John Doe vs State",
    item_number="1",
    file_number="F-123",
    petitioner_adv="Mr. A",
    respondent_adv="Ms. B",
    tags=["writ_petition", "education"]
)

# Close the connection
db.close()
```

## Environment Variables

The database connector uses the following environment variables:

```
DB_USER=ecourts
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ecourts
```

You can set these in a `.env` file in the project root or export them directly in your shell.

## Query Tools

The project includes several tools for querying the database:

### Command Line Interface

The `query_db.py` script provides a command-line interface for querying the database:

```bash
# List all available dates
python query_db.py --list-dates

# Query by date
python query_db.py --date 2025-03-23 --pretty

# Filter by bench number
python query_db.py --date 2025-03-23 --bench "COURT NO. 01" --pretty

# Search for a specific case
python query_db.py --case "W.P.(C)-6483/2021" --pretty

# Filter by tags
python query_db.py --tag "education" --pretty

# Output as JSON
python query_db.py --date 2025-03-23 --json
```

### API Endpoints

The FastAPI backend provides the following endpoints for querying the database:

- `GET /api/courts`: List all available courts
- `GET /api/courts/{court_code}/dates`: List available dates for a court
- `GET /api/courts/{court_code}/cause_lists/{date}`: Get cause lists for a court on a specific date
- `GET /api/cases/{case_id}`: Get details of a specific case
- `GET /api/cases/search`: Search for cases with various filters

## Tagging System

The database includes a tagging system for categorizing cases:

### Auto-Tagging

The `tag_cases.py` script can automatically tag cases based on patterns in case numbers and titles:

```bash
# Auto-tag all cases based on patterns
python tag_cases.py --auto-tag
```

Auto-tagging rules include:
- Case numbers with "W.P." are tagged as "writ_petition"
- Case numbers with "CRL.M.C." are tagged as "criminal"
- Case numbers with "CS(COMM)" are tagged as "commercial"
- Titles containing "education" are tagged as "education"
- And many more predefined patterns

### Manual Tagging

You can also manually tag cases:

```bash
# Manually tag a specific case
python tag_cases.py --case-id "case_uuid" --add-tags "important,urgent"

# Remove tags from a case
python tag_cases.py --case-id "case_uuid" --remove-tags "urgent"
```

## Data Processing Pipeline

The complete data pipeline integrates with the database at multiple points:

1. **Scraping**: Downloads PDFs and saves their paths in the database
2. **Processing**: Extracts structured data from PDFs using Gemini API
3. **Storage**: Stores the structured data in the database
4. **Tagging**: Automatically tags cases based on patterns

You can run the complete pipeline with:

```bash
python run_pipeline.py
```

## Parallel Processing

The data processing pipeline supports parallel processing for improved performance, following the architecture established in the project:

```bash
# Run the pipeline with parallel processing
python run_pipeline.py --parallel --download-workers 5 --processing-workers 3
```

This leverages the `ThreadPoolExecutor` for both PDF downloading and Gemini API processing, with configurable worker counts to optimize performance while avoiding API rate limits.

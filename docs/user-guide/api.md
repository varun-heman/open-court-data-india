# API Documentation

The Open Court Data India project provides a REST API for accessing court data programmatically. This guide explains how to use the API.

## API Overview

The API is built with FastAPI and provides endpoints for:

- Listing available courts
- Listing available dates for a court
- Retrieving cause lists for a court on a specific date
- Searching for cases with various filters
- Retrieving details of a specific case
- Managing tags for cases

## API Base URL

When running locally, the API is available at:

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. This may change in future versions.

## Endpoints

### Courts

#### List Courts

```
GET /api/courts
```

Returns a list of all available courts.

**Example Response:**

```json
[
  {
    "id": 1,
    "name": "Delhi High Court",
    "code": "delhi_hc",
    "website": "https://delhihighcourt.nic.in"
  }
]
```

### Dates

#### List Available Dates

```
GET /api/courts/{court_code}/dates
```

Returns a list of dates for which data is available for the specified court.

**Parameters:**

- `court_code`: The code of the court (e.g., `delhi_hc`)

**Example Response:**

```json
[
  "2025-03-23",
  "2025-03-22",
  "2025-03-21"
]
```

### Cause Lists

#### Get Cause Lists

```
GET /api/courts/{court_code}/cause_lists/{date}
```

Returns cause lists for the specified court on the specified date.

**Parameters:**

- `court_code`: The code of the court (e.g., `delhi_hc`)
- `date`: The date in YYYY-MM-DD format

**Example Response:**

```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "court": {
      "id": 1,
      "name": "Delhi High Court",
      "code": "delhi_hc"
    },
    "bench": {
      "id": 1,
      "bench_number": "COURT NO. 01",
      "judges": "HON'BLE CHIEF JUSTICE"
    },
    "list_date": "2025-03-23",
    "pdf_path": "data/delhi_hc/cause_lists/2025-03-23/pdf1.pdf",
    "cases": [
      {
        "id": "123e4567-e89b-12d3-a456-426614174001",
        "case_number": "W.P.(C)-6483/2021",
        "title": "John Doe vs State",
        "item_number": "1",
        "file_number": "F-123",
        "petitioner_adv": "Mr. A",
        "respondent_adv": "Ms. B",
        "tags": ["writ_petition", "education"]
      }
    ]
  }
]
```

### Cases

#### Get Case Details

```
GET /api/cases/{case_id}
```

Returns details of a specific case.

**Parameters:**

- `case_id`: The UUID of the case

**Example Response:**

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174001",
  "case_number": "W.P.(C)-6483/2021",
  "title": "John Doe vs State",
  "item_number": "1",
  "file_number": "F-123",
  "petitioner_adv": "Mr. A",
  "respondent_adv": "Ms. B",
  "cause_list": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "court": {
      "id": 1,
      "name": "Delhi High Court",
      "code": "delhi_hc"
    },
    "bench": {
      "id": 1,
      "bench_number": "COURT NO. 01",
      "judges": "HON'BLE CHIEF JUSTICE"
    },
    "list_date": "2025-03-23"
  },
  "tags": ["writ_petition", "education"]
}
```

#### Search Cases

```
GET /api/cases/search
```

Searches for cases with various filters.

**Query Parameters:**

- `court_code`: Filter by court code (e.g., `delhi_hc`)
- `date`: Filter by date (YYYY-MM-DD)
- `bench`: Filter by bench number
- `case_number`: Search for a specific case number
- `title`: Search in case titles
- `tag`: Filter by tag
- `limit`: Maximum number of results to return (default: 100)
- `offset`: Offset for pagination (default: 0)

**Example Request:**

```
GET /api/cases/search?court_code=delhi_hc&date=2025-03-23&tag=writ_petition
```

**Example Response:**

```json
{
  "total": 1,
  "offset": 0,
  "limit": 100,
  "results": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174001",
      "case_number": "W.P.(C)-6483/2021",
      "title": "John Doe vs State",
      "item_number": "1",
      "file_number": "F-123",
      "petitioner_adv": "Mr. A",
      "respondent_adv": "Ms. B",
      "cause_list": {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "court": {
          "id": 1,
          "name": "Delhi High Court",
          "code": "delhi_hc"
        },
        "bench": {
          "id": 1,
          "bench_number": "COURT NO. 01",
          "judges": "HON'BLE CHIEF JUSTICE"
        },
        "list_date": "2025-03-23"
      },
      "tags": ["writ_petition", "education"]
    }
  ]
}
```

### Tags

#### List Tags

```
GET /api/tags
```

Returns a list of all available tags.

**Example Response:**

```json
[
  {
    "id": 1,
    "name": "writ_petition"
  },
  {
    "id": 2,
    "name": "education"
  }
]
```

#### Add Tag to Case

```
POST /api/cases/{case_id}/tags
```

Adds a tag to a case.

**Parameters:**

- `case_id`: The UUID of the case

**Request Body:**

```json
{
  "tag": "important"
}
```

**Example Response:**

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174001",
  "tags": ["writ_petition", "education", "important"]
}
```

#### Remove Tag from Case

```
DELETE /api/cases/{case_id}/tags/{tag_name}
```

Removes a tag from a case.

**Parameters:**

- `case_id`: The UUID of the case
- `tag_name`: The name of the tag to remove

**Example Response:**

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174001",
  "tags": ["writ_petition", "education"]
}
```

## Error Handling

The API returns appropriate HTTP status codes for errors:

- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error responses include a JSON body with details:

```json
{
  "detail": "Case not found"
}
```

## Rate Limiting

Currently, the API does not implement rate limiting. This may change in future versions.

## Using the API with Python

Here's an example of using the API with Python's `requests` library:

```python
import requests

# Base URL
base_url = "http://localhost:8000"

# List courts
response = requests.get(f"{base_url}/api/courts")
courts = response.json()
print(courts)

# List available dates for Delhi HC
response = requests.get(f"{base_url}/api/courts/delhi_hc/dates")
dates = response.json()
print(dates)

# Get cause lists for a specific date
response = requests.get(f"{base_url}/api/courts/delhi_hc/cause_lists/2025-03-23")
cause_lists = response.json()
print(cause_lists)

# Search for cases with a specific tag
response = requests.get(f"{base_url}/api/cases/search", params={
    "court_code": "delhi_hc",
    "tag": "writ_petition"
})
cases = response.json()
print(cases)
```

## Using the API with JavaScript

Here's an example of using the API with JavaScript's `fetch` API:

```javascript
// Base URL
const baseUrl = "http://localhost:8000";

// List courts
fetch(`${baseUrl}/api/courts`)
  .then(response => response.json())
  .then(courts => console.log(courts));

// List available dates for Delhi HC
fetch(`${baseUrl}/api/courts/delhi_hc/dates`)
  .then(response => response.json())
  .then(dates => console.log(dates));

// Get cause lists for a specific date
fetch(`${baseUrl}/api/courts/delhi_hc/cause_lists/2025-03-23`)
  .then(response => response.json())
  .then(causeLists => console.log(causeLists));

// Search for cases with a specific tag
fetch(`${baseUrl}/api/cases/search?court_code=delhi_hc&tag=writ_petition`)
  .then(response => response.json())
  .then(cases => console.log(cases));
```

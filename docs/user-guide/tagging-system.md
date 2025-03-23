# Tagging System

The Open Court Data India project includes a tagging system for categorizing cases based on their characteristics. This guide explains how to use the tagging system.

## Overview

The tagging system allows you to:

- Automatically tag cases based on patterns in case numbers and titles
- Manually add or remove tags from cases
- Filter cases by tags when querying the database
- Analyze case distributions by tag

## Tag Types

Tags can be used to categorize cases in various ways:

- **Case Type**: writ_petition, criminal, civil, commercial, etc.
- **Subject Matter**: education, property, taxation, etc.
- **Status**: urgent, important, disposed, etc.
- **Custom Tags**: Any user-defined categories

## Auto-Tagging

The project includes an auto-tagging system that can automatically assign tags to cases based on patterns in case numbers and titles.

### Running Auto-Tagging

To run auto-tagging on all cases in the database:

```bash
python tag_cases.py --auto-tag
```

### Auto-Tagging Rules

The auto-tagging system uses the following rules:

#### Case Number Patterns

- **Writ Petitions**: Case numbers containing "W.P." are tagged as "writ_petition"
- **Criminal Cases**: Case numbers containing "CRL.M.C.", "CRL.A.", etc. are tagged as "criminal"
- **Civil Cases**: Case numbers containing "CS", "RFA", etc. are tagged as "civil"
- **Commercial Cases**: Case numbers containing "CS(COMM)" are tagged as "commercial"
- **Appeals**: Case numbers containing "LPA", "RFA", etc. are tagged as "appeal"

#### Title Patterns

- **Education**: Titles containing "education", "school", "university", etc. are tagged as "education"
- **Property**: Titles containing "property", "land", "rent", etc. are tagged as "property"
- **Taxation**: Titles containing "tax", "GST", "income tax", etc. are tagged as "taxation"
- **Employment**: Titles containing "employment", "service", "pension", etc. are tagged as "employment"

### Customizing Auto-Tagging Rules

You can customize the auto-tagging rules by editing the `tag_cases.py` script. Look for the `auto_tag_cases` function and modify the pattern matching rules.

## Manual Tagging

You can manually add or remove tags from cases using the `tag_cases.py` script.

### Listing Tags

To list all tags in the database:

```bash
python tag_cases.py --list-tags
```

### Adding Tags

To add tags to a case:

```bash
python tag_cases.py --case-id "case_uuid" --add-tags "important,urgent"
```

You can specify multiple tags separated by commas.

### Removing Tags

To remove tags from a case:

```bash
python tag_cases.py --case-id "case_uuid" --remove-tags "urgent"
```

### Finding a Case ID

To find the UUID of a case, you can use the `query_db.py` script:

```bash
python query_db.py --case "W.P.(C)-6483/2021" --pretty
```

This will display the case details, including its UUID.

## Querying by Tags

You can filter cases by tags when querying the database:

```bash
# Query cases with a specific tag
python query_db.py --tag "writ_petition" --pretty

# Combine with other filters
python query_db.py --date 2025-03-23 --tag "writ_petition" --pretty
```

## API Integration

The tagging system is integrated with the API:

### Listing Tags

```
GET /api/tags
```

Returns a list of all available tags.

### Adding Tags

```
POST /api/cases/{case_id}/tags
```

Adds a tag to a case.

### Removing Tags

```
DELETE /api/cases/{case_id}/tags/{tag_name}
```

Removes a tag from a case.

### Filtering by Tags

```
GET /api/cases/search?tag=writ_petition
```

Returns cases with the specified tag.

## Frontend Integration

The frontend includes a tagging interface:

- View tags for each case
- Add or remove tags from cases
- Filter cases by tags
- View tag statistics

## Tag Analysis

The tagging system enables various analyses:

- Distribution of case types
- Subject matter trends over time
- Identification of important or urgent cases
- Custom categorizations for research purposes

## Database Schema

The tagging system uses the following database schema:

```sql
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

This schema allows for a many-to-many relationship between cases and tags.

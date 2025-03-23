# Installation

This guide will help you set up the Open Court Data India project on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8 or higher
- PostgreSQL 12 or higher (optional, for database integration)
- Node.js 16 or higher (optional, for frontend development)

## Basic Installation

1. Clone the repository:

```bash
git clone https://github.com/varun-heman/open-court-data-india.git
cd open-court-data-india
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Database Setup (Optional)

If you want to use the database integration features:

1. Install PostgreSQL if not already installed:

```bash
# macOS (using Homebrew)
brew install postgresql
brew services start postgresql

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

2. Create a database and user:

```bash
# Connect to PostgreSQL
psql postgres

# Create user and database
CREATE USER ecourts WITH PASSWORD 'your_password';
CREATE DATABASE ecourts OWNER ecourts;
\q
```

3. Initialize the database schema:

```bash
# Set environment variables
export DB_USER=ecourts
export DB_PASSWORD=your_password
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=ecourts

# Initialize database schema
psql -U ecourts -d ecourts -f db/schema.sql
```

4. Create a `.env` file in the project root with your database credentials:

```
DB_USER=ecourts
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ecourts
```

## Gemini API Setup

To use the Gemini API for processing PDFs:

1. Obtain a Gemini API key from [Google AI Studio](https://ai.google.dev/)

2. Add your API key to the `.env` file:

```
GEMINI_API_KEY=your_gemini_api_key
```

## Frontend Setup (Optional)

If you want to use the frontend:

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install the required dependencies:

```bash
npm install
```

3. Start the development server:

```bash
npm start
```

## Documentation Setup (Optional)

To build and serve the documentation locally:

1. Install the documentation dependencies:

```bash
pip install mkdocs mkdocs-material pymdown-extensions mkdocstrings mkdocstrings-python
```

2. Serve the documentation:

```bash
mkdocs serve
```

3. Open your browser to http://localhost:8000 to view the documentation.

## Verifying the Installation

To verify that everything is set up correctly:

1. Run the basic scraper:

```bash
python -m scrapers.delhi_hc.cause_lists.cause_list_scraper --debug
```

2. If you've set up the database, run the complete pipeline:

```bash
python run_pipeline.py --debug
```

If both commands run without errors, your installation is successful!

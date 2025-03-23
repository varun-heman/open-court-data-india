#!/usr/bin/env python3
"""
Script to run the Delhi HC cause list scraper with database integration.

This script runs the Delhi HC cause list scraper, processes the PDFs with Gemini API,
and stores the structured data in the PostgreSQL database for the UI to access.
"""

import os
import sys
import logging
import argparse
from datetime import datetime
import subprocess
import time

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

from db.connector import DBConnector
from scrapers.delhi_hc.cause_lists.db_integrated_scraper import DelhiHCCauseListDBScraper
from utils.data_processor import CauseListProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_database(db_host, db_port, db_name, db_user, db_password, schema_file):
    """
    Set up the database with the schema.
    
    Args:
        db_host: Database host
        db_port: Database port
        db_name: Database name
        db_user: Database user
        db_password: Database password
        schema_file: Path to schema file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Check if database exists
        check_db_cmd = [
            "psql",
            "-h", db_host,
            "-p", db_port,
            "-U", db_user,
            "-c", f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"
        ]
        
        # Set PGPASSWORD environment variable for password
        env = os.environ.copy()
        if db_password:
            env["PGPASSWORD"] = db_password
        
        result = subprocess.run(
            check_db_cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Create database if it doesn't exist
        if "1 row" not in result.stdout:
            logger.info(f"Creating database: {db_name}")
            create_db_cmd = [
                "psql",
                "-h", db_host,
                "-p", db_port,
                "-U", db_user,
                "-c", f"CREATE DATABASE {db_name}"
            ]
            
            subprocess.run(
                create_db_cmd,
                env=env,
                check=True
            )
        
        # Apply schema
        logger.info(f"Applying schema from: {schema_file}")
        apply_schema_cmd = [
            "psql",
            "-h", db_host,
            "-p", db_port,
            "-U", db_user,
            "-d", db_name,
            "-f", schema_file
        ]
        
        subprocess.run(
            apply_schema_cmd,
            env=env,
            check=True
        )
        
        logger.info("Database setup completed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Error setting up database: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error setting up database: {e}")
        return False

def run_scraper(args):
    """
    Run the Delhi HC cause list scraper with database integration.
    
    Args:
        args: Command-line arguments
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create database connector
        db_connector = DBConnector(
            host=args.db_host,
            port=args.db_port,
            dbname=args.db_name,
            user=args.db_user,
            password=args.db_password
        )
        
        # Test database connection
        if not db_connector.connect():
            logger.error("Failed to connect to database")
            return False
        
        # Create and run scraper
        scraper = DelhiHCCauseListDBScraper(
            output_dir=args.output,
            config_file=args.config,
            db_connector=db_connector
        )
        
        if args.debug:
            scraper.logger.setLevel(logging.DEBUG)
        
        # Run scraper
        metadata = scraper.run()
        
        if not metadata:
            logger.warning("No cause lists were scraped")
        else:
            logger.info(f"Successfully scraped {len(metadata)} cause lists")
        
        return True
        
    except Exception as e:
        logger.error(f"Error running scraper: {e}", exc_info=True)
        return False

def process_existing_pdfs(args):
    """
    Process existing PDFs in the output directory.
    
    Args:
        args: Command-line arguments
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create database connector
        db_connector = DBConnector(
            host=args.db_host,
            port=args.db_port,
            dbname=args.db_name,
            user=args.db_user,
            password=args.db_password
        )
        
        # Test database connection
        if not db_connector.connect():
            logger.error("Failed to connect to database")
            return False
        
        # Create data processor
        data_processor = CauseListProcessor(db_connector, "delhi_hc")
        
        # Process PDFs in output directory
        output_dir = args.output or os.path.join(project_root, "data", "delhi_hc", "cause_lists")
        
        if args.date:
            # Process PDFs for specific date
            date_dir = os.path.join(output_dir, args.date)
            if not os.path.exists(date_dir):
                logger.error(f"Directory does not exist: {date_dir}")
                return False
            
            logger.info(f"Processing PDFs in: {date_dir}")
            results = data_processor.process_directory(date_dir)
            
            if not results:
                logger.warning(f"No PDFs were processed in: {date_dir}")
            else:
                logger.info(f"Successfully processed {len(results)} PDFs in: {date_dir}")
        else:
            # Process PDFs in all date directories
            processed_count = 0
            
            for date_dir in os.listdir(output_dir):
                date_path = os.path.join(output_dir, date_dir)
                
                # Skip non-directories and non-date directories
                if not os.path.isdir(date_path) or not date_dir.startswith("20"):
                    continue
                
                logger.info(f"Processing PDFs in: {date_path}")
                results = data_processor.process_directory(date_path)
                
                if results:
                    processed_count += len(results)
            
            if processed_count == 0:
                logger.warning("No PDFs were processed")
            else:
                logger.info(f"Successfully processed {processed_count} PDFs")
        
        return True
        
    except Exception as e:
        logger.error(f"Error processing existing PDFs: {e}", exc_info=True)
        return False

def run_api_server(args):
    """
    Run the API server.
    
    Args:
        args: Command-line arguments
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Set environment variables for database connection
        env = os.environ.copy()
        env["DB_HOST"] = args.db_host
        env["DB_PORT"] = args.db_port
        env["DB_NAME"] = args.db_name
        env["DB_USER"] = args.db_user
        if args.db_password:
            env["DB_PASSWORD"] = args.db_password
        
        # Run API server
        api_script = os.path.join(project_root, "api", "app.py")
        
        logger.info(f"Starting API server on port {args.port}")
        api_cmd = [
            "uvicorn",
            "api.app:app",
            "--host", "0.0.0.0",
            "--port", str(args.port),
            "--reload" if args.debug else ""
        ]
        
        # Remove empty arguments
        api_cmd = [arg for arg in api_cmd if arg]
        
        # Run API server in a subprocess
        process = subprocess.Popen(
            api_cmd,
            env=env,
            cwd=project_root
        )
        
        logger.info(f"API server started with PID: {process.pid}")
        
        # Wait for API server to start
        time.sleep(2)
        
        # Check if API server is running
        if process.poll() is not None:
            logger.error("API server failed to start")
            return False
        
        logger.info(f"API server is running on http://localhost:{args.port}")
        logger.info("Press Ctrl+C to stop the server")
        
        # Wait for user to press Ctrl+C
        try:
            process.wait()
        except KeyboardInterrupt:
            logger.info("Stopping API server")
            process.terminate()
            process.wait()
        
        return True
        
    except Exception as e:
        logger.error(f"Error running API server: {e}", exc_info=True)
        return False

def main():
    """
    Main function.
    """
    parser = argparse.ArgumentParser(
        description="Run the Delhi HC cause list scraper with database integration"
    )
    
    # Database options
    parser.add_argument("--db-host", default="localhost", help="Database host")
    parser.add_argument("--db-port", default="5432", help="Database port")
    parser.add_argument("--db-name", default="ecourts", help="Database name")
    parser.add_argument("--db-user", default="postgres", help="Database user")
    parser.add_argument("--db-password", help="Database password")
    
    # Scraper options
    parser.add_argument("--output", "-o", help="Output directory")
    parser.add_argument("--config", "-c", help="Configuration file")
    parser.add_argument("--date", "-d", help="Date in YYYY-MM-DD format (for processing existing PDFs)")
    
    # API options
    parser.add_argument("--port", "-p", type=int, default=8000, help="API server port")
    
    # General options
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--setup-db", action="store_true", help="Set up database schema")
    parser.add_argument("--scrape", action="store_true", help="Run scraper")
    parser.add_argument("--process", action="store_true", help="Process existing PDFs")
    parser.add_argument("--api", action="store_true", help="Run API server")
    
    args = parser.parse_args()
    
    # Set logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Set up database schema
    if args.setup_db:
        schema_file = os.path.join(project_root, "db", "schema.sql")
        if not os.path.exists(schema_file):
            logger.error(f"Schema file not found: {schema_file}")
            return 1
        
        if not setup_database(
            args.db_host, args.db_port, args.db_name, args.db_user, args.db_password, schema_file
        ):
            logger.error("Failed to set up database")
            return 1
    
    # Run scraper
    if args.scrape:
        if not run_scraper(args):
            logger.error("Failed to run scraper")
            return 1
    
    # Process existing PDFs
    if args.process:
        if not process_existing_pdfs(args):
            logger.error("Failed to process existing PDFs")
            return 1
    
    # Run API server
    if args.api:
        if not run_api_server(args):
            logger.error("Failed to run API server")
            return 1
    
    # If no action specified, show help
    if not (args.setup_db or args.scrape or args.process or args.api):
        parser.print_help()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Run the complete Delhi HC cause list data pipeline.

This script runs the entire pipeline:
1. Scrape Delhi HC cause lists
2. Process PDFs with Gemini API
3. Store data in PostgreSQL database
4. Tag cases automatically
"""

import argparse
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from dotenv import load_dotenv

# Import local modules
from utils.data_processor import CauseListProcessor
from db.connector import DBConnector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run the Delhi HC cause list data pipeline")
    
    # Main command options
    parser.add_argument("--date", type=str, help="Date to process (YYYY-MM-DD, default: today)")
    parser.add_argument("--days", type=int, default=1, help="Number of days to scrape (default: 1)")
    parser.add_argument("--no-scrape", action="store_true", help="Skip scraping step")
    parser.add_argument("--no-process", action="store_true", help="Skip processing step")
    parser.add_argument("--no-tag", action="store_true", help="Skip tagging step")
    parser.add_argument("--parallel", action="store_true", help="Enable parallel processing")
    parser.add_argument("--download-workers", type=int, default=5, help="Number of download workers (default: 5)")
    parser.add_argument("--processing-workers", type=int, default=3, help="Number of processing workers (default: 3)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    return parser.parse_args()


def run_scraper(date_str: Optional[str] = None, days: int = 1) -> None:
    """Run the Delhi HC cause list scraper."""
    from scrapers.delhi_hc.cause_list import DelhiHCCauseListScraper
    
    logger.info("Starting Delhi HC cause list scraper")
    
    # Initialize scraper
    scraper = DelhiHCCauseListScraper()
    
    # Set date range
    if date_str:
        try:
            start_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            logger.error(f"Invalid date format: {date_str}. Use YYYY-MM-DD")
            return
    else:
        start_date = datetime.now().date()
    
    # Run scraper for each day
    for i in range(days):
        current_date = start_date - timedelta(days=i)
        date_str = current_date.strftime("%Y-%m-%d")
        
        logger.info(f"Scraping Delhi HC cause lists for date: {date_str}")
        try:
            scraper.scrape_date(date_str)
        except Exception as e:
            logger.error(f"Error scraping date {date_str}: {e}")
    
    logger.info("Delhi HC cause list scraper completed")


def run_processor(date_str: Optional[str] = None, parallel: bool = False, processing_workers: int = 3) -> None:
    """Run the Delhi HC cause list data processor."""
    logger.info("Starting Delhi HC cause list data processor")
    
    # Initialize processor
    processor = CauseListProcessor(court_code="delhi_hc")
    
    # Determine directory to process
    if date_str:
        directory_path = os.path.join('data', 'delhi_hc', 'cause_lists', date_str)
    else:
        # Get today's date
        today = datetime.now().strftime('%Y-%m-%d')
        directory_path = os.path.join('data', 'delhi_hc', 'cause_lists', today)
    
    # Check if directory exists
    if not os.path.exists(directory_path):
        logger.error(f"Directory not found: {directory_path}")
        return
    
    logger.info(f"Processing directory: {directory_path}")
    
    # Process directory
    try:
        results = processor.process_directory(directory_path)
        logger.info(f"Processed {len(results)} files successfully")
    except Exception as e:
        logger.error(f"Error processing data: {e}")
        return
    
    logger.info("Delhi HC cause list data processor completed")


def run_tagger() -> None:
    """Run the auto-tagger for cases."""
    logger.info("Starting case auto-tagger")
    
    # Import here to avoid circular imports
    from tag_cases import auto_tag_cases
    
    # Initialize database connector
    db = DBConnector()
    
    try:
        # Run auto-tagger
        auto_tag_cases(db)
    except Exception as e:
        logger.error(f"Error tagging cases: {e}")
    finally:
        # Close database connection
        if db:
            db.close()
    
    logger.info("Case auto-tagger completed")


def main() -> None:
    """Main function."""
    # Load environment variables
    load_dotenv()
    
    # Parse arguments
    args = parse_args()
    
    # Set logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    start_time = time.time()
    logger.info("Starting Delhi HC cause list data pipeline")
    
    # Step 1: Scrape Delhi HC cause lists
    if not args.no_scrape:
        run_scraper(args.date, args.days)
    else:
        logger.info("Skipping scraping step")
    
    # Step 2: Process PDFs with Gemini API
    if not args.no_process:
        run_processor(args.date, args.parallel, args.processing_workers)
    else:
        logger.info("Skipping processing step")
    
    # Step 3: Tag cases automatically
    if not args.no_tag:
        run_tagger()
    else:
        logger.info("Skipping tagging step")
    
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    logger.info(f"Delhi HC cause list data pipeline completed in {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Query the database for Delhi High Court cause list data.

This script provides a simple command-line interface to query
the database for cause lists and cases.
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Union

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
    parser = argparse.ArgumentParser(description="Query the database for Delhi High Court cause list data")
    
    # Main command options
    parser.add_argument("--date", type=str, help="Date to query (YYYY-MM-DD)")
    parser.add_argument("--list-dates", action="store_true", help="List available dates")
    parser.add_argument("--bench", type=str, help="Bench number to filter by")
    parser.add_argument("--case", type=str, help="Case number to search for")
    parser.add_argument("--tag", type=str, help="Tag to filter by")
    parser.add_argument("--output", "-o", type=str, help="Output file path (JSON)")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    return parser.parse_args()


def format_date(date_obj: Union[str, date]) -> str:
    """Format date as YYYY-MM-DD."""
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.strptime(date_obj, "%Y-%m-%d").date()
        except ValueError:
            return date_obj
    
    if isinstance(date_obj, date):
        return date_obj.strftime("%Y-%m-%d")
    
    return str(date_obj)


def list_available_dates(db: DBConnector) -> None:
    """List available dates in the database."""
    dates = db.get_available_dates("delhi_hc")
    
    if not dates:
        logger.info("No dates available in the database")
        return
    
    logger.info(f"Found {len(dates)} dates in the database:")
    for date_str in sorted(dates, reverse=True):
        logger.info(f"  - {date_str}")


def query_cause_lists_by_date(db: DBConnector, query_date: str) -> List[Dict[str, Any]]:
    """Query cause lists by date."""
    cause_lists = db.get_cause_lists_by_date("delhi_hc", query_date)
    
    if not cause_lists:
        logger.info(f"No cause lists found for date: {query_date}")
        return []
    
    logger.info(f"Found {len(cause_lists)} cause lists for date: {query_date}")
    
    # Count total cases
    total_cases = sum(len(cl.get("cases", [])) for cl in cause_lists)
    logger.info(f"Total cases: {total_cases}")
    
    return cause_lists


def search_case_by_number(db: DBConnector, case_number: str) -> List[Dict[str, Any]]:
    """Search for a case by case number."""
    # Connect to the database
    if not db.conn:
        db.connect()
    
    # Query to search for cases by case number (partial match)
    query = """
    SELECT c.id, c.case_number, c.title, c.item_number, c.file_number, 
           c.petitioner_adv, c.respondent_adv, c.created_at,
           cl.list_date, cl.list_type, cl.pdf_path,
           cb.bench_number, cb.judges,
           ct.name as court_name
    FROM cases c
    JOIN cause_lists cl ON c.cause_list_id = cl.id
    JOIN court_benches cb ON cl.bench_id = cb.id
    JOIN courts ct ON cl.court_id = ct.id
    WHERE c.case_number ILIKE %s
    ORDER BY cl.list_date DESC, cb.bench_number
    """
    
    results = db.execute(query, (f"%{case_number}%",))
    
    if not results:
        logger.info(f"No cases found matching: {case_number}")
        return []
    
    logger.info(f"Found {len(results)} cases matching: {case_number}")
    
    # Format results
    formatted_results = []
    for row in results:
        formatted_results.append({
            "case_id": str(row["id"]),
            "case_number": row["case_number"],
            "title": row["title"],
            "item_number": row["item_number"],
            "file_number": row["file_number"],
            "petitioner_adv": row["petitioner_adv"],
            "respondent_adv": row["respondent_adv"],
            "court": row["court_name"],
            "bench": row["bench_number"],
            "judges": row["judges"],
            "list_date": format_date(row["list_date"]),
            "list_type": row["list_type"],
            "pdf_path": row["pdf_path"],
            "created_at": row["created_at"].isoformat() if row["created_at"] else None
        })
    
    return formatted_results


def filter_cases_by_tag(db: DBConnector, tag_name: str) -> List[Dict[str, Any]]:
    """Filter cases by tag."""
    # Connect to the database
    if not db.conn:
        db.connect()
    
    # Query to filter cases by tag
    query = """
    SELECT c.id, c.case_number, c.title, c.item_number, c.file_number, 
           c.petitioner_adv, c.respondent_adv, c.created_at,
           cl.list_date, cl.list_type, cl.pdf_path,
           cb.bench_number, cb.judges,
           ct.name as court_name
    FROM cases c
    JOIN cause_lists cl ON c.cause_list_id = cl.id
    JOIN court_benches cb ON cl.bench_id = cb.id
    JOIN courts ct ON cl.court_id = ct.id
    JOIN case_tag_mappings ctm ON c.id = ctm.case_id
    JOIN case_tags t ON ctm.tag_id = t.id
    WHERE t.name ILIKE %s
    ORDER BY cl.list_date DESC, cb.bench_number
    """
    
    results = db.execute(query, (f"%{tag_name}%",))
    
    if not results:
        logger.info(f"No cases found with tag: {tag_name}")
        return []
    
    logger.info(f"Found {len(results)} cases with tag: {tag_name}")
    
    # Format results
    formatted_results = []
    for row in results:
        formatted_results.append({
            "case_id": str(row["id"]),
            "case_number": row["case_number"],
            "title": row["title"],
            "item_number": row["item_number"],
            "file_number": row["file_number"],
            "petitioner_adv": row["petitioner_adv"],
            "respondent_adv": row["respondent_adv"],
            "court": row["court_name"],
            "bench": row["bench_number"],
            "judges": row["judges"],
            "list_date": format_date(row["list_date"]),
            "list_type": row["list_type"],
            "pdf_path": row["pdf_path"],
            "created_at": row["created_at"].isoformat() if row["created_at"] else None
        })
    
    return formatted_results


def filter_by_bench(db: DBConnector, date_str: str, bench_number: str) -> List[Dict[str, Any]]:
    """Filter cause lists by bench number."""
    # Connect to the database
    if not db.conn:
        db.connect()
    
    # Get court ID
    court_id = db.get_court_id("delhi_hc")
    if not court_id:
        logger.error("Court not found: delhi_hc")
        return []
    
    # Clean bench number
    bench_number = bench_number.strip().upper()
    
    # Query to get bench ID
    bench_query = "SELECT id FROM court_benches WHERE court_id = %s AND bench_number ILIKE %s"
    bench_result = db.execute(bench_query, (court_id, f"%{bench_number}%"))
    
    if not bench_result:
        logger.info(f"No bench found matching: {bench_number}")
        return []
    
    bench_ids = [row["id"] for row in bench_result]
    
    # Format date
    try:
        query_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        logger.error(f"Invalid date format: {date_str}. Use YYYY-MM-DD")
        return []
    
    # Query to get cause lists for the specified date and bench
    query = """
    SELECT cl.id, cl.list_date, cl.list_type, cl.pdf_path,
           cb.bench_number, cb.judges
    FROM cause_lists cl
    JOIN court_benches cb ON cl.bench_id = cb.id
    WHERE cl.court_id = %s AND cl.list_date = %s AND cl.bench_id = ANY(%s)
    """
    
    results = db.execute(query, (court_id, query_date, bench_ids))
    
    if not results:
        logger.info(f"No cause lists found for date {date_str} and bench {bench_number}")
        return []
    
    # Format results and get cases for each cause list
    formatted_results = []
    for row in results:
        cause_list_id = row["id"]
        
        # Query to get cases for this cause list
        cases_query = """
        SELECT c.id, c.case_number, c.title, c.item_number, c.file_number, 
               c.petitioner_adv, c.respondent_adv, c.created_at,
               array_agg(t.name) as tags
        FROM cases c
        LEFT JOIN case_tag_mappings ctm ON c.id = ctm.case_id
        LEFT JOIN case_tags t ON ctm.tag_id = t.id
        WHERE c.cause_list_id = %s
        GROUP BY c.id
        ORDER BY c.item_number
        """
        
        cases_result = db.execute(cases_query, (cause_list_id,))
        
        cases = []
        for case in cases_result:
            cases.append({
                "case_id": str(case["id"]),
                "case_number": case["case_number"],
                "title": case["title"],
                "item_number": case["item_number"],
                "file_number": case["file_number"],
                "petitioner_adv": case["petitioner_adv"],
                "respondent_adv": case["respondent_adv"],
                "tags": [tag for tag in case["tags"] if tag is not None],
                "created_at": case["created_at"].isoformat() if case["created_at"] else None
            })
        
        formatted_results.append({
            "cause_list_id": str(row["id"]),
            "list_date": format_date(row["list_date"]),
            "list_type": row["list_type"],
            "bench_number": row["bench_number"],
            "judges": row["judges"],
            "pdf_path": row["pdf_path"],
            "cases": cases
        })
    
    logger.info(f"Found {len(formatted_results)} cause lists for date {date_str} and bench {bench_number}")
    total_cases = sum(len(cl.get("cases", [])) for cl in formatted_results)
    logger.info(f"Total cases: {total_cases}")
    
    return formatted_results


def save_to_file(data: Any, output_path: str, pretty: bool = False) -> None:
    """Save data to a JSON file."""
    try:
        with open(output_path, 'w') as f:
            if pretty:
                json.dump(data, f, indent=2, default=str)
            else:
                json.dump(data, f, default=str)
        logger.info(f"Data saved to: {output_path}")
    except Exception as e:
        logger.error(f"Error saving data to file: {e}")


def main() -> None:
    """Main function."""
    args = parse_args()
    
    # Set logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger("db.connector").setLevel(logging.DEBUG)
    
    # Initialize database connector
    db = DBConnector()
    
    try:
        # List available dates
        if args.list_dates:
            list_available_dates(db)
            return
        
        # Search for a case by number
        if args.case:
            results = search_case_by_number(db, args.case)
            
            # Print results
            if results:
                if args.output:
                    save_to_file(results, args.output, args.pretty)
                else:
                    print(json.dumps(results, indent=2 if args.pretty else None, default=str))
            
            return
        
        # Filter cases by tag
        if args.tag:
            results = filter_cases_by_tag(db, args.tag)
            
            # Print results
            if results:
                if args.output:
                    save_to_file(results, args.output, args.pretty)
                else:
                    print(json.dumps(results, indent=2 if args.pretty else None, default=str))
            
            return
        
        # Query by date and optional bench
        if args.date:
            if args.bench:
                results = filter_by_bench(db, args.date, args.bench)
            else:
                results = query_cause_lists_by_date(db, args.date)
            
            # Print results
            if results:
                if args.output:
                    save_to_file(results, args.output, args.pretty)
                else:
                    print(json.dumps(results, indent=2 if args.pretty else None, default=str))
            
            return
        
        # If no specific command, show help
        if not any([args.date, args.list_dates, args.case, args.tag]):
            logger.info("No command specified. Use --help for usage information.")
            return
    
    finally:
        # Close database connection
        if db:
            db.close()


if __name__ == "__main__":
    main()

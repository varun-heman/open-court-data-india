#!/usr/bin/env python3
"""
Query the database for cause lists and cases.

This script provides a simple way to query the database for cause lists and cases
using the credentials from the .env file.
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database connection parameters from environment variables
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "ecourts")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")


def connect_to_db():
    """
    Connect to the database.
    
    Returns:
        Connection object or None if connection failed
    """
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None


def get_cause_lists(conn, date=None, court_code="delhi_hc"):
    """
    Get cause lists for a specific date.
    
    Args:
        conn: Database connection
        date: Date in YYYY-MM-DD format (default: today)
        court_code: Court code (default: delhi_hc)
        
    Returns:
        List of cause lists
    """
    try:
        # Set default date to today if not provided
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        # Create cursor
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Execute query
        query = """
        SELECT cl.id, cl.list_date, cl.list_type, cl.pdf_url, cl.pdf_path,
               cb.bench_number, cb.judges
        FROM cause_lists cl
        JOIN court_benches cb ON cl.bench_id = cb.id
        JOIN courts c ON cl.court_id = c.id
        WHERE c.code = %s AND cl.list_date = %s
        ORDER BY cb.bench_number
        """
        cursor.execute(query, (court_code, date))
        
        # Fetch results
        cause_lists = cursor.fetchall()
        
        # Close cursor
        cursor.close()
        
        return cause_lists
        
    except Exception as e:
        print(f"Error getting cause lists: {e}")
        return []


def get_cases(conn, cause_list_id):
    """
    Get cases for a specific cause list.
    
    Args:
        conn: Database connection
        cause_list_id: Cause list ID
        
    Returns:
        List of cases
    """
    try:
        # Create cursor
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Execute query
        query = """
        SELECT c.id, c.case_number, c.title, c.item_number, c.file_number,
               c.petitioner_adv, c.respondent_adv,
               array_agg(ct.name) as tags
        FROM cases c
        LEFT JOIN case_tag_mappings ctm ON c.id = ctm.case_id
        LEFT JOIN case_tags ct ON ctm.tag_id = ct.id
        WHERE c.cause_list_id = %s
        GROUP BY c.id
        ORDER BY c.item_number
        """
        cursor.execute(query, (cause_list_id,))
        
        # Fetch results
        cases = cursor.fetchall()
        
        # Close cursor
        cursor.close()
        
        return cases
        
    except Exception as e:
        print(f"Error getting cases: {e}")
        return []


def get_available_dates(conn, court_code="delhi_hc"):
    """
    Get available dates for a court.
    
    Args:
        conn: Database connection
        court_code: Court code (default: delhi_hc)
        
    Returns:
        List of available dates
    """
    try:
        # Create cursor
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Execute query
        query = """
        SELECT DISTINCT list_date
        FROM cause_lists cl
        JOIN courts c ON cl.court_id = c.id
        WHERE c.code = %s
        ORDER BY list_date DESC
        """
        cursor.execute(query, (court_code,))
        
        # Fetch results
        dates = cursor.fetchall()
        
        # Close cursor
        cursor.close()
        
        return [date["list_date"].strftime("%Y-%m-%d") for date in dates]
        
    except Exception as e:
        print(f"Error getting available dates: {e}")
        return []


def count_records(conn):
    """
    Count records in the database.
    
    Args:
        conn: Database connection
        
    Returns:
        Dictionary with record counts
    """
    try:
        # Create cursor
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Execute queries
        counts = {}
        
        # Count courts
        cursor.execute("SELECT COUNT(*) FROM courts")
        counts["courts"] = cursor.fetchone()["count"]
        
        # Count court benches
        cursor.execute("SELECT COUNT(*) FROM court_benches")
        counts["court_benches"] = cursor.fetchone()["count"]
        
        # Count cause lists
        cursor.execute("SELECT COUNT(*) FROM cause_lists")
        counts["cause_lists"] = cursor.fetchone()["count"]
        
        # Count cases
        cursor.execute("SELECT COUNT(*) FROM cases")
        counts["cases"] = cursor.fetchone()["count"]
        
        # Count case tags
        cursor.execute("SELECT COUNT(*) FROM case_tags")
        counts["case_tags"] = cursor.fetchone()["count"]
        
        # Close cursor
        cursor.close()
        
        return counts
        
    except Exception as e:
        print(f"Error counting records: {e}")
        return {}


def main():
    """
    Main function.
    """
    parser = argparse.ArgumentParser(description="Query the database for cause lists and cases")
    parser.add_argument("--date", "-d", help="Date in YYYY-MM-DD format (default: today)")
    parser.add_argument("--court", "-c", help="Court code (default: delhi_hc)", default="delhi_hc")
    parser.add_argument("--list-dates", "-l", action="store_true", help="List available dates")
    parser.add_argument("--count", "-n", action="store_true", help="Count records in the database")
    parser.add_argument("--cause-list", "-cl", help="Cause list ID to get cases for")
    args = parser.parse_args()
    
    # Connect to database
    conn = connect_to_db()
    if not conn:
        sys.exit(1)
    
    try:
        # Count records
        if args.count:
            counts = count_records(conn)
            print("\nRecord counts:")
            for table, count in counts.items():
                print(f"  {table}: {count}")
            print()
        
        # List available dates
        if args.list_dates:
            dates = get_available_dates(conn, args.court)
            print("\nAvailable dates:")
            for date in dates:
                print(f"  {date}")
            print()
        
        # Get cause lists for a specific date
        if not args.cause_list:
            date = args.date or datetime.now().strftime("%Y-%m-%d")
            cause_lists = get_cause_lists(conn, date, args.court)
            
            print(f"\nCause lists for {date}:")
            if not cause_lists:
                print("  No cause lists found")
            else:
                for cl in cause_lists:
                    print(f"  Bench: {cl['bench_number']}")
                    print(f"  Judges: {cl['judges']}")
                    print(f"  List type: {cl['list_type']}")
                    print(f"  ID: {cl['id']}")
                    print()
        
        # Get cases for a specific cause list
        if args.cause_list:
            cases = get_cases(conn, args.cause_list)
            
            print(f"\nCases for cause list {args.cause_list}:")
            if not cases:
                print("  No cases found")
            else:
                for case in cases:
                    print(f"  Case number: {case['case_number']}")
                    print(f"  Title: {case['title']}")
                    print(f"  Item number: {case['item_number']}")
                    if case['tags'] and case['tags'][0] is not None:
                        print(f"  Tags: {', '.join(case['tags'])}")
                    print()
        
    finally:
        # Close connection
        conn.close()


if __name__ == "__main__":
    main()

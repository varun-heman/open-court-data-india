#!/usr/bin/env python3
"""
Tag cases in the database based on various criteria.

This script provides a way to add tags to cases in the database,
either manually or automatically based on case attributes.
"""

import argparse
import logging
import os
import re
import sys
from typing import Dict, List, Optional, Any, Set, Tuple

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
    parser = argparse.ArgumentParser(description="Tag cases in the database")
    
    # Main command options
    parser.add_argument("--case", type=str, help="Case number to tag")
    parser.add_argument("--tag", type=str, help="Tag to add")
    parser.add_argument("--auto-tag", action="store_true", help="Auto-tag cases based on patterns")
    parser.add_argument("--list-tags", action="store_true", help="List all tags in the database")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    return parser.parse_args()


def list_all_tags(db: DBConnector) -> None:
    """List all tags in the database."""
    # Connect to the database
    if not db.conn:
        db.connect()
    
    # Query to get all tags with count of cases
    query = """
    SELECT t.name, COUNT(ctm.case_id) as case_count
    FROM case_tags t
    LEFT JOIN case_tag_mappings ctm ON t.id = ctm.tag_id
    GROUP BY t.id, t.name
    ORDER BY t.name
    """
    
    results = db.execute(query)
    
    if not results:
        logger.info("No tags found in the database")
        return
    
    logger.info(f"Found {len(results)} tags in the database:")
    for row in results:
        logger.info(f"  - {row['name']} ({row['case_count']} cases)")


def tag_case(db: DBConnector, case_number: str, tag_name: str) -> None:
    """Tag a specific case."""
    # Connect to the database
    if not db.conn:
        db.connect()
    
    # Clean inputs
    case_number = case_number.strip()
    tag_name = tag_name.strip().lower()
    
    # Find the case
    case_query = """
    SELECT id FROM cases WHERE case_number ILIKE %s
    """
    
    case_results = db.execute(case_query, (f"%{case_number}%",))
    
    if not case_results:
        logger.error(f"No cases found matching: {case_number}")
        return
    
    # Get or create the tag
    tag_id = get_or_create_tag(db, tag_name)
    if not tag_id:
        logger.error(f"Failed to create tag: {tag_name}")
        return
    
    # Add tag to each matching case
    success_count = 0
    for case in case_results:
        case_id = case["id"]
        if add_tag_to_case(db, case_id, tag_id):
            success_count += 1
    
    logger.info(f"Added tag '{tag_name}' to {success_count} of {len(case_results)} matching cases")


def get_or_create_tag(db: DBConnector, tag_name: str) -> Optional[int]:
    """Get or create a tag in the database."""
    # Check if tag exists
    tag_query = "SELECT id FROM case_tags WHERE name = %s"
    tag_result = db.execute(tag_query, (tag_name,))
    
    if tag_result:
        return tag_result[0]["id"]
    
    # Create new tag
    insert_query = "INSERT INTO case_tags (name) VALUES (%s) RETURNING id"
    try:
        result = db.execute(insert_query, (tag_name,))
        if result:
            logger.info(f"Created new tag: {tag_name}")
            return result[0]["id"]
    except Exception as e:
        logger.error(f"Error creating tag: {e}")
    
    return None


def add_tag_to_case(db: DBConnector, case_id: str, tag_id: int) -> bool:
    """Add a tag to a case."""
    # Check if mapping already exists
    check_query = "SELECT 1 FROM case_tag_mappings WHERE case_id = %s AND tag_id = %s"
    check_result = db.execute(check_query, (case_id, tag_id))
    
    if check_result:
        logger.debug(f"Tag already exists for case {case_id}")
        return True
    
    # Add tag to case
    insert_query = "INSERT INTO case_tag_mappings (case_id, tag_id) VALUES (%s, %s)"
    try:
        db.execute(insert_query, (case_id, tag_id))
        logger.debug(f"Added tag to case {case_id}")
        return True
    except Exception as e:
        logger.error(f"Error adding tag to case: {e}")
        return False


def auto_tag_cases(db: DBConnector) -> None:
    """Automatically tag cases based on patterns in case numbers and titles."""
    # Connect to the database
    if not db.conn:
        db.connect()
    
    # Define tagging rules
    tagging_rules = [
        # Case type tags based on case number
        {"pattern": r"W\.P\.(C)", "field": "case_number", "tag": "writ_petition_civil"},
        {"pattern": r"W\.P\.(CRL)", "field": "case_number", "tag": "writ_petition_criminal"},
        {"pattern": r"CRL\.M\.C", "field": "case_number", "tag": "criminal_misc"},
        {"pattern": r"CRL\.A", "field": "case_number", "tag": "criminal_appeal"},
        {"pattern": r"RFA", "field": "case_number", "tag": "regular_first_appeal"},
        {"pattern": r"FAO", "field": "case_number", "tag": "first_appeal_order"},
        {"pattern": r"CM APPL", "field": "case_number", "tag": "civil_misc_application"},
        {"pattern": r"CS\(COMM\)", "field": "case_number", "tag": "commercial_suit"},
        {"pattern": r"ARB\.P", "field": "case_number", "tag": "arbitration_petition"},
        {"pattern": r"CONT\.CAS", "field": "case_number", "tag": "contempt_case"},
        {"pattern": r"LPA", "field": "case_number", "tag": "letters_patent_appeal"},
        {"pattern": r"MAT\.APP", "field": "case_number", "tag": "matrimonial_appeal"},
        
        # Subject matter tags based on title
        {"pattern": r"INCOME TAX", "field": "title", "tag": "income_tax"},
        {"pattern": r"SERVICE", "field": "title", "tag": "service_matter"},
        {"pattern": r"PROPERTY", "field": "title", "tag": "property_dispute"},
        {"pattern": r"LAND", "field": "title", "tag": "land_dispute"},
        {"pattern": r"RENT", "field": "title", "tag": "rent_matter"},
        {"pattern": r"BANK", "field": "title", "tag": "banking"},
        {"pattern": r"INSURANCE", "field": "title", "tag": "insurance"},
        {"pattern": r"EDUCATION", "field": "title", "tag": "education"},
        {"pattern": r"UNIVERSITY", "field": "title", "tag": "education"},
        {"pattern": r"COLLEGE", "field": "title", "tag": "education"},
        {"pattern": r"SCHOOL", "field": "title", "tag": "education"},
        {"pattern": r"STUDENT", "field": "title", "tag": "education"},
        
        # Party type tags
        {"pattern": r"UNION OF INDIA", "field": "title", "tag": "govt_party"},
        {"pattern": r"GOVT\.", "field": "title", "tag": "govt_party"},
        {"pattern": r"GOVERNMENT", "field": "title", "tag": "govt_party"},
        {"pattern": r"DELHI DEVELOPMENT AUTHORITY", "field": "title", "tag": "govt_party"},
        {"pattern": r"DDA", "field": "title", "tag": "govt_party"},
        {"pattern": r"MUNICIPAL", "field": "title", "tag": "govt_party"},
        {"pattern": r"M/S", "field": "title", "tag": "company_party"},
        {"pattern": r"LTD", "field": "title", "tag": "company_party"},
        {"pattern": r"LIMITED", "field": "title", "tag": "company_party"},
        {"pattern": r"PVT", "field": "title", "tag": "company_party"},
        {"pattern": r"PRIVATE", "field": "title", "tag": "company_party"},
        {"pattern": r"CORPORATION", "field": "title", "tag": "company_party"},
    ]
    
    # Get all cases
    cases_query = """
    SELECT id, case_number, title FROM cases
    """
    
    cases = db.execute(cases_query)
    
    if not cases:
        logger.info("No cases found in the database")
        return
    
    logger.info(f"Found {len(cases)} cases to process")
    
    # Process each case
    total_tags_added = 0
    for case in cases:
        case_id = case["id"]
        case_number = case["case_number"] or ""
        title = case["title"] or ""
        
        # Apply tagging rules
        tags_for_case = set()
        for rule in tagging_rules:
            field_value = case_number if rule["field"] == "case_number" else title
            if re.search(rule["pattern"], field_value, re.IGNORECASE):
                tags_for_case.add(rule["tag"])
        
        # Add tags to case
        for tag_name in tags_for_case:
            tag_id = get_or_create_tag(db, tag_name)
            if tag_id and add_tag_to_case(db, case_id, tag_id):
                total_tags_added += 1
    
    logger.info(f"Added {total_tags_added} tags to cases")


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
        # List all tags
        if args.list_tags:
            list_all_tags(db)
            return
        
        # Tag a specific case
        if args.case and args.tag:
            tag_case(db, args.case, args.tag)
            return
        
        # Auto-tag cases
        if args.auto_tag:
            auto_tag_cases(db)
            return
        
        # If no specific command, show help
        if not any([args.list_tags, args.case and args.tag, args.auto_tag]):
            logger.info("No command specified. Use --help for usage information.")
            return
    
    finally:
        # Close database connection
        if db:
            db.close()


if __name__ == "__main__":
    main()

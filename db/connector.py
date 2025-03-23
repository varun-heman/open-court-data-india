"""
Database connector for the ecourts-scrapers project.

This module provides a connection to the PostgreSQL database
and functions to interact with the database.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from datetime import datetime, date
import uuid
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DBConnector:
    """
    Database connector for the ecourts-scrapers project.
    """
    
    def __init__(
        self,
        host: str = None,
        port: str = None,
        dbname: str = None,
        user: str = None,
        password: str = None
    ):
        """
        Initialize the database connector.
        
        Args:
            host: Database host
            port: Database port
            dbname: Database name
            user: Database user
            password: Database password
        """
        # Load environment variables from .env file
        load_dotenv()
        
        # Get database connection parameters from environment variables if not provided
        self.host = host or os.environ.get("DB_HOST", "localhost")
        self.port = port or os.environ.get("DB_PORT", "5432")
        self.dbname = dbname or os.environ.get("DB_NAME", "ecourts")
        self.user = user or os.environ.get("DB_USER", "postgres")
        self.password = password or os.environ.get("DB_PASSWORD", "")
        
        # Connection and cursor
        self.conn = None
        self.cursor = None
        
        logger.info(f"Initialized database connector for {self.dbname} on {self.host}:{self.port}")
        
        # Automatically connect to the database
        self.connect()
        if self.conn:
            logger.info("Connected to database")
    
    def connect(self) -> bool:
        """
        Connect to the database.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Connect to the database
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                dbname=self.dbname,
                user=self.user,
                password=self.password
            )
            
            # Create cursor
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            
            logger.info(f"Connected to database {self.dbname}")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            return False
    
    def disconnect(self) -> None:
        """
        Disconnect from the database.
        """
        try:
            if self.cursor:
                self.cursor.close()
            
            if self.conn:
                self.conn.close()
            
            logger.info("Disconnected from database")
            
        except Exception as e:
            logger.error(f"Error disconnecting from database: {e}")
    
    def close(self) -> None:
        """
        Alias for disconnect.
        """
        self.disconnect()
    
    def execute(self, query: str, params: Optional[Tuple] = None) -> Optional[List[Dict[str, Any]]]:
        """
        Execute a query.
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            Query results as a list of dictionaries, or None if query failed
        """
        try:
            # Ensure we have a connection
            if not self.conn:
                if not self.connect():
                    logger.error("Cannot execute query: No database connection")
                    return None
                    
            # Execute query
            self.cursor.execute(query, params)
            
            # Commit if not a SELECT query
            if not query.strip().upper().startswith("SELECT"):
                self.conn.commit()
            
            # Return results for SELECT queries
            if query.strip().upper().startswith("SELECT") or "RETURNING" in query.upper():
                return list(self.cursor.fetchall())
            
            return []
            
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            logger.debug(f"Query: {query}")
            logger.debug(f"Params: {params}")
            
            # Rollback on error
            if self.conn:
                self.conn.rollback()
                
            return None
    
    def execute_many(self, query: str, params_list: List[Tuple]) -> bool:
        """
        Execute a query with multiple parameter sets.
        
        Args:
            query: SQL query
            params_list: List of parameter tuples
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Connect if not already connected
            if not self.conn or self.conn.closed:
                if not self.connect():
                    return False
            
            # Execute query with multiple parameter sets
            self.cursor.executemany(query, params_list)
            
            # Commit changes
            self.conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error executing query with multiple parameter sets: {e}")
            logger.debug(f"Query: {query}")
            
            # Rollback transaction
            if self.conn:
                self.conn.rollback()
            
            return False
    
    def execute_values(self, query: str, values: List[Tuple], template: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """
        Execute a query with multiple values using execute_values.
        
        Args:
            query: SQL query
            values: List of value tuples
            template: Optional template for values
            
        Returns:
            Query results as a list of dictionaries, or None if query failed
        """
        try:
            # Ensure we have a connection
            if not self.conn:
                if not self.connect():
                    logger.error("Cannot execute query: No database connection")
                    return None
            
            # Skip if no values
            if not values:
                logger.debug("No values to insert, skipping")
                return []
                
            # Execute query with values
            execute_values(self.cursor, query, values, template=template)
            
            # Commit changes
            self.conn.commit()
            
            # Return results if query returns results
            if "RETURNING" in query.upper():
                try:
                    return list(self.cursor.fetchall())
                except psycopg2.ProgrammingError as e:
                    # Handle "no results to fetch" error gracefully
                    if "no results to fetch" in str(e):
                        logger.debug("No results to fetch from execute_values")
                        return []
                    raise
            
            return []
            
        except Exception as e:
            logger.error(f"Error executing query with multiple values: {e}")
            logger.debug(f"Query: {query}")
            
            # Rollback on error
            if self.conn:
                self.conn.rollback()
                
            return None
    
    # Court-related methods
    def get_court_id(self, court_code: str) -> Optional[int]:
        """
        Get court ID by court code.
        
        Args:
            court_code: Court code
            
        Returns:
            Court ID or None if not found
        """
        query = "SELECT id FROM courts WHERE code = %s"
        result = self.execute(query, (court_code,))
        
        if result and len(result) > 0:
            return result[0]["id"]
        
        return None
    
    def get_bench_id(self, court_id: int, bench_number: str, judges: Optional[str] = None) -> Optional[int]:
        """
        Get bench ID by court ID and bench number.
        
        Args:
            court_id: Court ID
            bench_number: Bench number
            judges: Judges on the bench (not used for lookup, only for logging)
            
        Returns:
            Bench ID or None if not found
        """
        try:
            # Clean bench number to ensure consistent format
            bench_number = bench_number.strip().upper()
            
            # Query to get existing bench
            query = "SELECT id FROM court_benches WHERE court_id = %s AND bench_number = %s"
            result = self.execute(query, (court_id, bench_number))
            
            if result and len(result) > 0:
                bench_id = result[0]["id"]
                logger.debug(f"Found existing bench: {bench_number} (ID: {bench_id})")
                return bench_id
            
            logger.debug(f"Bench not found: {bench_number} for court ID {court_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting bench ID: {e}")
            logger.debug(f"Parameters: court_id={court_id}, bench_number={bench_number}")
            return None
    
    def create_bench(self, court_id: int, bench_number: str, judges: Optional[str] = None) -> Optional[int]:
        """
        Create a court bench.
        
        Args:
            court_id: Court ID
            bench_number: Bench number
            judges: Judges on the bench
            
        Returns:
            Bench ID or None if creation failed
        """
        try:
            # Ensure we have a connection
            if not self.conn:
                if not self.connect():
                    logger.error("Cannot create bench: No database connection")
                    return None
                    
            # Clean bench number to ensure consistent format
            bench_number = bench_number.strip().upper()
            
            # Create new bench
            insert_query = """
            INSERT INTO court_benches (court_id, bench_number, judges)
            VALUES (%s, %s, %s)
            RETURNING id
            """
            result = self.execute(insert_query, (court_id, bench_number, judges))
            
            if result and len(result) > 0:
                bench_id = result[0]["id"]
                logger.info(f"Created new bench: {bench_number} (ID: {bench_id})")
                return bench_id
            
            logger.error(f"Failed to create bench: No ID returned from insert query")
            return None
            
        except Exception as e:
            logger.error(f"Error creating bench: {e}")
            logger.debug(f"Parameters: court_id={court_id}, bench_number={bench_number}, judges={judges}")
            return None
    
    def get_or_create_bench(self, court_id: int, bench_number: str, judges: Optional[str] = None) -> Optional[int]:
        """
        Get or create a court bench.
        
        Args:
            court_id: Court ID
            bench_number: Bench number
            judges: Judges on the bench
            
        Returns:
            Bench ID or None if creation failed
        """
        try:
            # Clean bench number to ensure consistent format
            bench_number = bench_number.strip().upper()
            
            # First, try to get existing bench
            query = "SELECT id FROM court_benches WHERE court_id = %s AND bench_number = %s"
            result = self.execute(query, (court_id, bench_number))
            
            if result and len(result) > 0:
                bench_id = result[0]["id"]
                
                # Update judges if provided
                if judges:
                    update_query = "UPDATE court_benches SET judges = %s WHERE id = %s"
                    self.execute(update_query, (judges, bench_id))
                
                return bench_id
            
            # Create new bench
            insert_query = """
            INSERT INTO court_benches (court_id, bench_number, judges)
            VALUES (%s, %s, %s)
            RETURNING id
            """
            result = self.execute(insert_query, (court_id, bench_number, judges))
            
            if result and len(result) > 0:
                logger.info(f"Created new bench: {bench_number}")
                return result[0]["id"]
            
            logger.error(f"Failed to create bench: No ID returned from insert query")
            return None
            
        except Exception as e:
            logger.error(f"Error creating bench: {e}")
            logger.debug(f"Parameters: court_id={court_id}, bench_number={bench_number}, judges={judges}")
            return None
    
    # Cause list methods
    def create_cause_list(
        self,
        court_id: int,
        bench_id: int,
        list_date: Union[str, date],
        list_type: str = "Daily List",
        pdf_url: Optional[str] = None,
        pdf_path: Optional[str] = None
    ) -> Optional[uuid.UUID]:
        """
        Create a cause list.
        
        Args:
            court_id: Court ID
            bench_id: Bench ID
            list_date: List date (YYYY-MM-DD)
            list_type: List type
            pdf_url: URL to PDF file
            pdf_path: Path to PDF file
            
        Returns:
            Cause list ID or None if creation failed
        """
        try:
            # Convert string date to date object if needed
            if isinstance(list_date, str):
                list_date = datetime.strptime(list_date, "%Y-%m-%d").date()
            
            # Check if cause list already exists
            query = """
            SELECT id FROM cause_lists
            WHERE court_id = %s AND bench_id = %s AND list_date = %s AND list_type = %s
            """
            result = self.execute(query, (court_id, bench_id, list_date, list_type))
            
            if result and len(result) > 0:
                cause_list_id = result[0]["id"]
                
                # Update PDF URL and path if provided
                if pdf_url or pdf_path:
                    update_query = """
                    UPDATE cause_lists
                    SET pdf_url = COALESCE(%s, pdf_url), pdf_path = COALESCE(%s, pdf_path)
                    WHERE id = %s
                    """
                    self.execute(update_query, (pdf_url, pdf_path, cause_list_id))
                
                return cause_list_id
            
            # Create new cause list
            insert_query = """
            INSERT INTO cause_lists (court_id, bench_id, list_date, list_type, pdf_url, pdf_path)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
            """
            result = self.execute(
                insert_query,
                (court_id, bench_id, list_date, list_type, pdf_url, pdf_path)
            )
            
            if result and len(result) > 0:
                return result[0]["id"]
            
            logger.error(f"Failed to create cause list: No ID returned from insert query")
            return None
            
        except Exception as e:
            logger.error(f"Error creating cause list: {e}")
            logger.debug(f"Parameters: court_id={court_id}, bench_id={bench_id}, list_date={list_date}, list_type={list_type}")
            return None
    
    def get_or_create_tag(self, tag_name: str) -> Optional[int]:
        """
        Get or create a case tag.
        
        Args:
            tag_name: Tag name
            
        Returns:
            Tag ID or None if creation failed
        """
        # First, try to get existing tag
        query = "SELECT id FROM case_tags WHERE name = %s"
        result = self.execute(query, (tag_name,))
        
        if result and len(result) > 0:
            return result[0]["id"]
        
        # Create new tag
        insert_query = "INSERT INTO case_tags (name) VALUES (%s) RETURNING id"
        result = self.execute(insert_query, (tag_name,))
        
        if result and len(result) > 0:
            return result[0]["id"]
        
        return None
    
    def create_case(
        self,
        cause_list_id: uuid.UUID,
        case_number: str,
        title: Optional[str] = None,
        item_number: Optional[str] = None,
        file_number: Optional[str] = None,
        petitioner_adv: Optional[str] = None,
        respondent_adv: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[uuid.UUID]:
        """
        Create a case.
        
        Args:
            cause_list_id: Cause list ID
            case_number: Case number
            title: Case title
            item_number: Item number
            file_number: File number
            petitioner_adv: Petitioner advocate
            respondent_adv: Respondent advocate
            tags: List of tag names
            
        Returns:
            Case ID or None if creation failed
        """
        try:
            # Check if case already exists
            check_query = """
            SELECT id FROM cases 
            WHERE cause_list_id = %s AND case_number = %s
            """
            existing = self.execute(check_query, (cause_list_id, case_number))
            
            if existing and len(existing) > 0:
                logger.info(f"Case already exists: {case_number} for cause list {cause_list_id}")
                return existing[0]["id"]
            
            # Create case
            insert_query = """
            INSERT INTO cases (cause_list_id, case_number, title, item_number, file_number, petitioner_adv, respondent_adv)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """
            result = self.execute(
                insert_query,
                (cause_list_id, case_number, title, item_number, file_number, petitioner_adv, respondent_adv)
            )
            
            if not result or len(result) == 0:
                logger.error(f"Failed to create case: {case_number}")
                return None
            
            case_id = result[0]["id"]
            logger.debug(f"Created case: {case_number} with ID: {case_id}")
            
            # Add tags if provided
            if tags and len(tags) > 0:
                tag_mappings = []
                
                for tag_name in tags:
                    try:
                        tag_id = self.get_or_create_tag(tag_name)
                        if tag_id:
                            tag_mappings.append((case_id, tag_id))
                        else:
                            logger.warning(f"Failed to create tag: {tag_name}")
                    except Exception as e:
                        logger.error(f"Error creating tag {tag_name}: {e}")
                
                if tag_mappings:
                    try:
                        mapping_query = """
                        INSERT INTO case_tag_mappings (case_id, tag_id)
                        VALUES %s
                        ON CONFLICT (case_id, tag_id) DO NOTHING
                        """
                        self.execute_values(mapping_query, tag_mappings)
                        logger.debug(f"Added {len(tag_mappings)} tags to case {case_number}")
                    except Exception as e:
                        logger.error(f"Error adding tags to case {case_number}: {e}")
            
            return case_id
            
        except Exception as e:
            logger.error(f"Error creating case {case_number}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    # Query methods for the UI
    def get_cause_lists_by_date(
        self,
        court_code: str,
        list_date: Union[str, date]
    ) -> List[Dict[str, Any]]:
        """
        Get cause lists by date.
        
        Args:
            court_code: Court code
            list_date: List date (YYYY-MM-DD)
            
        Returns:
            List of cause lists with cases
        """
        # Convert string date to date object if needed
        if isinstance(list_date, str):
            list_date = datetime.strptime(list_date, "%Y-%m-%d").date()
        
        # Get court ID
        court_id = self.get_court_id(court_code)
        if not court_id:
            logger.error(f"Court not found: {court_code}")
            return []
        
        # Get cause lists
        cause_lists_query = """
        SELECT cl.id, cl.list_date, cl.list_type, cl.pdf_url,
               cb.bench_number AS court_no, cb.judges AS bench
        FROM cause_lists cl
        JOIN court_benches cb ON cl.bench_id = cb.id
        WHERE cl.court_id = %s AND cl.list_date = %s
        ORDER BY cb.bench_number
        """
        cause_lists = self.execute(cause_lists_query, (court_id, list_date))
        
        if not cause_lists:
            return []
        
        # Get cases for each cause list
        result = []
        for cause_list in cause_lists:
            # Get cases
            cases_query = """
            SELECT c.id, c.item_number, c.case_number, c.title, c.file_number,
                   c.petitioner_adv, c.respondent_adv
            FROM cases c
            WHERE c.cause_list_id = %s
            ORDER BY c.item_number
            """
            cases = self.execute(cases_query, (cause_list["id"],))
            
            # Get tags for each case
            if cases:
                for case in cases:
                    tags_query = """
                    SELECT ct.name
                    FROM case_tag_mappings ctm
                    JOIN case_tags ct ON ctm.tag_id = ct.id
                    WHERE ctm.case_id = %s
                    """
                    tags_result = self.execute(tags_query, (case["id"],))
                    
                    # Add tags to case
                    case["tags"] = [tag["name"] for tag in tags_result] if tags_result else []
            
            # Format cause list
            formatted_cause_list = {
                "court": "DELHI HIGH COURT",
                "courtNo": cause_list["court_no"],
                "bench": cause_list["bench"],
                "cases": cases or []
            }
            
            result.append(formatted_cause_list)
        
        return result
    
    def get_available_dates(self, court_code: str) -> List[str]:
        """
        Get available dates for a court.
        
        Args:
            court_code: Court code
            
        Returns:
            List of available dates in YYYY-MM-DD format
        """
        # Get court ID
        court_id = self.get_court_id(court_code)
        if not court_id:
            logger.error(f"Court not found: {court_code}")
            return []
        
        # Get available dates
        query = """
        SELECT DISTINCT list_date
        FROM cause_lists
        WHERE court_id = %s
        ORDER BY list_date DESC
        """
        result = self.execute(query, (court_id,))
        
        if not result:
            return []
        
        # Format dates
        return [date["list_date"].strftime("%Y-%m-%d") for date in result]

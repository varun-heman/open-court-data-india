"""
API for the ecourts-scrapers project.

This module provides a FastAPI application that serves court data from the database.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from fastapi import FastAPI, HTTPException, Query, Depends, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager

from db.connector import DBConnector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database connector
db = DBConnector()

# Lifespan context manager for database connection
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to database on startup
    db.connect()
    yield
    # Disconnect from database on shutdown
    db.disconnect()

# Create FastAPI app
app = FastAPI(
    title="eCourts Scrapers API",
    description="API for accessing court data from the eCourts scrapers project",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class Case(BaseModel):
    caseNumber: str
    title: Optional[str] = None
    tags: List[str] = []
    itemNumber: Optional[str] = None
    fileNumber: Optional[str] = None
    causeList: str = "Daily List"
    petitionerAdv: Optional[str] = None
    respondentAdv: Optional[str] = None

class CauseList(BaseModel):
    court: str
    courtNo: str
    bench: Optional[str] = None
    cases: List[Case] = []

class CauseListResponse(BaseModel):
    court: str
    date: str
    cause_lists: List[CauseList] = []

class DateResponse(BaseModel):
    dates: List[str]


# Routes
@app.get("/")
async def root():
    """
    Root endpoint.
    """
    return {"message": "Welcome to the eCourts Scrapers API"}

@app.get("/courts")
async def get_courts():
    """
    Get list of available courts.
    """
    query = "SELECT id, name, code, website FROM courts"
    courts = db.execute(query)
    
    if not courts:
        return []
    
    return courts

@app.get("/courts/{court_code}/dates", response_model=DateResponse)
async def get_available_dates(court_code: str):
    """
    Get available dates for a court.
    """
    dates = db.get_available_dates(court_code)
    return {"dates": dates}

@app.get("/courts/{court_code}/cause_lists/{date}", response_model=CauseListResponse)
async def get_cause_lists(
    court_code: str,
    date: str = Path(..., description="Date in YYYY-MM-DD format")
):
    """
    Get cause lists for a court on a specific date.
    """
    try:
        # Validate date format
        try:
            parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        # Get cause lists from database
        cause_lists = db.get_cause_lists_by_date(court_code, parsed_date)
        
        if not cause_lists:
            return {
                "court": court_code.upper(),
                "date": date,
                "cause_lists": []
            }
        
        return {
            "court": court_code.upper(),
            "date": date,
            "cause_lists": cause_lists
        }
        
    except Exception as e:
        logger.error(f"Error getting cause lists: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Run the app with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

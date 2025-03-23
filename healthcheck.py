#!/usr/bin/env python3
"""
Healthcheck API and Dashboard for Court Scrapers
"""

import os
import sys
import json
import time
import threading
import subprocess
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import inspect

from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import scraper utilities
from utils.scraper_utils import BaseScraper
from utils.common import get_today_formatted

# Constants
HEALTHCHECK_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "healthcheck")
LAST_RUN_FILE = os.path.join(HEALTHCHECK_DIR, "last_run.json")

# Create the healthcheck directory if it doesn't exist
os.makedirs(HEALTHCHECK_DIR, exist_ok=True)

# Dictionary to store running scraper processes
running_scrapers = {}

# Dictionary to store last run times
last_run_times = {}

# Lock for thread safety
lock = threading.Lock()

# Event to signal the scheduler thread to stop
scheduler_stop_event = threading.Event()

def get_scrapers() -> List[Dict[str, Any]]:
    """
    Get all available scrapers.
    
    Returns:
        List[Dict[str, Any]]: List of scraper information.
    """
    scrapers = []
    
    # Get all Python files in the scrapers directory
    scrapers_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scrapers")
    
    # First, find all base scrapers
    for root, _, files in os.walk(scrapers_dir):
        for file in files:
            if file.endswith("_scraper.py") and not file.startswith("__") and "cause_lists" not in root:
                # Get the module path
                rel_path = os.path.relpath(os.path.join(root, file), os.path.dirname(os.path.abspath(__file__)))
                module_path = rel_path.replace(os.path.sep, ".").replace(".py", "")
                
                # Import the module
                try:
                    module = importlib.import_module(module_path)
                    
                    # Find all scraper classes in the module
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and issubclass(obj, BaseScraper) and obj != BaseScraper:
                            # Get the scraper ID
                            scraper_id = obj.__name__.lower()
                            if scraper_id.endswith("scraper"):
                                scraper_id = scraper_id[:-7]
                            
                            # Get the court name from the directory name
                            court_dir = os.path.basename(os.path.dirname(os.path.join(root, file)))
                            court_name = " ".join(court_dir.split("_")).title()
                            
                            # Get the base URL based on court
                            base_url = "https://example.com"
                            if court_dir == "delhi_hc":
                                base_url = "https://delhihighcourt.nic.in"
                            
                            # Create the scraper info
                            scraper_info = {
                                "id": court_dir,
                                "module": module_path,
                                "type": "base",
                                "name": f"{court_name} Court",
                                "court": court_name,
                                "base_url": base_url,
                                "specialized": []
                            }
                            
                            # Get the scraper status
                            status_file = os.path.join(HEALTHCHECK_DIR, f"{scraper_info['id']}.json")
                            if os.path.exists(status_file):
                                with open(status_file, "r") as f:
                                    scraper_info["status"] = json.load(f)
                            else:
                                scraper_info["status"] = {
                                    "id": scraper_info['id'],
                                    "status": "unknown",
                                    "last_check": None,
                                    "last_success": None,
                                    "last_failure": None,
                                    "error": None,
                                    "history": []
                                }
                            
                            # Calculate daily summary
                            scraper_info["daily_summary"] = calculate_daily_summary(scraper_info["status"])
                            
                            # Add the scraper to the list
                            scrapers.append(scraper_info)
                except Exception as e:
                    print(f"Error importing module {module_path}: {e}")
    
    # Now find all specialized scrapers
    for root, _, files in os.walk(scrapers_dir):
        for file in files:
            if file.endswith("_scraper.py") and not file.startswith("__") and "cause_lists" in root:
                # Get the module path
                rel_path = os.path.relpath(os.path.join(root, file), os.path.dirname(os.path.abspath(__file__)))
                module_path = rel_path.replace(os.path.sep, ".").replace(".py", "")
                
                try:
                    # Import the module
                    module = importlib.import_module(module_path)
                    
                    # Find all scraper classes in the module
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and issubclass(obj, BaseScraper) and obj != BaseScraper:
                            # Get the scraper ID
                            scraper_id = obj.__name__.lower()
                            if scraper_id.endswith("scraper"):
                                scraper_id = scraper_id[:-7]
                            
                            # Get the court name from the directory structure
                            court_dir = os.path.basename(os.path.dirname(os.path.dirname(os.path.join(root, file))))
                            specialized_type = os.path.basename(os.path.dirname(os.path.join(root, file)))
                            
                            # Create the specialized ID - ensure it's consistent and unique
                            if specialized_type == "cause_lists":
                                specialized_id = f"{court_dir}_cause_lists"
                            else:
                                specialized_id = f"{court_dir}_{specialized_type}"
                            
                            # Get the court name
                            court_name = " ".join(court_dir.split("_")).title()
                            
                            # Get the specialized name - normalize to consistent naming
                            if specialized_type == "cause_lists":
                                specialized_name = "Cause Lists"
                            else:
                                specialized_name = " ".join(specialized_type.split("_")).title()
                            
                            # Get the base URL based on court
                            base_url = "https://example.com"
                            if court_dir == "delhi_hc":
                                base_url = "https://delhihighcourt.nic.in"
                            
                            # Check if this specialized scraper is already in the list
                            if any(s.get('id') == specialized_id for scraper in scrapers for s in scraper.get("specialized", [])):
                                continue
                            
                            # Create the specialized scraper info
                            specialized_info = {
                                "id": specialized_id,
                                "module": module_path,
                                "type": "specialized",
                                "name": specialized_name,
                                "court": court_name,
                                "base_url": base_url
                            }
                            
                            # Get the scraper status
                            status_file = os.path.join(HEALTHCHECK_DIR, f"{specialized_id}.json")
                            if os.path.exists(status_file):
                                with open(status_file, "r") as f:
                                    specialized_info["status"] = json.load(f)
                            else:
                                specialized_info["status"] = {
                                    "id": specialized_id,
                                    "status": "unknown",
                                    "last_check": None,
                                    "last_success": None,
                                    "last_failure": None,
                                    "error": None,
                                    "history": []
                                }
                            
                            # Calculate daily summary
                            specialized_info["daily_summary"] = calculate_daily_summary(specialized_info["status"])
                            
                            # Find the base scraper and add the specialized scraper to it
                            for scraper in scrapers:
                                if scraper["id"] == court_dir:
                                    scraper["specialized"].append(specialized_info)
                                    break
                except Exception as e:
                    print(f"Error importing specialized module {module_path}: {e}")
    
    # Update base scraper status based on specialized scrapers
    for scraper in scrapers:
        if scraper["specialized"]:
            # Check if any specialized scraper is running
            any_running = any(s["status"]["status"] == "running" for s in scraper["specialized"])
            if any_running:
                scraper["status"]["status"] = "running"
                continue
                
            # Check if all specialized scrapers are in error state
            all_error = all(s["status"]["status"] == "error" for s in scraper["specialized"])
            if all_error:
                scraper["status"]["status"] = "error"
                continue
                
            # Check if any specialized scraper is in error state
            any_error = any(s["status"]["status"] == "error" for s in scraper["specialized"])
            if any_error:
                # If base scraper is OK but some specialized scrapers have errors, mark as warning
                if scraper["status"]["status"] == "ok":
                    scraper["status"]["status"] = "warning"
    
    return scrapers

def get_scraper_status(scraper_id: str) -> Dict[str, Any]:
    """
    Get the status of a scraper.
    """
    try:
        # Get the status file path
        status_file = os.path.join(HEALTHCHECK_DIR, f"{scraper_id}.json")
        
        # Check if the status file exists
        if not os.path.exists(status_file):
            return {"status": "unknown", "error": "No status file found"}
        
        # Read the status file
        with open(status_file, "r") as f:
            status = json.load(f)
        
        # Format timestamps in human-readable 24-hour IST format
        for key in ["last_check", "last_success", "last_failure", "last_run"]:
            if key in status and status[key]:
                # Parse ISO timestamp
                try:
                    timestamp = status[key]
                    if "T" in timestamp:
                        date_part = timestamp.split("T")[0]
                        time_part = timestamp.split("T")[1]
                        if "." in time_part:
                            time_part = time_part.split(".")[0]  # Remove milliseconds
                        status[key] = f"{date_part} {time_part} IST"
                except Exception as e:
                    print(f"Error formatting timestamp {key}: {e}")
        
        return status
    except Exception as e:
        return {"status": "unknown", "error": str(e)}

def update_scraper_status(scraper_info: Dict[str, Any], status: str, error: Optional[str] = None) -> None:
    """
    Update the status of a scraper.
    """
    try:
        # Get the status file path
        status_file = os.path.join(HEALTHCHECK_DIR, f"{scraper_info['id']}.json")
        
        # Create the healthcheck directory if it doesn't exist
        os.makedirs(os.path.dirname(status_file), exist_ok=True)
        
        # Get the current status
        current_status = {}
        if os.path.exists(status_file):
            with open(status_file, "r") as f:
                try:
                    current_status = json.load(f)
                except json.JSONDecodeError:
                    current_status = {}
        
        # Update the status
        current_status["status"] = status
        current_status["last_check"] = datetime.now().isoformat()
        
        # Update success or failure timestamp
        if status == "ok":
            current_status["last_success"] = datetime.now().isoformat()
        elif status == "error":
            current_status["last_failure"] = datetime.now().isoformat()
            if error:
                current_status["error"] = error
        
        # Add to history
        if "history" not in current_status:
            current_status["history"] = []
        
        # Add entry to history
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "status": status
        }
        if error and status == "error":
            history_entry["error"] = error
        
        current_status["history"].insert(0, history_entry)
        
        # Limit history to 100 entries
        current_status["history"] = current_status["history"][:100]
        
        # Write the status
        with open(status_file, "w") as f:
            json.dump(current_status, f, indent=2)
    except Exception as e:
        print(f"Error updating scraper status: {e}")

def check_scraper_health(scraper_info: Dict[str, Any]) -> Tuple[str, Optional[str]]:
    """
    Check the health of a scraper.
    
    Args:
        scraper_info: Scraper information.
        
    Returns:
        Tuple[str, Optional[str]]: Status and error message.
    """
    # If this is a base scraper with specialized scrapers, check if all specialized scrapers are healthy
    if scraper_info["type"] == "base" and "specialized" in scraper_info and scraper_info["specialized"]:
        # If all specialized scrapers are OK, then the base scraper is OK
        all_ok = True
        for specialized in scraper_info["specialized"]:
            if specialized["status"]["status"] != "ok":
                all_ok = False
                break
        
        if all_ok:
            return "ok", None
    
    try:
        # Import the module
        module = importlib.import_module(scraper_info["module"])
        
        # Get the scraper class
        scraper_class = None
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, BaseScraper) and obj != BaseScraper:
                scraper_class = obj
                break
        
        if scraper_class is None:
            return "error", "Scraper class not found"
        
        # Initialize the scraper
        court_name = scraper_info["court"]
        base_url = scraper_info["base_url"]
        
        # For specialized scrapers, don't pass court_name and base_url
        if scraper_info["type"] == "specialized":
            try:
                scraper = scraper_class()
                status = "ok"
                error = None
            except Exception as e:
                return "error", str(e)
        else:
            try:
                # For Delhi HC, we need to handle it differently
                if scraper_info["id"] == "delhi_hc":
                    # Don't try to initialize the base scraper if it has specialized scrapers
                    if "specialized" in scraper_info and scraper_info["specialized"]:
                        return "ok", None
                
                scraper = scraper_class(court_name=court_name, base_url=base_url)
                status = "ok"
                error = None
            except Exception as e:
                return "error", str(e)
        
        return status, error
    except Exception as e:
        return "error", str(e)

def run_scheduler():
    """
    Run the scheduler in a separate thread.
    
    Note: This function is kept for backward compatibility but no longer schedules
    automatic health checks. Status is now updated directly when scrapers are run.
    """
    # No longer schedule automatic health checks
    # Just keep the thread running to avoid breaking existing code
    while not scheduler_stop_event.is_set():
        time.sleep(1)

def run_scraper(scraper_info: Dict[str, Any]) -> None:
    """
    Run a scraper in a separate process.
    
    Args:
        scraper_info: Scraper information dictionary
    """
    scraper_id = scraper_info["id"]
    
    # Check if scraper is already running
    with lock:
        if scraper_id in running_scrapers and running_scrapers[scraper_id].poll() is None:
            return
    
    # Update status to running - this is now redundant as the BaseScraper will update status,
    # but we keep it for backwards compatibility with any scrapers not using BaseScraper
    update_scraper_status(scraper_info, "running")
    
    # Determine the module to run
    if scraper_info["type"] == "base":
        module_path = f"scrapers.{scraper_info['court']}.{os.path.basename(scraper_info['file'])[:-3]}"
    else:
        module_path = f"scrapers.{scraper_info['court']}.{scraper_info['type']}.{os.path.basename(scraper_info['file'])[:-3]}"
    
    # Start the scraper process
    cmd = [sys.executable, "-m", module_path]
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Store the process
    with lock:
        running_scrapers[scraper_id] = process
        last_run_times[scraper_id] = datetime.now()
    
    # Wait for the process to complete
    stdout, stderr = process.communicate()
    
    # Update status based on exit code - this is now redundant as the BaseScraper will update status,
    # but we keep it for backwards compatibility with any scrapers not using BaseScraper
    if process.returncode == 0:
        update_scraper_status(scraper_info, "ok")
    else:
        update_scraper_status(scraper_info, "error", stderr)
    
    # Remove the process from running scrapers
    with lock:
        if scraper_id in running_scrapers:
            del running_scrapers[scraper_id]

@app.route("/")
def index():
    """Render the dashboard."""
    # Get all scrapers
    scrapers = get_scrapers()
    
    # Get last run times
    last_run_times = {}
    if os.path.exists(LAST_RUN_FILE):
        with open(LAST_RUN_FILE, "r") as f:
            last_run_times = json.load(f)
    
    # Get status for each scraper
    for scraper in scrapers:
        # Get status
        scraper["status"] = get_scraper_status(scraper["id"])
        
        # Add running status
        with lock:
            if scraper["id"] in running_scrapers and running_scrapers[scraper["id"]].poll() is None:
                scraper["status"]["status"] = "running"
        
        # Add last run time
        if scraper["id"] in last_run_times:
            scraper["status"]["last_run"] = last_run_times[scraper["id"]].isoformat()
        
        # Process history into daily summary
        scraper["daily_summary"] = calculate_daily_summary(scraper["status"])
        
        # Get status for specialized scrapers
        if "specialized" in scraper:
            for specialized in scraper["specialized"]:
                try:
                    # Get status
                    specialized["status"] = get_scraper_status(specialized["id"])
                    
                    # Add running status
                    with lock:
                        if specialized["id"] in running_scrapers and running_scrapers[specialized["id"]].poll() is None:
                            specialized["status"]["status"] = "running"
                    
                    # Add last run time
                    if specialized["id"] in last_run_times:
                        specialized["status"]["last_run"] = last_run_times[specialized["id"]].isoformat()
                    
                    # Process history into daily summary
                    specialized["daily_summary"] = calculate_daily_summary(specialized["status"])
                except Exception as e:
                    specialized["status"] = {"status": "unknown", "error": str(e)}
    
    # Pass the current time to the template in 24-hour IST format
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return render_template("dashboard.html", scrapers=scrapers, current_time=current_time)

@app.route("/api/scrapers")
def api_scrapers():
    """API endpoint to list all scrapers."""
    scrapers = get_scrapers()
    return jsonify(scrapers)

@app.route("/api/status")
def api_status():
    """API endpoint to get status of all scrapers."""
    scrapers = get_scrapers()
    
    # Get status for each scraper
    status = {}
    for scraper in scrapers:
        status[scraper["id"]] = get_scraper_status(scraper["id"])
        
        # Add specialized scrapers
        if "specialized" in scraper:
            for specialized in scraper["specialized"]:
                status[specialized["id"]] = get_scraper_status(specialized["id"])
    
    return jsonify(status)

@app.route("/api/status/<scraper_id>")
def api_status_scraper(scraper_id):
    """API endpoint to get status of a specific scraper."""
    status = get_scraper_status(scraper_id)
    return jsonify(status)

@app.route("/api/check/<scraper_id>")
def api_check_scraper(scraper_id):
    """API endpoint to check the health of a specific scraper."""
    # Find the scraper
    scrapers = get_scrapers()
    scraper_info = None
    
    for scraper in scrapers:
        if scraper["id"] == scraper_id:
            scraper_info = scraper
            break
        
        # Check specialized scrapers
        if "specialized" in scraper:
            for specialized in scraper["specialized"]:
                if specialized["id"] == scraper_id:
                    scraper_info = specialized
                    break
    
    if not scraper_info:
        return jsonify({"error": "Scraper not found"}), 404
    
    # Check the scraper health
    status, error = check_scraper_health(scraper_info)
    
    # Update status
    update_scraper_status(scraper_info, status, error)
    
    return jsonify({
        "id": scraper_id,
        "status": status,
        "error": error
    })

@app.route("/api/run/<scraper_id>")
def api_run_scraper(scraper_id):
    """API endpoint to run a specific scraper."""
    # Find the scraper
    scrapers = get_scrapers()
    scraper_info = None
    
    for scraper in scrapers:
        if scraper["id"] == scraper_id:
            scraper_info = scraper
            break
        
        # Check specialized scrapers
        if "specialized" in scraper:
            for specialized in scraper["specialized"]:
                if specialized["id"] == scraper_id:
                    scraper_info = specialized
                    break
    
    if not scraper_info:
        return jsonify({"error": "Scraper not found"}), 404
    
    # Check if scraper is already running
    with lock:
        if scraper_id in running_scrapers and running_scrapers[scraper_id].poll() is None:
            return jsonify({
                "id": scraper_id,
                "status": "running",
                "message": "Scraper is already running"
            })
    
    # Run the scraper in a separate thread
    thread = threading.Thread(target=run_scraper, args=(scraper_info,))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "id": scraper_id,
        "status": "running",
        "message": "Scraper started"
    })

@app.route("/run/<scraper_id>")
def run_scraper_web(scraper_id):
    """Web endpoint to run a specific scraper."""
    api_run_scraper(scraper_id)
    return redirect(url_for("index"))

@app.route("/check/<scraper_id>")
def check_scraper_web(scraper_id):
    """Web endpoint to check a specific scraper."""
    api_check_scraper(scraper_id)
    return redirect(url_for("index"))

@app.route('/api/history/<scraper_id>')
def get_scraper_history(scraper_id):
    """
    Get the history of a scraper for display in the dashboard.
    """
    try:
        status_data = get_scraper_status(scraper_id)
        
        # Process history into daily summary
        daily_summary = {}
        
        for entry in status_data.get("history", []):
            timestamp = entry.get("timestamp", "")
            date_str = timestamp.split("T")[0] if timestamp else ""
            
            # Format time in 24-hour IST format
            time_str = ""
            if timestamp and "T" in timestamp:
                time_part = timestamp.split("T")[1]
                if "." in time_part:
                    time_part = time_part.split(".")[0]  # Remove milliseconds
                # Format as HH:MM:SS IST
                time_str = f"{time_part} IST"
            
            if not date_str:
                continue
                
            if date_str not in daily_summary:
                daily_summary[date_str] = {
                    "date": date_str,
                    "statuses": [],
                    "errors": [],
                    "total_count": 0,
                    "ok_count": 0,
                    "uptime_percentage": 0,
                    "last_status": None,
                    "last_error": None,
                    "last_timestamp": None
                }
            
            status = entry.get("status")
            error = entry.get("error")
            
            daily_summary[date_str]["statuses"].append(status)
            daily_summary[date_str]["total_count"] += 1
            
            if status == "ok":
                daily_summary[date_str]["ok_count"] += 1
            elif status == "error" and error:
                daily_summary[date_str]["errors"].append(error)
            
            # Update last status, error, and timestamp
            daily_summary[date_str]["last_status"] = status
            if status == "error" and error:
                daily_summary[date_str]["last_error"] = error
            daily_summary[date_str]["last_timestamp"] = time_str
        
        # Calculate uptime percentage for each day
        for date_str, day_data in daily_summary.items():
            if day_data["total_count"] > 0:
                day_data["uptime_percentage"] = (day_data["ok_count"] / day_data["total_count"]) * 100
        
        # Convert to list and sort by date (newest first)
        daily_summary_list = list(daily_summary.values())
        daily_summary_list.sort(key=lambda x: x["date"], reverse=True)
        
        return jsonify({
            "scraper_id": scraper_id,
            "daily_summary": daily_summary
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def calculate_daily_summary(status: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Process scraper history into daily summary.
    """
    try:
        # Process history into daily summary
        daily_summary = {}
        
        for entry in status.get("history", []):
            timestamp = entry.get("timestamp", "")
            date_str = timestamp.split("T")[0] if timestamp else ""
            
            # Format time in 24-hour IST format
            time_str = ""
            if timestamp and "T" in timestamp:
                time_part = timestamp.split("T")[1]
                if "." in time_part:
                    time_part = time_part.split(".")[0]  # Remove milliseconds
                # Format as HH:MM:SS IST
                time_str = f"{time_part} IST"
            
            if not date_str:
                continue
                
            if date_str not in daily_summary:
                daily_summary[date_str] = {
                    "date": date_str,
                    "statuses": [],
                    "errors": [],
                    "total_count": 0,
                    "ok_count": 0,
                    "uptime_percentage": 0,
                    "last_status": None,
                    "last_error": None,
                    "last_timestamp": None
                }
            
            status_val = entry.get("status")
            error = entry.get("error")
            
            daily_summary[date_str]["statuses"].append(status_val)
            daily_summary[date_str]["total_count"] += 1
            
            if status_val == "ok":
                daily_summary[date_str]["ok_count"] += 1
            elif status_val == "error" and error:
                daily_summary[date_str]["errors"].append(error)
            
            # Update last status, error, and timestamp
            daily_summary[date_str]["last_status"] = status_val
            if status_val == "error" and error:
                daily_summary[date_str]["last_error"] = error
            daily_summary[date_str]["last_timestamp"] = time_str
        
        # Calculate uptime percentage for each day
        for date_str, day_data in daily_summary.items():
            if day_data["total_count"] > 0:
                day_data["uptime_percentage"] = (day_data["ok_count"] / day_data["total_count"]) * 100
        
        # Convert to list and sort by date (newest first)
        daily_summary_list = list(daily_summary.values())
        daily_summary_list.sort(key=lambda x: x["date"], reverse=True)
        
        return daily_summary_list
    except Exception as e:
        print(f"Error processing daily summary: {e}")
        return []

if __name__ == "__main__":
    # Create templates directory if it doesn't exist
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
    os.makedirs(templates_dir, exist_ok=True)
    
    # Start the scheduler in a separate thread
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    # Run the app
    try:
        app.run(host="0.0.0.0", port=5001, debug=True, use_reloader=False)
    finally:
        # Stop the scheduler when the app is shutting down
        scheduler_stop_event.set()
        scheduler_thread.join(timeout=1)

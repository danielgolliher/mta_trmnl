"""
MTA L Train Arrivals for TRMNL
Fetches real-time subway arrivals at Metropolitan Ave / Lorimer St
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime
import pytz
from nyct_gtfs import NYCTFeed

app = FastAPI(title="MTA L Train Arrivals for TRMNL")

# Metropolitan Ave / Lorimer St stop IDs
# The L train uses stop IDs like "L10" with N/S suffix for direction
# L10N = Manhattan-bound, L10S = Canarsie-bound
STOP_ID = "L10"
MANHATTAN_BOUND = f"{STOP_ID}N"
CANARSIE_BOUND = f"{STOP_ID}S"

# NYC timezone
NYC_TZ = pytz.timezone("America/New_York")


def get_arrivals():
    """Fetch real-time L train arrivals at Metropolitan/Lorimer"""
    try:
        feed = NYCTFeed("L")
        now = datetime.now(NYC_TZ)
        
        arrivals = {
            "manhattan": [],  # Northbound to 8th Ave
            "canarsie": [],   # Southbound to Canarsie/Rockaway Pkwy
        }
        
        for trip in feed.trips:
            # Check each stop in this trip's schedule
            for stop_update in trip.stop_time_updates:
                stop_id = stop_update.stop_id
                
                # Check if this train stops at our station
                if stop_id in [MANHATTAN_BOUND, CANARSIE_BOUND]:
                    arrival_time = stop_update.arrival
                    if arrival_time is None:
                        continue
                    
                    # Calculate minutes until arrival
                    if hasattr(arrival_time, 'timestamp'):
                        arrival_dt = datetime.fromtimestamp(arrival_time.timestamp(), NYC_TZ)
                    else:
                        arrival_dt = arrival_time.replace(tzinfo=NYC_TZ) if arrival_time.tzinfo is None else arrival_time
                    
                    minutes = int((arrival_dt - now).total_seconds() / 60)
                    
                    # Only include trains arriving in the future (and within 60 min)
                    if 0 <= minutes <= 60:
                        train_info = {
                            "minutes": minutes,
                            "arrival_time": arrival_dt.strftime("%-I:%M %p"),
                        }
                        
                        if stop_id == MANHATTAN_BOUND:
                            arrivals["manhattan"].append(train_info)
                        else:
                            arrivals["canarsie"].append(train_info)
        
        # Sort by arrival time and limit to next 5 trains each direction
        arrivals["manhattan"] = sorted(arrivals["manhattan"], key=lambda x: x["minutes"])[:5]
        arrivals["canarsie"] = sorted(arrivals["canarsie"], key=lambda x: x["minutes"])[:5]
        
        return arrivals
        
    except Exception as e:
        return {"error": str(e), "manhattan": [], "canarsie": []}


@app.get("/")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "station": "Metropolitan Ave / Lorimer St", "line": "L"}


@app.get("/arrivals")
def get_train_arrivals():
    """
    Get upcoming L train arrivals at Metropolitan Ave / Lorimer St
    Returns JSON formatted for TRMNL polling
    """
    now = datetime.now(NYC_TZ)
    arrivals = get_arrivals()
    
    return JSONResponse({
        "station": "Metropolitan / Lorimer",
        "line": "L",
        "updated": now.strftime("%-I:%M %p"),
        "updated_date": now.strftime("%a %b %-d"),
        "manhattan": arrivals.get("manhattan", []),
        "canarsie": arrivals.get("canarsie", []),
        "error": arrivals.get("error")
    })


@app.get("/arrivals/trmnl")
def get_train_arrivals_trmnl():
    """
    Formatted specifically for TRMNL's merge_variables structure
    """
    now = datetime.now(NYC_TZ)
    arrivals = get_arrivals()
    
    # Format for easy display
    manhattan_display = []
    for train in arrivals.get("manhattan", []):
        if train["minutes"] == 0:
            manhattan_display.append("Now")
        elif train["minutes"] == 1:
            manhattan_display.append("1 min")
        else:
            manhattan_display.append(f"{train['minutes']} min")
    
    canarsie_display = []
    for train in arrivals.get("canarsie", []):
        if train["minutes"] == 0:
            canarsie_display.append("Now")
        elif train["minutes"] == 1:
            canarsie_display.append("1 min")
        else:
            canarsie_display.append(f"{train['minutes']} min")
    
    return JSONResponse({
        "station": "Metropolitan / Lorimer",
        "line": "L",
        "updated": now.strftime("%-I:%M %p"),
        "manhattan_trains": arrivals.get("manhattan", []),
        "canarsie_trains": arrivals.get("canarsie", []),
        "manhattan_next": manhattan_display[0] if manhattan_display else "No trains",
        "canarsie_next": canarsie_display[0] if canarsie_display else "No trains",
        "manhattan_following": ", ".join(manhattan_display[1:4]) if len(manhattan_display) > 1 else "",
        "canarsie_following": ", ".join(canarsie_display[1:4]) if len(canarsie_display) > 1 else "",
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

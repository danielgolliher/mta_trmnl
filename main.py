"""
MTA L Train Arrivals for TRMNL
Fetches real-time subway arrivals at Metropolitan Ave / Lorimer St
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
from nyct_gtfs import NYCTFeed

app = FastAPI(title="MTA L Train Arrivals for TRMNL")

# Metropolitan Ave / Lorimer St stop IDs
# L10N = Manhattan-bound (toward 8th Ave)
# L10S = Canarsie-bound (toward Rockaway Pkwy)
MANHATTAN_STOP_ID = "L10N"
CANARSIE_STOP_ID = "L10S"


def get_arrivals():
    """Fetch real-time L train arrivals at Metropolitan/Lorimer"""
    try:
        feed = NYCTFeed("L")
        now = datetime.now(timezone.utc)
        
        arrivals = {
            "manhattan": [],  # Northbound to 8th Ave
            "canarsie": [],   # Southbound to Canarsie/Rockaway Pkwy
        }
        
        # Get all trains heading to our station (Manhattan-bound)
        manhattan_trains = feed.filter_trips(headed_for_stop_id=MANHATTAN_STOP_ID)
        for train in manhattan_trains:
            # Find the stop_time_update for our specific stop
            for stop in train.stop_time_updates:
                if stop.stop_id == MANHATTAN_STOP_ID:
                    arrival_time = stop.arrival
                    if arrival_time is None:
                        continue
                    
                    # arrival_time is already a datetime object
                    # Make sure we handle timezone properly
                    if arrival_time.tzinfo is None:
                        arrival_time = arrival_time.replace(tzinfo=timezone.utc)
                    
                    # Calculate minutes until arrival
                    delta = arrival_time - now
                    minutes = int(delta.total_seconds() / 60)
                    
                    # Only include trains arriving soon (not in the past, within 60 min)
                    if 0 <= minutes <= 60:
                        arrivals["manhattan"].append({
                            "minutes": minutes,
                            "arrival_time": arrival_time.strftime("%-I:%M %p"),
                            "headsign": train.headsign_text or "8 Av",
                        })
                    break  # Found our stop, move to next train
        
        # Get all trains heading to our station (Canarsie-bound)
        canarsie_trains = feed.filter_trips(headed_for_stop_id=CANARSIE_STOP_ID)
        for train in canarsie_trains:
            for stop in train.stop_time_updates:
                if stop.stop_id == CANARSIE_STOP_ID:
                    arrival_time = stop.arrival
                    if arrival_time is None:
                        continue
                    
                    if arrival_time.tzinfo is None:
                        arrival_time = arrival_time.replace(tzinfo=timezone.utc)
                    
                    delta = arrival_time - now
                    minutes = int(delta.total_seconds() / 60)
                    
                    if 0 <= minutes <= 60:
                        arrivals["canarsie"].append({
                            "minutes": minutes,
                            "arrival_time": arrival_time.strftime("%-I:%M %p"),
                            "headsign": train.headsign_text or "Canarsie-Rockaway Pkwy",
                        })
                    break
        
        # Sort by arrival time and limit to next 6 trains each direction
        arrivals["manhattan"] = sorted(arrivals["manhattan"], key=lambda x: x["minutes"])[:6]
        arrivals["canarsie"] = sorted(arrivals["canarsie"], key=lambda x: x["minutes"])[:6]
        
        return arrivals
        
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc(), "manhattan": [], "canarsie": []}


@app.get("/")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "station": "Metropolitan Ave / Lorimer St", "line": "L"}


@app.get("/arrivals")
def get_train_arrivals():
    """
    Get upcoming L train arrivals at Metropolitan Ave / Lorimer St
    Returns raw JSON with all arrival data
    """
    from zoneinfo import ZoneInfo
    now = datetime.now(ZoneInfo("America/New_York"))
    arrivals = get_arrivals()
    
    return JSONResponse({
        "station": "Metropolitan / Lorimer",
        "line": "L",
        "updated": now.strftime("%-I:%M %p"),
        "updated_date": now.strftime("%a %b %-d"),
        "manhattan": arrivals.get("manhattan", []),
        "canarsie": arrivals.get("canarsie", []),
        "error": arrivals.get("error"),
        "traceback": arrivals.get("traceback"),
    })


@app.get("/arrivals/trmnl")
def get_train_arrivals_trmnl():
    """
    Formatted specifically for TRMNL's merge_variables structure
    Shows Manhattan-bound trains prominently
    """
    from zoneinfo import ZoneInfo
    now = datetime.now(ZoneInfo("America/New_York"))
    arrivals = get_arrivals()
    
    manhattan_trains = arrivals.get("manhattan", [])
    canarsie_trains = arrivals.get("canarsie", [])
    
    # Format arrival times for display
    def format_minutes(mins):
        if mins == 0:
            return "Now"
        elif mins == 1:
            return "1 min"
        else:
            return f"{mins} min"
    
    # Build display strings
    manhattan_display = [format_minutes(t["minutes"]) for t in manhattan_trains]
    canarsie_display = [format_minutes(t["minutes"]) for t in canarsie_trains]
    
    # Build detailed train list for template iteration
    manhattan_list = [
        {"minutes": format_minutes(t["minutes"]), "time": t["arrival_time"]}
        for t in manhattan_trains
    ]
    canarsie_list = [
        {"minutes": format_minutes(t["minutes"]), "time": t["arrival_time"]}
        for t in canarsie_trains
    ]
    
    return JSONResponse({
        "station": "Metropolitan / Lorimer",
        "line": "L",
        "updated": now.strftime("%-I:%M %p"),
        
        # Full train lists for iteration in template
        "manhattan_list": manhattan_list,
        "canarsie_list": canarsie_list,
        
        # Quick access to next trains
        "manhattan_next": manhattan_display[0] if manhattan_display else "No trains",
        "manhattan_next_time": manhattan_trains[0]["arrival_time"] if manhattan_trains else "",
        
        "canarsie_next": canarsie_display[0] if canarsie_display else "No trains",
        "canarsie_next_time": canarsie_trains[0]["arrival_time"] if canarsie_trains else "",
        
        # Following trains as comma-separated string
        "manhattan_following": ", ".join(manhattan_display[1:4]) if len(manhattan_display) > 1 else "",
        "canarsie_following": ", ".join(canarsie_display[1:4]) if len(canarsie_display) > 1 else "",
        
        # Error info for debugging
        "error": arrivals.get("error"),
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

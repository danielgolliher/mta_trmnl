# MTA L Train Arrivals for TRMNL

Display real-time L train arrivals at Metropolitan Ave / Lorimer St on your TRMNL e-ink display.

## Quick Start

### 1. Deploy the Server

You need to host this API somewhere. Here are free options:

#### Option A: Railway (Recommended - easiest)
1. Go to [railway.app](https://railway.app)
2. Sign up / log in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Connect this repository
5. Railway will auto-detect it's a Python app and deploy
6. Copy your deployment URL (something like `https://mta-trmnl-production.up.railway.app`)

#### Option B: Render
1. Go to [render.com](https://render.com)
2. New → Web Service
3. Connect your GitHub repo
4. Settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Deploy and copy your URL

#### Option C: Run Locally (for testing)
```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
# or
uvicorn main:app --reload
```

Then visit `http://localhost:8000/arrivals/trmnl` to see the JSON output.

### 2. Set Up TRMNL Private Plugin

1. **Get Developer Edition** (if you don't have it)
   - Go to [usetrmnl.com/upgrade](https://usetrmnl.com/upgrade)
   - One-time $20 fee

2. **Create the Plugin**
   - Log into TRMNL → Plugins → Search "Private Plugin" → Add
   - Name: `L Train Arrivals` (or whatever you want)
   - Strategy: **Polling**
   - Polling URL: `https://YOUR-DEPLOYED-URL/arrivals/trmnl`
   - Polling Verb: GET
   - Click Save

3. **Add the Markup Template**
   - Click "Edit Markup" on your plugin
   - Copy the contents of `trmnl-template.liquid` from this repo
   - Paste it into the markup editor
   - Save

4. **Add to Your Playlist**
   - Go to your device's playlist
   - Add the L Train Arrivals plugin
   - Set refresh interval (e.g., every 5 minutes)

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Health check |
| `GET /arrivals` | Raw arrival data as JSON |
| `GET /arrivals/trmnl` | Formatted for TRMNL polling |

### Example Response (`/arrivals/trmnl`)

```json
{
  "station": "Metropolitan / Lorimer",
  "line": "L",
  "updated": "9:42 AM",
  "manhattan_list": [
    {"minutes": "3 min", "time": "9:45 AM"},
    {"minutes": "8 min", "time": "9:50 AM"},
    {"minutes": "14 min", "time": "9:56 AM"},
    {"minutes": "22 min", "time": "10:04 AM"}
  ],
  "canarsie_list": [
    {"minutes": "1 min", "time": "9:43 AM"},
    {"minutes": "7 min", "time": "9:49 AM"}
  ],
  "manhattan_next": "3 min",
  "manhattan_next_time": "9:45 AM",
  "canarsie_next": "1 min",
  "canarsie_next_time": "9:43 AM",
  "manhattan_following": "8 min, 14 min, 22 min",
  "canarsie_following": "7 min"
}
```

## TRMNL Templates

Two templates are included:

1. **`trmnl-template.liquid`** - Shows both directions with Manhattan trains prominently displayed
2. **`trmnl-template-manhattan-only.liquid`** - Shows only Manhattan-bound trains (simpler layout)

## Customizing for a Different Station

To use a different L train station, edit `main.py` and change the `STOP_ID`:

```python
# L Train Stop IDs (from MTA GTFS data):
# L01 = 8th Ave
# L02 = 6th Ave
# L03 = Union Sq - 14th St
# L05 = 3rd Ave
# L06 = 1st Ave
# L08 = Bedford Ave
# L10 = Lorimer St / Metropolitan Ave  <-- current
# L11 = Graham Ave
# L12 = Grand St
# L13 = Montrose Ave
# L14 = Morgan Ave
# L15 = Jefferson St
# L16 = DeKalb Ave
# L17 = Myrtle Ave - Wyckoff Ave
# L19 = Halsey St
# L20 = Wilson Ave
# L21 = Bushwick Ave - Aberdeen St
# L22 = Broadway Junction
# L24 = Atlantic Ave
# L25 = Sutter Ave
# L26 = Livonia Ave
# L27 = New Lots Ave
# L28 = East 105th St
# L29 = Canarsie - Rockaway Pkwy

STOP_ID = "L10"  # Change this to your station
```

## How It Works

1. The server fetches real-time data from the MTA's GTFS-RT feed (no API key required!)
2. It filters for trains stopping at Metropolitan/Lorimer
3. Calculates minutes until arrival
4. Returns clean JSON that TRMNL can display

The MTA feed URL: `https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct/gtfs-l`

## What The Display Shows

The display shows **actual real-time arrival times** pulled from the MTA's GTFS real-time feed - the same data that powers the countdown clocks in subway stations.

For example, if the next Manhattan-bound L train arrives at 9:45 AM (3 minutes from now), you'll see:
- **3 min** (time until arrival)
- **9:45 AM** (actual arrival time)

## Troubleshooting

**No trains showing?**
- The L train runs less frequently late night/early morning
- Check the raw data at `/arrivals` endpoint - it includes error messages if something's wrong

**Times seem wrong?**
- The MTA feed uses UTC internally; times are converted to Eastern time for display
- Check if there are service alerts on the L train

**Display not updating?**
- Check your TRMNL playlist refresh interval
- Verify your server is running (visit the `/` health check endpoint)
- The `/arrivals` endpoint shows a `traceback` field if there's an error

**Testing locally?**
```bash
# Run the server
python main.py

# In another terminal, test the endpoints:
curl http://localhost:8000/arrivals | python -m json.tool
curl http://localhost:8000/arrivals/trmnl | python -m json.tool
```

## License

MIT - do whatever you want with it!

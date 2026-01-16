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
  "manhattan_trains": [
    {"minutes": 3, "arrival_time": "9:45 AM"},
    {"minutes": 8, "arrival_time": "9:50 AM"},
    {"minutes": 14, "arrival_time": "9:56 AM"}
  ],
  "canarsie_trains": [
    {"minutes": 1, "arrival_time": "9:43 AM"},
    {"minutes": 7, "arrival_time": "9:49 AM"}
  ],
  "manhattan_next": "3 min",
  "canarsie_next": "1 min",
  "manhattan_following": "8 min, 14 min",
  "canarsie_following": "7 min"
}
```

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

## Troubleshooting

**No trains showing?**
- The L train runs less frequently late night/early morning
- Check if the MTA feed is working: visit the raw endpoint `/arrivals`

**Display not updating?**
- Check your TRMNL playlist refresh interval
- Verify your server is running (visit the `/` health check endpoint)

**Wrong station?**
- Double-check the `STOP_ID` in `main.py`
- The stop ID format is `L##` where ## is the station number

## License

MIT - do whatever you want with it!

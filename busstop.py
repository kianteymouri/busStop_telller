import requests
from PIL import Image, ImageDraw, ImageFont
import time, os
from datetime import datetime

API_KEY = "put your own api here"
DEBUG = False  # Set True to see which stops/routes return data


#change these stops to ur own, visit google maps and click on stop for stop ID
ROUTES = [
    {"label": "Bus 36E", "route_id": "36", "stop_id": "50575", "dest": "RSF / Telegraph"},
    {"label": "Bus 7",  "route_id": "7",  "stop_id": "55452", "dest": "Soda Hall"},
    {"label": "Bus 12N", "route_id": "12", "stop_id": "51622", "dest": "Trader Joe's"},
    {"label": "Bus 12S", "route_id": "12", "stop_id": "58115", "dest": "Ashby Station"},
    {"label": "Bus 36W", "route_id": "36", "stop_id": "58575", "dest": "Emeryville"},
]

def safe_json(resp):
    try:
        return resp.json()
    except Exception:
        return []

def fetch_arrivals(stop_id, route_id, label, dest_name):
    """Fetch live predictions, then fallback to near-term schedule"""
    arrivals = []
    now = datetime.now()

    # --- Try live data ---
    try:
        url = f"https://api.actransit.org/transit/stops/{stop_id}/predictions?token={API_KEY}"
        resp = requests.get(url, timeout=5)
        data = safe_json(resp)
        for p in data:
            route = p.get("RouteName", "")
            if route != route_id:
                continue
            dep_str = p.get("PredictedDeparture")
            if dep_str:
                dep_time = datetime.strptime(dep_str, "%Y-%m-%dT%H:%M:%S")
                mins = int((dep_time - now).total_seconds() / 60)
                if 0 <= mins <= 90:
                    arrivals.append({
                        "label": label,
                        "dest": dest_name + " (live)",
                        "eta": f"{mins} min ({dep_time.strftime('%I:%M %p')})",
                        "abs_time": dep_time
                    })
    except Exception as e:
        print(f"Live fetch error for {stop_id}: {e}")

    # --- Fallback to scheduled trips if no live buses soon ---
    if not arrivals:
        try:
            sched_url = f"https://api.actransit.org/transit/route/{route_id}/schedule/current?stopId={stop_id}&token={API_KEY}"
            resp = requests.get(sched_url, timeout=5)
            data = safe_json(resp)
            for s in data:
                dep_str = s.get("DepartureTime")
                if dep_str:
                    dep_time = datetime.strptime(dep_str, "%Y-%m-%dT%H:%M:%S")
                    mins = int((dep_time - now).total_seconds() / 60)
                    if 0 <= mins <= 90:  # only next hour & a half
                        arrivals.append({
                            "label": label,
                            "dest": dest_name + " (sched.)",
                            "eta": f"{mins} min ({dep_time.strftime('%I:%M %p')})",
                            "abs_time": dep_time
                        })
        except Exception as e:
            print(f"Schedule fallback error for {stop_id}: {e}")

    return arrivals


def draw_display(flat_arrivals):
    """Render the display"""
    width, height = 800, 480
    img = Image.new('1', (width, height), 255)
    draw = ImageDraw.Draw(img)

    try:
        font_large = ImageFont.truetype("/Library/Fonts/Arial Bold.ttf", 22)
        font_medium = ImageFont.truetype("/Library/Fonts/Arial.ttf", 18)
        font_small = ImageFont.truetype("/Library/Fonts/Arial.ttf", 16)
    except:
        font_large = font_medium = font_small = ImageFont.load_default()

    # Header bar
    draw.rectangle([(0, 0), (width, 45)], fill=0)
    draw.text((10, 10), "UPCOMING BUS ARRIVALS", font=font_large, fill=255)
    now = datetime.now().strftime("%I:%M %p")
    draw.text((width // 2 - 50, 10), now, font=font_medium, fill=255)
    draw.text((width - 100, 10), "ETA", font=font_large, fill=255)

    # Rows
    start_y = 60
    row_h = 50
    max_rows = 8

    if not flat_arrivals:
        draw.text((20, start_y + 20), "No upcoming buses right now.", font=font_medium, fill=0)
    else:
        for i, bus in enumerate(flat_arrivals[:max_rows]):
            y = start_y + i * row_h
            if i % 2 == 0:
                draw.rectangle([(0, y), (width, y + row_h)], fill=240)
            draw.text((20, y + 12), bus["label"], font=font_large, fill=0)
            draw.text((160, y + 15), bus["dest"], font=font_small, fill=0)
            draw.text((width - 220, y + 12), bus["eta"], font=font_small, fill=0)

    draw.text((10, height - 25),
              f"Updated: {datetime.now().strftime('%b %d, %Y %H:%M:%S')}",
              font=font_small, fill=0)

    desktop_path = os.path.expanduser("~/Desktop/bus_display_preview.png")
    img.save(desktop_path)
    print(f"✅ Updated board saved to {desktop_path}")

def main_loop():
    """Main updater"""
    while True:
        all_arrivals = []
        for info in ROUTES:
            arrivals = fetch_arrivals(info["stop_id"], info["route_id"], info["label"], info["dest"])
            all_arrivals.extend(arrivals)

        all_arrivals.sort(key=lambda x: x["abs_time"])
        draw_display(all_arrivals)
        time.sleep(60)

if __name__ == "__main__":
    main_loop()

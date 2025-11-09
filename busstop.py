cp /home/kian/bus_board_epaper.py /home/kian/bus_board_epaper.py.bak

cat > /home/kian/bus_board_epaper.py << 'PY'
#!/usr/bin/env python3
import os, time, requests
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

#change to ur own
API_KEY = "________"

# Panel settings
WIDTH, HEIGHT = 800, 480       # set to 880, 528 if you have 7.5" HD
HD_PANEL = False               # True if your panel is the 7.5 HD (880x528)
REFRESH_SEC = 60

HEADER_TEXT = "UPCOMING BUSSES"


#change these routes.
ROUTES = [
    {"label": "Bus 36E", "route_id": "36", "stop_id": "50575", "dest": "RSF / Telegraph"},
    {"label": "Bus 7",   "route_id": "7",  "stop_id": "55452", "dest": "Soda Hall"},
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
    rows, now = [], datetime.now()
    # live
    try:
        url = f"https://api.actransit.org/transit/stops/{stop_id}/predictions?token={API_KEY}"
        data = safe_json(requests.get(url, timeout=6))
        for p in data:
            if p.get("RouteName") != route_id:
                continue
            s = p.get("PredictedDeparture")
            if not s:
                continue
            t = datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")
            mins = int((t - now).total_seconds() / 60)
            if 0 <= mins <= 120:
                rows.append({
                    "label": label,
                    "dest": dest_name + " (live)",
                    "eta_str": f"{mins} min ({t.strftime('%I:%M %p')})",
                    "abs_time": t
                })
    except Exception as e:
        print(f"Live fetch error @ {stop_id}/{route_id}: {e}")

    # schedule fallback if none
    if not rows:
        try:
            url = f"https://api.actransit.org/transit/route/{route_id}/schedule/current?stopId={stop_id}&token={API_KEY}"
            data = safe_json(requests.get(url, timeout=8))
            for s in data:
                ds = s.get("DepartureTime")
                if not ds:
                    continue
                t = datetime.strptime(ds, "%Y-%m-%dT%H:%M:%S")
                mins = int((t - now).total_seconds() / 60)
                if 0 <= mins <= 120:
                    rows.append({
                        "label": label,
                        "dest": dest_name + " (sched)",
                        "eta_str": f"{mins} min ({t.strftime('%I:%M %p')})",
                        "abs_time": t
                    })
        except Exception as e:
            print(f"Schedule fetch error @ {stop_id}/{route_id}: {e}")
    return rows

def draw_display(rows):
    img = Image.new('1', (WIDTH, HEIGHT), 1)  # 1 = white, 0 = black
    d = ImageDraw.Draw(img)

    BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    REG ="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    def font(path, size):
        try: return ImageFont.truetype(path, size)
        except: return ImageFont.load_default()

    f_header = font(BOLD, 40)
    f_label  = font(BOLD, 34)   # route label
    f_dest   = font(REG, 24)    # destination
    f_eta    = font(BOLD, 34)   # eta
    f_small  = font(REG, 20)

    def text_w(s, f): return d.textlength(s, font=f)

    # header bar
    top = 64
    d.rectangle((0,0,WIDTH,top), fill=0)
    d.text((16,10), HEADER_TEXT, font=f_header, fill=1)

    # right-align the clock inside a 16 px right margin
    clock = datetime.now().strftime("%I:%M %p").lstrip("0")
    cw = text_w(clock, f_label)
    d.text((WIDTH - 16 - cw, 12), clock, font=f_label, fill=1)

    d.line((0, top, WIDTH, top), fill=0, width=2)

    # columns
    left_margin = 16
    right_margin = 16
    label_x=left_margin
    dest_x = 200
    sample_h = max(f_label.getbbox("A")[3], f_eta.getbbox("A")[3])
    row_h = sample_h + 22
    y = top + 8

    def clip(s, f, maxw):
        if text_w(s, f) <= maxw: return s
        ell = "…"
        while s and text_w(s + ell, f) > maxw:
            s = s[:-1]
        return s + ell if s else ell

    if rows:
        rows.sort(key=lambda r: r["abs_time"])
        for r in rows:
            if y + row_h > HEIGHT - 36:
                break
            d.line((0, y, WIDTH, y), fill=0, width=1)

            # left: route label
            d.text((label_x, y + 8), r["label"], font=f_label, fill=0)

            # right: ETA, right-aligned against right margin
            eta = r["eta_str"]
            eta_w = text_w(eta, f_eta)
            eta_right_x = WIDTH - right_margin
            eta_x = eta_right_x - eta_w
            d.text((eta_x, y + 8), eta, font=f_eta, fill=0)

            # middle: destination, truncated to stop before ETA
            max_dest_w = eta_x - dest_x - 12
            d.text((dest_x, y + 10), clip(r["dest"], f_dest, max_dest_w), font=f_dest, fill=0)

            y += row_h

        d.line((0, y, WIDTH, y), fill=0, width=2)
    else:
        d.text((label_x, y + 10), "No upcoming buses right now.", font=f_label, fill=0)

    # footer
    d.text((16, HEIGHT-28), f"Updated: {datetime.now().strftime('%b %d, %Y %H:%M:%S')}",
           font=f_small, fill=0)
    return img

def push_epaper(img):
    import sys
    sys.path.append(os.path.expanduser('~/e-Paper/RaspberryPi_JetsonNano/python/lib'))
    from waveshare_epd import epd7in5_V2, epd7in5_HD
    driver = epd7in5_HD if HD_PANEL else epd7in5_V2
    epd = driver.EPD()
    epd.init()
    epd.Clear()
    epd.display(epd.getbuffer(img.convert("1")))
    epd.sleep()
    print("Pushed to e-paper")

def main():
    while True:
        rows = []
        for r in ROUTES:
            rows += fetch_arrivals(r["stop_id"], r["route_id"], r["label"], r["dest"])
        img = draw_display(rows)
        out = os.path.expanduser('~/Desktop/bus_display_preview.png')
        img.save(out); print("Saved", out)
        try:
            push_epaper(img)
        except Exception as e:
            print(f"E-paper push failed: {e}")
        time.sleep(REFRESH_SEC)

if __name__ == "__main__":
    main()
PY
chmod +x /home/kian/bus_board_epaper.py

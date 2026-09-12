import os
import time
import requests
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

DB = "https://alertasismica-bf17b-default-rtdb.firebaseio.com/alerta.json"
USGS = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
LAST = None

def push(act, epi="Normal", s=0):
    d = {"alerta_activa": "true" if act else "false", "epicentro": epi, "segundos_restantes": str(s)}
    try:
        requests.put(DB, json=d, timeout=10)
    except:
        pass

def loop():
    global LAST
    while True:
        try:
            r = requests.get(USGS, timeout=10)
            if r.status_code == 200:
                fts = r.json().get("features", [])
                if fts:
                    f = fts[0]
                    sid = f.get("id")
                    p = f.get("properties", {})
                    mag = p.get("mag")
                    plc = p.get("place") or "Sismo"
                    t1 = p.get("time", 0)
                    t0 = int(time.time() * 1000)
                    if mag and mag >= 4.5 and (t0 - t1) < 300000:
                        if sid != LAST:
                            LAST = sid
                            push(True, f"M{mag} - {plc}", 35)
                            time.sleep(45)
                            push(False, f"Ultimo: M{mag}", 0)
        except:
            pass
        time.sleep(15)

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

if __name__ == "__main__":
    t = threading.Thread(target=loop, daemon=True)
    t.start()
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), H).serve_forever()

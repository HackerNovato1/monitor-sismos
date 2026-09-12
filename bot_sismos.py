import os
import time
import requests
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

DB = "https://alertasismica-bf17b-default-rtdb.firebaseio.com/alerta.json"
USGS = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
LAST = None

# --- LIMITES GEOGRAFICOS PARA EL SALVADOR Y COSTAS CERCANAS ---
LAT_MIN = 11.5
LAT_MAX = 15.0
LON_MIN = -91.5
LON_MAX = -87.0

def push(act, epi="Normal", s=0):
    d = {"alerta_activa": "true" if act else "false", "epicentro": epi, "segundos_restantes": str(s)}
    try:
        requests.put(DB, json=d, timeout=10)
    except:
        pass

def es_zona_local(lat, lon, lugar):
    # 1. Comprobación por coordenadas
    if LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX:
        return True
    # 2. Comprobación por nombre
    lugar_lower = lugar.lower()
    paises = ["el salvador", "salvador", "guatemala", "honduras", "nicaragua"]
    if any(p in lugar_lower for p in paises):
        return True
    return False

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
                    geom = f.get("geometry", {})
                    coords = geom.get("coordinates", [0, 0])
                    
                    lon = coords[0]
                    lat = coords[1]
                    mag = p.get("mag")
                    plc = p.get("place") or "Sismo"
                    t1 = p.get("time", 0)
                    t0 = int(time.time() * 1000)
                    
                    # Magnitud >= 4.0, reciente (< 5 min) y en la zona de interes
                    if mag and mag >= 4.0 and (t0 - t1) < 300000:
                        if es_zona_local(lat, lon, plc):
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
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

if __name__ == "__main__":
    t = threading.Thread(target=loop, daemon=True)
    t.start()
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), H).serve_forever()

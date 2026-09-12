import time
import requests
import threading
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- CONFIGURACIÓN DE FIREBASE ---
DB_ENDPOINT = "https://alertasismica-bf17b-default-rtdb.firebaseio.com/alerta.json"
USGS_API_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"

MAGNITUD_MINIMA = 4.5
ULTIMO_ID_PROCESADO = None

def actualizar_firebase(activa, epicentro="Normal", segundos=0):
    payload = {
        "alerta_activa": "true" if activa else "false",
        "epicentro": epicentro,
        "segundos_restantes": str(segundos)
    }
    try:
        resp = requests.put(DB_ENDPOINT, json=payload, timeout=10)
        print(f"[*] Firebase actualizado -> Activa: {activa} | {epicentro}")
    except Exception as e:
        print(f"[!] Error al actualizar Firebase: {e}")

def vigilar_sismos():
    global ULTIMO_ID_PROCESADO
    print("[*] Vigilante de sismos 24/7 iniciado correctamente...", flush=True)

    while True:
        try:
            r = requests.get(USGS_API_URL, timeout=10)
            if r.status_code == 200:
                data = r.json()
                features = data.get("features", [])

                if len(features) > 0:
                    ultimo_sismo = features[0]
                    sismo_id = ultimo_sismo.get("id")
                    props = ultimo_sismo.get("properties", {})
                    
                    mag = props.get("mag")
                    lugar = props.get("place", "Ubicacion no especificada")
                    tiempo_ms = props.get("time", 0)

                    tiempo_actual_ms = int(time.time() * 1000)
                    es_reciente = (tiempo_actual_ms - tiempo_ms) < (5 * 60 * 1000)

                    if mag is not None and mag >= MAGNITUD_MINIMA and es_reciente:
                        if sismo_id != ULTIMO_ID_PROCESADO:
                            ULTIMO_ID_PROCESADO = sismo_id
                            print(f"\n[ALERTA SISMO DETECTADA] M{mag} - {lugar}", flush=True)
                            
                            actualizar_firebase(True, f"M{mag} - {lugar}", 35)
                            time.sleep(45)
                            actualizar_firebase(False, f"Ultimo: M{mag} - {lugar}", 0)

        except Exception as err:
            print(f"[!] Error temporal en ciclo: {err}", flush=True)

        time.sleep(15)

# Servidor Web ligero para Render
class WebHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Monitor Sismico Activo 24/7")

def iniciar_servidor_web():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), WebHandler)
    print(f"[*] Servidor web iniciado en puerto {port}", flush=True)
    server.serve_forever()

if __name__ == "__main__":
    # Inicia el vigilante en segundo plano
    hilo_sismos = threading.Thread(target=vigilar_sismos)
    hilo_sismos.daemon = True
    hilo_sismos.start()

    # Inicia el servidor web en primer plano para Render
    iniciar_servidor_web()
    if len(features) > 0:
                    ultimo_sismo = features[0]
                    sismo_id = ultimo_sismo.get("id")
                    props = ultimo_sismo.get("properties", {})
                    
                    mag = props.get("mag")
                    lugar = props.get("place", "Ubicacion no especificada")
                    tiempo_ms = props.get("time", 0)

                    # Verificar si el sismo ocurrió hace menos de 5 minutos
                    tiempo_actual_ms = int(time.time() * 1000)
                    es_reciente = (tiempo_actual_ms - tiempo_ms) < (5 * 60 * 1000)

                    if mag is not None and mag >= MAGNITUD_MINIMA and es_reciente:
                        if sismo_id != ULTIMO_ID_PROCESADO:
                            ULTIMO_ID_PROCESADO = sismo_id
                            print(f"\n[ALERTA SISMO DETECTADA] M{mag} - {lugar}")
                            
                            # 1. Disparar alarma en Firebase
                            actualizar_firebase(True, f"M{mag} - {lugar}", 35)

                            # 2. Dejar sonar la alarma durante 45 segundos
                            time.sleep(45)

                            # 3. Regresar automáticamente a estado seguro
                            actualizar_firebase(False, f"Ultimo: M{mag} - {lugar}", 0)

        except Exception as err:
            print(f"[!] Error temporal en ciclo: {err}")

        # Consulta cada 15 segundos
        time.sleep(15)

if __name__ == "__main__":
    vigilar_sismos()

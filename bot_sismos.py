import os
import time
import requests
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

DB_URL = "https://alertasismica-bf17b-default-rtdb.firebaseio.com/alerta.json"
USGS_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
MAG_MIN = 4.5
LAST_ID = None

def update_fb(activa, epicentro="Normal", seg=0):
    body = {"alerta_activa": "true" if activa else "false", "epicentro": epicentro, "segundos_restantes": str(seg)}
    try:
        requests.put(DB_URL, json=body, timeout=10)
    except:
        pass

def loop_sismos():
    global LAST_ID
    while True:
        try:
            res = requests.get(USGS_URL, timeout=10)
            if res.status_code == 200:
                features = res.json().get("features", [])
                if features:
                    first = features[0]
                    sid = first.get("id")
                    props = first.get("properties", {})
                    mag = props.get("mag")
                    place = props.get("place", "Sismo detectado")
                    t_sismo = props.get("time", 0)
                    t_now = int(time.time() * 1000)

                    if mag and mag >= MAG_MIN and (t_now - t_sismo) < 300000:
                        if sid != LAST_ID:
                            LAST_ID = sid
                            update_fb(True, f"M{mag} - {place}", 35)
                            time.sleep(45)
                            update_fb(False, f"Ultimo: M{mag} - {place}", 0)
        except:
            pass
        time.sleep(15)

class Server(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

if __name__ == "__main__":
    t = threading.Thread(target=loop_sismos, daemon=True)
    t.start()
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), Server).serve_forever()
    mag = props.get("mag")
                    lugar = props.get("place", "Ubicacion no especificada")
                    tiempo_ms = props.get("time", 0)

                    tiempo_actual_ms = int(time.time() * 1000)
                    es_reciente = (tiempo_actual_ms - tiempo_ms) < (5 * 60 * 1000)

                    if mag is not None and mag >= MAGNITUD_MINIMA and es_reciente:
                        if sismo_id != ULTIMO_ID_PROCESADO:
                            ULTIMO_ID_PROCESADO = sismo_id
                            print(f"[ALERTA SISMO] M{mag} - {lugar}", flush=True)
                            actualizar_firebase(True, f"M{mag} - {lugar}", 35)
                            time.sleep(45)
                            actualizar_firebase(False, f"Ultimo: M{mag} - {lugar}", 0)
        except Exception as err:
            print(f"[!] Error ciclo: {err}", flush=True)

        time.sleep(15)

class WebHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK - Monitor Sismico Activo")

def iniciar_servidor():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), WebHandler)
    server.serve_forever()

if __name__ == "__main__":
    t = threading.Thread(target=vigilar_sismos)
    t.daemon = True
    t.start()
    iniciar_servidor()
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

# Author: @Phongoderso
from flask import Flask, jsonify, Response
from threading import Thread, Condition
from werkzeug.serving import WSGIRequestHandler
import logging
import socket
import sys
import time
import cv2

app = Flask(__name__)

# --- Kamera-Einstellungen ---
CAM_WIDTH, CAM_HEIGHT, CAM_FPS = 640, 480, 30   # kleiner = weniger Verzögerung
JPEG_QUALITY = 70                                # 60 bis 80 ist meist ein guter Kompromiss


class Camera:
    """
    Liest eine Kamera in einem eigenen Thread und hält immer nur das neueste Bild bereit.

    Gegenüber dem alten Code:
    - Kein Rückstau: Veraltete Kamerabilder werden verworfen, statt in einer Warteschlange zu altern.
    - Jedes Bild wird nur einmal kodiert, egal wie viele Zuschauer es gibt.
    - Solange niemand zuschaut, wird nichts dekodiert oder kodiert (spart CPU und Strom).
    - Hängt die Kamera, wird sie automatisch neu geöffnet.
    """

    def __init__(self, index, name):
        self.index, self.name = index, name
        self.jpg = None          # neuestes Bild als JPEG
        self.seq = 0             # Zähler, wird mit jedem neuen Bild größer
        self.viewers = 0         # Anzahl aktiver Zuschauer
        self.cond = Condition()
        Thread(target=self._run, daemon=True).start()

    def _open(self):
        backend = cv2.CAP_V4L2 if sys.platform.startswith('linux') else cv2.CAP_ANY
        cap = cv2.VideoCapture(self.index, backend)
        # MJPG: Die Kamera komprimiert selbst. Das spart USB-Bandbreite, besonders bei zwei Kameras.
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
        cap.set(cv2.CAP_PROP_FPS, CAM_FPS)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)       # nur das neueste Bild puffern
        return cap

    def _run(self):
        cap, fails = self._open(), 0
        while True:
            if not cap.grab():                    # wartet auf das nächste Kamerabild
                fails += 1
                if fails >= 30:                   # Kamera hängt: neu öffnen
                    logging.warning(f'Kamera {self.name}: öffne neu')
                    cap.release()
                    time.sleep(1)
                    cap, fails = self._open(), 0
                else:
                    time.sleep(0.05)
                continue
            fails = 0
            if self.viewers == 0:                 # niemand schaut: Bild nur verwerfen
                continue
            ok, frame = cap.retrieve()
            if not ok:
                continue
            ok, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
            if ok:
                with self.cond:
                    self.jpg = buf.tobytes()
                    self.seq += 1
                    self.cond.notify_all()

    def frames(self):
        """Stream für einen Zuschauer. Ein langsamer Zuschauer überspringt Bilder, statt zu verzögern."""
        with self.cond:
            self.viewers += 1
            seq = self.seq                        # alte Bilder nicht mehr ausliefern
        try:
            while True:
                with self.cond:
                    if not self.cond.wait_for(lambda: self.seq != seq, timeout=5):
                        continue                  # kein neues Bild: Verbindung offen halten
                    seq, jpg = self.seq, self.jpg
                yield (b'--frame\r\nContent-Type: image/jpeg\r\nContent-Length: %d\r\n\r\n' % len(jpg)
                       + jpg + b'\r\n')
        finally:
            with self.cond:
                self.viewers -= 1


class StreamingRequestHandler(WSGIRequestHandler):
    """Verhindert Verzögerungen auf TCP-Ebene beim Streamen."""

    def setup(self):
        super().setup()
        # Kleine Datenpakete sofort senden (kein Nagle-Algorithmus).
        self.request.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        # Kleiner Sendepuffer: Bei langsamem WLAN stauen sich nicht mehrere alte Bilder an.
        self.request.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 131072)


cameraFront = Camera(0, 'front')
cameraBack = Camera(1, 'back')


def stream(camera):
    return Response(camera.frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame',
                    headers={'Cache-Control': 'no-store', 'X-Accel-Buffering': 'no'})


@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# Aktuelle Sensordaten, die dein Hauptprogramm aktualisieren kann
sensor_data = {
    'voltage': 0.0,
    'ampere': 0.0,
    'speed': 0.0,
    'distance_front': 0.0,
    'distance_back': 0.0,
    'steering': 0.0,
    'connected': False,
}

@app.route('/camera/front_feed')
def front_feed():
    return stream(cameraFront)

@app.route('/camera/back_feed')
def back_feed():
    return stream(cameraBack)

@app.route('/sensors/batt/voltage', methods=['GET'])
def get_battery_voltage():
    """Gibt die aktuelle Batterie-Spannung zurück."""
    return jsonify({
        'voltage': sensor_data['voltage'],
        'battery': sensor_data['voltage'],
    })

@app.route('/sensors/batt/ampere', methods=['GET'])
def get_battery_ampere():
    """Gibt die aktuelle Batterie-Stromstärke zurück."""
    return jsonify({'ampere': sensor_data['ampere']})

@app.route('/sensors', methods=['GET'])
def get_sensors():
    """Gibt alle Sensordaten zurück."""
    return jsonify(sensor_data)

@app.route('/sensors/speed', methods=['GET'])
def get_speed():
    """Gibt die aktuelle Geschwindigkeit zurück."""
    return jsonify({'speed': sensor_data['speed']})

@app.route('/sensors/distance', methods=['GET'])
def get_distance():
    """Gibt die aktuellen Entfernungswerte zurück."""
    return jsonify({
        'distance_front': sensor_data['distance_front'],
        'distance_back': sensor_data['distance_back'],
    })

@app.route('/sensors/steering', methods=['GET'])
def get_steering():
    """Gibt den aktuellen Lenkungswert zurück."""
    return jsonify({'steering': sensor_data['steering']})

@app.route('/sensors/status', methods=['GET'])
def get_status():
    """Gibt den Verbindungsstatus zurück."""
    return jsonify({'connected': sensor_data['connected']})


def start_web_server(port=5000, debug=False):
    def run():
        logging.info(f'Starte Web-Server auf Port {port}')
        app.run(host='0.0.0.0', port=port, debug=debug, use_reloader=False,
                threaded=True, request_handler=StreamingRequestHandler)

    thread = Thread(target=run, daemon=True)
    thread.start()
    return thread


def update_sensor_data(adc, tof, gps=None):
    """
    Aktualisiert die globalen Sensordaten mit Werten aus deinen Sensorobjekten.
    """
    try:
        sensor_data['voltage'] = adc.get_12voltage(1)
        sensor_data['ampere'] = adc.get_ampere(0)
        sensor_data['distance_front'] = tof.get_mm_vorne()
        sensor_data['distance_back'] = tof.get_mm_hinten()
        sensor_data['steering'] = adc.get_lenkung(2)
        sensor_data['connected'] = True
    except Exception as e:
        logging.error(f'Fehler beim Aktualisieren der Sensordaten: {e}')
        sensor_data['connected'] = False


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start_web_server(port=5000)
    print('Web-Server läuft auf http://localhost:5000')
    input('Drücke Enter zum Beenden...')
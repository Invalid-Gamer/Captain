from flask import Flask, jsonify, Response
from threading import Thread
import logging
import cv2

app = Flask(__name__)
camera = cv2.VideoCapture(0)

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Aktuelle Sensordaten, die dein Hauptprogramm aktualisieren kann
sensor_data = {
    'battery': 0.0,
    'ampere': 0.0,
    'speed': 0.0,
    'distance_front': 0.0,
    'distance_back': 0.0,
    'steering': 0.0,
    'connected': False,
}

@app.route('/camera/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/sensors/batt/voltage', methods=['GET'])
def get_battery_voltage():
    """Gibt die aktuelle Batterie-Spannung zurück."""
    return jsonify({'battery': sensor_data['battery']})

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
        app.run(host='0.0.0.0', port=port, debug=debug, use_reloader=False)

    thread = Thread(target=run, daemon=True)
    thread.start()
    return thread


def update_sensor_data(adc, tof, gps=None):
    """
    Aktualisiert die globalen Sensordaten mit Werten aus deinen Sensorobjekten.
    """
    try:
        sensor_data['battery'] = adc.get_12voltage(1)
        sensor_data['ampere'] = adc.get_ampere(0)
        sensor_data['distance_front'] = tof.get_mm_vorne()
        sensor_data['distance_back'] = tof.get_mm_hinten()
        sensor_data['steering'] = adc.get_lenkung(2)
        sensor_data['connected'] = True
    except Exception as e:
        logging.error(f'Fehler beim Aktualisieren der Sensordaten: {e}')
        sensor_data['connected'] = False


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    start_web_server(port=5000)
    print('Web-Server läuft auf http://localhost:5000')
    input('Drücke Enter zum Beenden...')
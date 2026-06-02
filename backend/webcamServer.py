import cv2
import logging
import threading
from flask import Flask, Response

from comps.sensors.ADC import ADC
from comps.sensors.TOF import TOF

port = 5000
app = Flask(__name__)
camera = cv2.VideoCapture(0) # Schnappt sich den nächstbesten Kamera Feed
adc_instance:ADC
tof_instance:TOF

def generate_frames(): # Kamera frames verarbeiten und in jpg wiedergeben
    while True:
        success, frame = camera.read()

        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/') # Standard-Hässliches Interface
def index():
    return '<h1>Kamera Stream</h1><img src="/video_feed" width="640">'

@app.route('/video_feed') # Rohfeed
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def webcamServer(adc,tof):
    global adc_instance
    global tof_instance
    adc_instance = adc
    tof_instance = tof
    t = threading.current_thread()
    logging.info(f"Webcam Server running on Port: {port}")
    if getattr(t, "do_run", True):
        app.run(host='0.0.0.0', port=port)
@app.route('/sensors/lenkung')
def lenkug():
    return str(adc_instance.get_lenkung(2))
@app.route('/sensors/batt/voltage')
def voltage():
    return str(adc_instance.get_12voltage(1))
@app.route('/sensors/batt/ampere')
def ampere():
    return str(adc_instance.get_ampere(0))
@app.route('/sensors/tof/vorne')
def vorne():
    return str(tof_instance.get_mm_vorne())
@app.route('/sensors/tof/hinten')
def hinten():
    return str(tof_instance.get_mm_hinten())
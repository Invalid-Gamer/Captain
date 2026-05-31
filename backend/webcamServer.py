import cv2
import logging
import threading
from flask import Flask, Response

port = 5000
app = Flask(__name__)
camera = cv2.VideoCapture(0) # Schnappt sich den nächstbesten Kamera Feed

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
def webcamServer():
    t = threading.current_thread()
    logging.info(f"Webcam Server running on Port: {port}")
    if getattr(t, "do_run", True):
        app.run(host='0.0.0.0', port=port)

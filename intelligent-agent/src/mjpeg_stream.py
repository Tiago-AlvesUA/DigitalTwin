from flask import Flask, Response, request
import queue
import time
import threading

app = Flask(__name__)

frame_queue = queue.Queue(maxsize=10)

@app.route('/', methods=['POST'])
def upload_frame():
    if request.method == 'POST':
        try:
            frame_queue.put(request.data, block=False) 
        except queue.Full:
            pass
        return 'OK', 200
    return 'Use POST requests', 400
   

def generate_mjpeg():
    while True:
        try:
            frame = frame_queue.get(timeout=1)  # Wait for a frame to be available
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except queue.Empty:
            continue
            
# NOTE: This script is done to only serve one client at a time. Because the queue is used to store frames, if multiple clients try to access the stream, there will be lost frames.
@app.route('/video_feed')
def video_feed():
    return Response(generate_mjpeg(),
                mimetype='multipart/x-mixed-replace; boundary=frame')


app.run(host="0.0.0.0", port=5000)
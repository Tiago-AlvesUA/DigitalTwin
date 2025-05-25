from flask import Flask, Response
#import cv2
import os
import time

app = Flask(__name__)

def generate_frames():
    # TODO: Comment
    seen_frames = set()  # Set to keep track of seen frames

    while True:
        frame_files = sorted(os.listdir("simulation_frames"))
        
        for file in frame_files:
            # TODO: Comment
            if file in seen_frames:
                continue

            file_path = os.path.join("simulation_frames", file)
            with open(file_path, 'rb') as f:
                frame = f.read()    # Reads each image in binary mode, to get raw bytes
            # yield a multipart frame
            
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
            # TODO: Comment
            seen_frames.add(file)

            # os.remove(file_path)  # Remove the file after sending it

            time.sleep(1)

        time.sleep(0.2) # Sleep to avoid busy waiting

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

app.run(host="0.0.0.0", port=5000)

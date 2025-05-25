from flask import Flask, Response, request
import time
import threading
import queue

app = Flask(__name__)

latest_frame = None

frame_queue = queue.Queue(maxsize=10) 

@app.route('/', methods=['POST'])
def upload_frame():
    global latest_frame
    if request.method == 'POST':
        try:
            frame_queue.put(request.data, block=False) 
        except queue.Full:
            pass
        return 'OK', 200
    return 'Use POST requests', 400
   

def generate_mjpeg():
    global latest_frame
    while True:
        try:
            frame = frame_queue.get(timeout=1)  # Wait for a frame to be available
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except queue.Empty:
            continue
            

@app.route('/video_feed')
def video_feed():
    return Response(generate_mjpeg(),
                mimetype='multipart/x-mixed-replace; boundary=frame')


app.run(host="0.0.0.0", port=5000)


# # fastapi_mjpeg_ws_server.py
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# from fastapi.responses import StreamingResponse
# from queue import Queue
# import asyncio
# import time

# app = FastAPI()
# frame_queue = Queue(maxsize=10)

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     try:
#         while True:
#             data = await websocket.receive_bytes()
#             if frame_queue.full():
#                 frame_queue.get()
#             frame_queue.put(data)
#     except WebSocketDisconnect:
#         print("WebSocket client disconnected")

# def mjpeg_streamer():
#     while True:
#         if not frame_queue.empty():
#             frame = frame_queue.get()
#             yield (b"--frame\r\n"
#                    b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
#         else:
#             time.sleep(0.5)

# @app.get("/video_feed")
# def video_feed():
#     return StreamingResponse(mjpeg_streamer(), media_type="multipart/x-mixed-replace; boundary=frame")

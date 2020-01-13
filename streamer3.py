"""
https://github.com/oitsjustjose/Flask-OpenCV-Streamer
"""

"""Stores a Streamer class"""
import time
from threading import Thread

import cv2
from flask import Flask, Response, render_template, request
from flask_socketio import SocketIO

app = Flask(__name__)
socketio=SocketIO(app)
port = 8887
frame_rate = 30
server="http://rpi-6.wifi.local.cmu.edu:8888/video_feed"
VCap=cv2.VideoCapture(server)
if not VCap.isOpened():
    print("ERROR! Check the camera.")
    exit(0)

@app.route("/video_feed")
def video_feed():
    """Route which renders solely the video"""
    return Response(
        gen(), mimetype="multipart/x-mixed-replace; boundary=jpgboundary"
    )

def get_frame(frame):
    """Encodes the OpenCV image"""
    _, jpeg = cv2.imencode(
        ".jpg",
        frame,
        params=(cv2.IMWRITE_JPEG_QUALITY, 70),
    )
    return jpeg.tobytes()

def gen():
    """A generator for the image."""
    header = "--jpgboundary\r\nContent-Type: image/jpeg\r\n"
    prefix = ""
    while True:
        ret, frame =VCap.read()
        stream=get_frame(frame)
        msg = (
            prefix
            + header
            + "Content-Length: {}\r\n\r\n".format(len(stream))
        )

        yield (msg.encode("utf-8") + stream)
        prefix = "\r\n"
        time.sleep(1 / (10*frame_rate))


#thread = Thread(
#    daemon=True,
#    target=app.run,
#    kwargs={
#        "host": "0.0.0.0",
#        "port": port,
#        "debug": False,
#        "threaded": True,
#    },
#)
#thread.start()
#is_streaming = True

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
    #app.run(host='0.0.0.0', port=port, debug=True)

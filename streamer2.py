"""
https://github.com/oitsjustjose/Flask-OpenCV-Streamer
"""

"""Stores a Streamer class"""
import time
from threading import Thread

import cv2
from flask import Flask, Response, render_template, request
from flask_socketio import SocketIO

import socket 
from sys import argv

app = Flask(__name__)
socketio=SocketIO(app)
is_streaming = False
port = 8888
frame_rate = 30
server="http://rpi-6.wifi.local.cmu.edu:8888/video_feed"
#server="http://mellon.andrew.cmu.edu:8887/video_feed"
VCap=cv2.VideoCapture(server)
if not VCap.isOpened():
    print("ERROR! Check the camera.")
    exit(0)
host_name = "rpi-6.wifi.local.cmu.edu"
host_port = 7777
if len(argv)>1:
    host_port=int(argv[1])
try:
    host_ip = socket.gethostbyname(host_name)
except:
    print("no host!")
    exit(0)

@app.route("/video_feed")
def video_feed():
    """Route which renders solely the video"""
    thread = Thread(daemon=True, target=gen)
    return Response(
        gen(), mimetype="multipart/x-mixed-replace; boundary=jpgboundary"
       #thread.start(), mimetype="multipart/x-mixed-replace; boundary=jpgboundary"
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

@app.route("/")
def index():
    """Route which renders the video within an HTML template"""
    return render_template("index.html")

@socketio.on('connect')
def on_connect():
    print('browser is connected!')

@socketio.on('button')
def on_button(data):
    print(data)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host_ip, host_port))
    s.send(data.encode('ascii'))
    s.close()
    

#self.thread = Thread(
#    daemon=True,
#    target=self.flask.run,
#    kwargs={
#        "host": "0.0.0.0",
#        "port": self.port,
#        "debug": False,
#        "threaded": True,
#    },
#)
#self.thread.start()
#self.is_streaming = True


#thread = Thread(
#    daemon=True,
#    target=socketio.run,
#    kwargs={
#        "app": app,
#        "host": "0.0.0.0",
#        "port": 8888,
#        "debug": True,
#        "threaded": True,
#    },
#)
#self.is_streaming = True

if __name__=='__main__':
#    thread.start()
#    is_streaming=True
    socketio.run(app,host="0.0.0.0", port=8888, debug=True)

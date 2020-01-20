import time
import cv2
import socket

from threading import Thread
from flask import Flask, Response, request
from flask_socketio import SocketIO
from sys import argv


app = Flask(__name__)
socketio = SocketIO(app)

is_streaming = False
port = 8888
frame_rate = 30
server = "http://rpi-6.wifi.local.cmu.edu:8888/video_feed"
#server="http://mellon.andrew.cmu.edu:8887/video_feed"
VCap=cv2.VideoCapture(server)
host_name = "rpi-6.wifi.local.cmu.edu"
host_port = 7777
if len(argv) > 1:
    host_port = int(argv[1])
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
        gen(), mimetype = "multipart/x-mixed-replace; boundary=jpgboundary"
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
        ret, frame = VCap.read()
        stream = get_frame(frame)
        msg = (
            prefix
            + header
            + "Content-Length: {}\r\n\r\n".format(len(stream))
        )

        yield (msg.encode("utf-8") + stream)
        prefix = "\r\n"
        time.sleep(1 / (10*frame_rate))


@socketio.on('connect')
def on_connect():
    print('Browser is connected!')

@socketio.on('button')
def on_button(data):
    print(data)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host_ip, host_port))
    s.send(data.encode('ascii'))
    s.close()


from app.modules import index, loading, unloading, maintenance

app.register_blueprint(index.bp)
app.register_blueprint(loading.bp)
app.register_blueprint(unloading.bp)
app.register_blueprint(maintenance.bp)


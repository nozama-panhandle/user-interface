import time
import cv2
import socket
import pymysql

from threading import Thread
from flask import Flask, Response, request
from flask_socketio import SocketIO
from sys import argv


app = Flask(__name__)
socketio = SocketIO(app)

is_streaming = False
port = 8888
frame_rate = 30
host_name = "rpi-6.wifi.local.cmu.edu"
host_port = 7777
db=pymysql.connect(host='localhost',
                   user='strong',
                   password='strong',
                   db='orderdb')
cursor = db.cursor(pymysql.cursors.DictCursor)

if len(argv) > 1:
    host_port = int(argv[1])
try:
    host_ip = socket.gethostbyname(host_name)
except:
    print("no host!")
    exit(0)

@socketio.on('connect')
def on_connect():
    print('Browser is connected!')

@socketio.on('keypress')
def on_keypress(data):
    print(data)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(host_ip, host_port)
    s.connect((host_ip, host_port))
    s.send(data.encode('ascii'))
    s.close()

@socketio.on('button')
def on_button(data):
    print(data)
    com, id_ = data.split()
#0: completed
#1: pending
#2: shipping
#3: scheduled
    if com =="reset":
        self.cursor.execute("UPDATE orders SET pending='1' WHERE pending='2'")
    elif com == "complete":
        self.cursor.execute("UPDATE orders SET pending='2' WHERE pending='3'")
    elif com == "clear":
        self.cursor.execute("UPDATE orders SET pending='0' WHERE id='%s'"%id_)
    elif com == "schedule":
        self.cursor.execute("UPDATE orders SET pending='1' WHERE pending='3'")
        pend_list = self.cursor.execute("SELECT pending='1' FROM orders")
        
        self.cursor.execute("UPDATE orders SET pending='3' WHERE id='%s'"% pend_list[0]['id'])

        
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(host_ip, host_port)
    s.connect((host_ip, host_port))
    s.send(data.encode('ascii'))
    s.close()

from app.modules import index, loading, unloading, maintenance

app.register_blueprint(index.bp)
app.register_blueprint(loading.bp)
app.register_blueprint(unloading.bp)
app.register_blueprint(maintenance.bp)


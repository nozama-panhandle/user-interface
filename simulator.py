import time
import socketio

unloading_t=5
unloading_per=1.1
loading_t=10
loading_per=1.1

sio = socketio.Client()
sio.connect('http://mellon.andrew.cmu.edu:9999', namespaces=['/loading','/unloading'])

c_orders=None
inven=None

#@sio.event
#def connect():


@sio.on('inventory',namespace='/loading')
def on_inven(data):
    inven=data
    print(inven)


@sio.on('refresh', namespace='/loading')
def on_refresh(data):
    c_orders=data
    print(c_orders)

@sio.on('arrived', namespace='/loading')
def on_arrived_load(data):


@sio.on('arrived', namespace='/unloading')
def on_arrived_load(data):



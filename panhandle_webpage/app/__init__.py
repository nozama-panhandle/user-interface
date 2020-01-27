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
    com, address = data.split()
#0: completed
#1: pending
#2: shipping
#3: scheduled
    if com =="reset":
        cursor.execute("UPDATE orders SET pending='1' WHERE pending='2'")
        db.commit()
    elif com == "complete":
        cursor.execute("UPDATE orders SET pending='2' WHERE pending='3'")
        db.commit()

        ##next address
        #cursor.execute("SELECT address, red, blue, green FROM orders WHERE pending='2' ORDER BY delivery_order")
        cursor.execute("SELECT address, red, blue, green FROM orders WHERE pending='2'")

        c_orders = cursor.fetchall()
        print("c_orders : ",c_orders)
        if len(c_orders)==0:
            next_address = 0
        else:
            next_address = c_orders[0]['address']
        ###inventory
        #cursor.execute("SELECT red, blue, green, pending=2 FROM orderdb.orders")
        #c_orders = cursor.fetchall()

        current_orders = c_orders
        current_orders_r = 0
        current_orders_g = 0
        current_orders_b = 0

        for i in range(len(current_orders)):
            current_orders_r += current_orders[i]['red']
            current_orders_g += current_orders[i]['green']
            current_orders_b += current_orders[i]['blue']

        cursor.execute("SELECT red, blue, green FROM inventory")
        inventory = cursor.fetchall()

        inventory_r = inventory[0]['red']
        inventory_g = inventory[0]['green']
        inventory_b = inventory[0]['blue']

        inventory_r -= current_orders_r
        inventory_g -= current_orders_g
        inventory_b -= current_orders_b

        update_inventory_r = "UPDATE inventory SET red='%d' " % (inventory_r)
        cursor.execute(update_inventory_r)
        db.commit()
        update_inventory_g = "UPDATE inventory SET green='%d'" % (inventory_g)
        cursor.execute(update_inventory_g)
        db.commit()
        update_inventory_b = "UPDATE inventory SET blue='%d'" % (inventory_b)
        cursor.execute(update_inventory_b)
        db.commit()

        #print(current_orders_r)
        #print(inventory)
        ###complete
        #cursor.execute("UPDATE orders SET pending='2' WHERE pending='3'")
        #db.commit()

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host_ip, host_port))
        s.send((com+' '+str(next_address)).encode('ascii'))
        s.close()
    elif com == "clear":
        cursor.execute("UPDATE orders SET pending='0' WHERE pending='2' and address='%s'"%address)
        db.commit()
        ###next scheduled number
        cursor.execute("SELECT address FROM orders WHERE pending='2' order by delivery_order")
        next_address=cursor.fetchall()

       
        if len(next_address)==0:
            next_address=0
        else:
            next_address = next_address[0]['address']
        #if address ==next_address:
        #    print("more package to unload")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host_ip, host_port))
        s.send((com+' '+str(next_address)).encode('ascii'))
        s.close()
    elif com == "schedule":
        cursor.execute("UPDATE orders SET pending='1' WHERE pending='3'")
        db.commit()
        cursor.execute("SELECT id FROM orders WHERE pending='1'")
        pend_list=cursor.fetchall()
        print(pend_list)
        cursor.execute("UPDATE orders SET pending='3', delivery_order='0' WHERE id='%s'"% pend_list[0]['id'])
        db.commit()
    elif com =="replenish":
        ####inventory replenishment
        init_r, init_g, init_b = 26, 26, 26
        shipping_r, shipping_g, shipping_b = 0,0,0
        cursor.execute("SELECT red, blue, green FROM orders where pending='2'")
        shipping=cursor.fetchall()

        for i in range(len(shipping)):
            shipping_r += shipping[i]['red']
            shipping_g += shipping[i]['green']
            shipping_b += shipping[i]['blue']
        shipping_r = init_r - shipping_r
        shipping_g = init_g - shipping_g
        shipping_b = init_b - shipping_b

        cursor.execute("UPDATE inventory  SET red='%s'" % (shipping_r))
        db.commit()
        cursor.execute("UPDATE inventory  SET green='%s'" % (shipping_g))
        db.commit()
        cursor.execute("UPDATE inventory  SET blue='%s'" % (shipping_b))
        db.commit()

#from app.modules import buttonio

        

from app.modules import index, loading, unloading, maintenance

app.register_blueprint(index.bp)
app.register_blueprint(loading.bp)
app.register_blueprint(unloading.bp)
app.register_blueprint(maintenance.bp)


import time
import cv2
import socket
import pymysql
import random
import string


port = 8888
frame_rate = 30
host_name = "rpi-6.wifi.local.cmu.edu"
host_port = 7777
db=pymysql.connect(host='localhost',
                   user='strong',
                   password='strong',
                   db='orderdb')
cursor = db.cursor(pymysql.cursors.DictCursor)


def empty_orders():
    cursor.execute("DELETE FROM orders")
    db.commit()

empty_orders()
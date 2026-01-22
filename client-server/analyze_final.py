import time
import pymysql
from datetime import datetime, timedelta
import pdb
import sys

from tensorboardX import SummaryWriter
host_name = "rpi-6.wifi.local.cmu.edu"
host_port = 7777


db = pymysql.connect(host='localhost',
                     user='strong',
                     password='strong',
                     db='orderdb')
cursor = db.cursor(pymysql.cursors.DictCursor)
cursor.execute("SELECT * FROM orders")
orders = cursor.fetchall()
total = len(orders)
# c_t1,c_t2,c_t3,c_t4=15,25,30,40
c1,c2,c3,c4=0,0,0,0
# for order in orders:
#     t1 = order['orderdate']
#     t2 = order['filldate']
#     during = time.mktime(t2.timetuple())-time.mktime(t1.timetuple())
#     if during<60*c_t1:
#         c1+=1
#     if during<60*c_t2:
#         c2+=1
#     if during < 60*c_t3:
#         c3+= 1
#     if during < 60*c_t4:
#         c4 += 1
# print("In 15 min: %d "%((c1/total)*100))
# print("In 25 min: %d "%((c2/total)*100))
# print("In 30 min: %d "%((c3/total)*100))
# print("In 40 min: %d "%((c4/total)*100))
c5,c6=0,0
for order in orders:
    address = order['address']
    if address==101:
        c1+=1
    if address==102:
        c2+=1
    if address==103:
        c3+= 1
    if address==201:
        c4 += 1
    if address==202:
        c5 += 1
    if address == 203:
        c6 += 1
print("In 15 101: %d,%d,%d,%d,%d,%d "%((c1/total)*100,(c2/total)*100,(c3/total)*100,(c4/total)*100,(c5/total)*100,(c6/total)*100))

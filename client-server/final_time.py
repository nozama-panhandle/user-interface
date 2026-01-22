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

start_time = orders[0]['orderdate']
final_time = orders[0]['orderdate']
for order in orders:
    t2= order['filldate']
    if t2>final_time:
        final_time=t2
during = time.mktime(final_time.timetuple())-time.mktime(start_time.timetuple())
print("Total Delivery Time: %d min %d sec"%(during//60, during%60))

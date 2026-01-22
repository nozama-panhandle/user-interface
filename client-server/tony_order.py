import pymysql
from datetime import datetime, timedelta
import time
import pdb
host_name = "rpi-6.wifi.local.cmu.edu"
host_port = 7777
db = pymysql.connect(host='localhost',
                     user='strong',
                     password='strong',
                     db='orderdb')
cursor = db.cursor(pymysql.cursors.DictCursor)
cursor.execute("SELECT * FROM dryrun_orders")
tonyorders = cursor.fetchall()


for i, tony in enumerate(tonyorders):
    db = pymysql.connect(host='localhost',
                         user='strong',
                         password='strong',
                         db='orderdb')
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM dryrun_orders")
    tonyorders = cursor.fetchall()

    t1 = tony['orderdate']
    t2 = tonyorders[i+1]['orderdate']

    wait = time.mktime(t2.timetuple()) - time.mktime(t1.timetuple())
    cursor.execute(
        "INSERT into orders(id,customer,address,red,green,blue,pending) VALUES ('%d','%s','%d','%d','%d','%d','1')" \
        % (tony['id'], tony['customer'], tony['address'], tony['red'], tony['green'], tony['blue']))
    db.commit()
    print(tony)
    time.sleep(wait)
import time
import pymysql
from datetime import datetime, timedelta
import pdb

from tensorboardX import SummaryWriter
host_name = "rpi-6.wifi.local.cmu.edu"
host_port = 7777
db=pymysql.connect(host='localhost',
                   user='strong',
                   password='strong',
                   db='orderdb')
cursor = db.cursor(pymysql.cursors.DictCursor)


def track_inventory():
    cursor.execute("DELETE FROM orders")
    db.commit()

writer = SummaryWriter('log/')
interval=5
pastorders=[]
wait_t = 0
wait_tot = 0
wait_av = 0
wait_max = 0
throughput_tot=0
while(1):
    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()
    backlog_ = 0
    throughput_ = 0
    for order in orders:
        if order['pending']!=1:
            backlog_+=1
        if order['pending']==0 and order['address']==101 and order not in pastorders:
            throughput_+=1
            t1 = order['orderdate']
            t2 = order['filldate']
            if type(t2)==str:
                print('Filldate string error!')
                wait_=0
            else:
                wait_ =  time.mktime(t2.timetuple())- time.mktime(t1.timetuple())
            wait_t+=wait_
            if wait_max<wait_:
                wait_max=wait_
    wait_tot +=wait_t
    throughput_tot += throughput_
    if throughput_!=0:
        wait_av = wait_tot/throughput_

    print("Time : ", datetime.now(),", Throughput: %d, Backlog : %d, Ave Wait time :  %d min %.2f sec, Max Wait time: %d min %.2f sec" \
          %(throughput_,backlog_, wait_av//60, wait_av%60,wait_max//60,wait_max%60))
    pastorders=orders
    time.sleep(interval)
    # tf_loss_summary = tf.summary.scalar('throughput', throughput_)
    writer.add_scalar('throughput',throughput_)
    writer.add_scalar('backlog',backlog_)
    writer.add_scalar('average wait time',wait_av)
    writer.add_scalar('maximum wait time',wait_max)
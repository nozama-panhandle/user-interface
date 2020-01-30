import time
import pymysql
from datetime import datetime, timedelta
import pdb
import sys

from tensorboardX import SummaryWriter
host_name = "rpi-6.wifi.local.cmu.edu"
host_port = 7777
db=pymysql.connect(host='localhost',
                   user='strong',
                   password='strong',
                   db='orderdb')
cursor = db.cursor(pymysql.cursors.DictCursor)


writer = SummaryWriter('./log/Alg1')
writer_inv = SummaryWriter('log_inventory/Alg1')
interval=1
pastorders=[]
wait_t = 0
wait_tot = 0
wait_av = 0
wait_max = 0
throughput_tot=0
step = 0
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

    print(datetime.now(),", Throughput: %d, Backlog : %d, Ave Wait time :  %d min %.2f sec, Max Wait time: %d min %.2f sec" \
          %(throughput_,backlog_, wait_av//60, wait_av%60,wait_max//60,wait_max%60))
    pastorders=orders
    writer.add_scalar('throughput',throughput_,step)
    writer.add_scalar('backlog',backlog_,step)
    writer.add_scalar('average wait time',wait_av,step)
    writer.add_scalar('maximum wait time',wait_max,step)


    ###inventory
    cursor.execute("SELECT * FROM inventory")
    invs = cursor.fetchall()

    inv = invs[0]
    red_ = inv['red']
    green_ = inv['green']
    blue_ = inv['blue']

    writer_inv.add_scalar('red', red_, step)
    writer_inv.add_scalar('green', green_, step)
    writer_inv.add_scalar('blue', blue_, step)
    print(datetime.now(), " Red: %d, Green : %d, Blue :  %d " % (red_, green_, blue_))

    writer.close()
    writer_inv.close()
    time.sleep(interval)
    step=step+1
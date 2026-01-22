import time
import pymysql
from datetime import datetime, timedelta
import pdb
import sys

from tensorboardX import SummaryWriter
host_name = "rpi-6.wifi.local.cmu.edu"
host_port = 7777



writer = SummaryWriter('./log/Final') #writer_inv = SummaryWriter('log_inventory/Alg1')
interval=10
pastorders=[]
wait_t = 0
wait_tot = 0
wait_av = 0
wait_max = 0
throughput_tot=0
step = 0
throughput_ = 0
while(1):
    db = pymysql.connect(host='localhost',
                         user='strong',
                         password='strong',
                         db='orderdb')
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()
    wait_tot=0
    backlog_ = 0
    for order in orders:
        if order['pending']!=0:
            backlog_+=1
        if order['pending']==0 and order not in pastorders:
            throughput_+=1
            pastorders.append(order)

        t1 = order['orderdate']
        t2 = order['filldate']
        if type(t2)==str:
            t2=datetime.now()
            wait_= time.mktime(t2.timetuple())- time.mktime(t1.timetuple())
        else:
            wait_ =  time.mktime(t2.timetuple())- time.mktime(t1.timetuple())
        wait_tot+=wait_
        if wait_max<wait_:
            wait_max=wait_

    if len(orders) != 0:
        wait_av = wait_tot / len(orders)

    if step %500== 0 and len(orders)!=0:
        writer.add_scalar('throughput', throughput_, step)
        throughput_tot += throughput_
        throughput_ = 0
        print("#######################################   %d "%step)
        start_time =orders[0]['orderdate']
        t2= datetime.now()
        during = time.mktime(t2.timetuple())-time.mktime(start_time.timetuple())
        print("Total Delivery Time: %d min %d sec"%(during//60, during%60))
        print("Number of Delivered Orders: %d "%(throughput_tot))

    if backlog_==0 and len(orders)>20:
        throughput_tot += throughput_
        throughput_ = 0
        print("=============================================================")
        print("=============              SUMMARY            ===============")
        print("=============================================================")
        start_time =orders[0]['orderdate']
        during = time.mktime(t2.timetuple())-time.mktime(start_time.timetuple())
        print("Total Delivery Time: %d min %d sec"%(during//60, during%60))
        print("Number of Delivered Orders: %d "%(throughput_tot))

    writer.add_scalar('Backlog',backlog_,step)
    writer.add_scalars('Waiting Time', {'average': wait_av, 'maximum': wait_max}, step)


    ##############inventory
    cursor.execute("SELECT * FROM inventory")
    invs = cursor.fetchall()
    inv = invs[0]
    red_ = inv['red']
    green_ = inv['green']
    blue_ = inv['blue']
    writer.add_scalars('Inventory', {'red': red_, 'green': green_, 'blue': blue_}, step)


    ##############clicklogs
    cursor.execute("SELECT * FROM clicklogs")
    orders = cursor.fetchall()
    if len(orders)>2:
        pastorder = orders[-1]
        firstorder = orders[0]
        for order in orders:
            if order['begin'] == pastorder['begin'] and order['status']=='unload' and pastorder in orders:
                orders.remove(pastorder)
            pastorder = order
        if firstorder in orders:
            orders.remove(firstorder)
        load = []
        unload = []
        for order in orders:
            if order['status'] == 'load':
                load.append(order)

            if order['status'] == 'unload':
                unload.append(order)


        loading_time = 0
        schedule_time = 0
        for order in load:
            t_sch = order['schedule']
            t1 = order['begin']
            t2 = order['end']
            sch_temp = time.mktime(t2.timetuple()) - time.mktime(t_sch.timetuple())
            loading_temp = time.mktime(t2.timetuple()) - time.mktime(t1.timetuple())
            if loading_temp > 0:
                loading_time += loading_temp
            if sch_temp > 0:
                schedule_time += sch_temp

        unloading_time = 0
        for order in unload:
            t1 = order['begin']
            t2 = order['end']
            unloading_temp = time.mktime(t2.timetuple()) - time.mktime(t1.timetuple())
            if unloading_temp > 0:
                unloading_time += unloading_temp
        if len(load)!=0 :
            schedule_time = schedule_time / len(load)
            loading_time = loading_time / len(load)
        else:
            print("len(load)==0")
            print(orders)

        if len(unload) != 0:
            unloading_time = unloading_time / len(unload)
        else:
            print("len(unload)==0")
            print(orders)
        writer.add_scalars('click time',{'schedule time': schedule_time, 'loading time': loading_time, 'unloading time': unloading_time}, step)
        if step %500== 0 and len(orders)!=0:
            print("schedule time", schedule_time, "loading time", loading_time, "unloading time", unloading_time)


    step=step+1
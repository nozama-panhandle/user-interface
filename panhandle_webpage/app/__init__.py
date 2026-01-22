import time
import cv2
import socket
import pymysql
import time
from threading import Thread
from flask import Flask, Response, request, render_template
from flask_socketio import SocketIO
from sys import argv
from datetime import datetime
from datetime import MINYEAR
from app.modules import rgbschedule as schedule
#from app.modules import newschedule as schedule
#from app.modules import schedule as schedule
from collections import Counter


app = Flask(__name__)
socketio = SocketIO(app)


is_streaming = False

db=pymysql.connect(host='localhost',
                   user='strong',
                   password='strong',
                   db='orderdb')

schedule_time=datetime.now()
begin_time=datetime.now()
end_time=datetime.now()

inStop= True
robotConn = False

@socketio.on('connect', namespace='/loading')
def on_connect():
    print('Loading page is connected!')
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT address, red, blue, green FROM scheduling WHERE pending='3'")
    orders = cursor.fetchall()
    ### Sum all number of r,g,b blocks
    c_orders=sum(map(Counter, orders), Counter())
    socketio.emit('refresh', c_orders, namespace='/loading')
    cursor.execute("SELECT red, blue, green FROM inventory")
    inventory = cursor.fetchall()
    socketio.emit('inventory', inventory[0], namespace='/loading')
    cursor.close()


@socketio.on('connect', namespace='/unloading')
def on_connect():
    print('Unloading page is connected!')
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT address, cast(sum(red) as unsigned) red, cast(sum(green) as unsigned) green, cast(sum(blue) as unsigned) blue FROM scheduling WHERE pending='2' group by address order by delivery_order")
    c_orders = cursor.fetchall()
    socketio.emit('refresh', c_orders, namespace='/unloading')
    cursor.close()

maint=0
@socketio.on('connect', namespace='/monitoring')
def on_connect():
    global maint
    print('Monitoring page is connected!')
    socketio.emit('refresh', maint, namespace='/monitoring')

    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT red, blue, green FROM inventory")
    inventory = cursor.fetchall()
    socketio.emit('inventory', inventory[0], namespace='/monitoring')
    
    #cursor.execute("SELECT id FROM orders")
    #whole_orders = cursor.fetchall()
    #cursor.execute("SELECT id FROM orders WHERE pending='0'")
    #completed_orders = cursor.fetchall()
    #progress = (len(completed_orders) / len(whole_orders))
    #socketio.emit('progress', progress, namespace='/monitoring')

    cursor.close()

@socketio.on('disconnect', namespace='/robot')
def on_disconnect():
    print("The robot is disconnected!")
    global robotConn
    robotConn=False

@socketio.on('connect', namespace='/robot')
def on_connect():
    global maint, robotConn
    robotConn=True
    print('The robot is connected!', robotConn)
    socketio.emit('maintenance', maint, namespace='/robot')

@socketio.on('maintenance', namespace='/monitoring')
def on_Maintenance(data):
    global maint, inStop
    print(data)
    if data==0:
        maint=0
        inStop=True
        print("monitoring!")
        socketio.emit('refresh', 0, namespace='/monitoring')
        socketio.emit('maintenance', 0, namespace='/robot')
    else:
        maint=1
        print("maintenance!")
        socketio.emit('refresh', 1, namespace='/monitoring')
        socketio.emit('maintenance', 1, namespace='/robot')

@socketio.on('maintenance', namespace='/robot')
def on_MaintenanceRobot(data):
    global maint
    print(data)
    if data==0:
        maint=0
        print("monitoring!")
        socketio.emit('refresh', 0, namespace='/monitoring')
    else:
        maint=1
        print("maintenance!")
        socketio.emit('refresh', 1, namespace='/monitoring')
'''
@socketio.on('progress', namespace='/monitoring')
def order_progress(data):
    print(data)
    cursor = db.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT id FROM orders")
    whole_orders = cursor.fetchall()

    cursor.execute("SELECT id FROM orders WHERE pending='0'")
    completed_orders = cursor.fetchall()

    progress = (len(completed_orders) / len(whole_orders))
    
    socketio.emit('progress', progress, namespace='/monitoring')
    cursor.close()
'''
@socketio.on('message', namespace='/robot')
def on_message(data):
    global schedule_time, begin_time, end_time
    global inStop
    print(data)
    addr = data.split()[1]
    print(type(addr), " ",addr)
    begin_time=datetime.now()
    inStop = True
    if addr=='0':
        socketio.emit('arrived', data.split()[1],namespace='/loading')
    else:
        socketio.emit('arrived', data.split()[1],namespace='/unloading')

#@socketio.on('connect', namespace='/robot')
#def on_connect_robot():
#    print('Robot is connected!')

@socketio.on('keypress')
def on_keypress(data):
    print(data)
    socketio.emit("message", data, namespace='/robot')


@socketio.on('button', namespace='/unloading')
def on_button(data):
    global schedule_time, begin_time, end_time
    global inStop, robotConn, maint
    print('unloading ',data)
    com, address = data.split()
#0: completed
#1: pending
#2: shipping
#3: scheduled
    cursor = db.cursor(pymysql.cursors.DictCursor)
    if com == "clear":
        print(inStop)
        if maint or not inStop or not robotConn:
            cursor.close()
            return
        inStop=False
        #TODO partial order
        now = datetime.now()

        # cursor.execute("SELECT address, cast(sum(red) as unsigned) red, cast(sum(green) as unsigned) green, cast(sum(blue) as unsigned) blue FROM scheduling WHERE pending='2' AND address='%s'"%(address))
        # orders=cursor.fetchall()
        cursor.execute("SELECT address, red, green, blue, id FROM scheduling WHERE pending='2' AND address='%s'" % (address))
        orders = cursor.fetchall()
        for order in orders:
            cursor.execute("insert into clicklogs(status, red, green, blue, begin, end, orderid) values('unload','%d','%d','%d', '%s','%s','%d')"\
                           %(order['red'], order['green'], order['blue'], begin_time, now, order['id']))
            db.commit()

        cursor.execute("SELECT id, is_last FROM scheduling WHERE pending='2' AND address='%s'" % (address))
        orders_ = cursor.fetchall()
        for order in orders_:
            if order['is_last']==0:
                cursor.execute("UPDATE scheduling SET delivery_order=NULL, pending='0' WHERE id='%d' AND pending='2'" % (order['id']))
                db.commit()
            else:
                cursor.execute(
                    "SELECT cast(sum(red) as unsigned) red, cast(sum(green) as unsigned) green, cast(sum(blue) as unsigned) blue FROM scheduling WHERE id='%d'"% (order['id']))
                idxorders = cursor.fetchall()
                idxorders=idxorders[0]
                cursor.execute("UPDATE orders SET red='%d', green='%d', blue='%d', filldate='%s', delivery_order=NULL, pending='0' WHERE id='%d'" \
                               % (idxorders['red'], idxorders['green'], idxorders['blue'], now, order['id']))
                db.commit()
                cursor.execute("DELETE FROM scheduling WHERE id='%s'" % (order['id']))
                db.commit()
        ###next scheduled number
        #cursor.execute("SELECT address, red, green, blue FROM orders WHERE pending='2' order by delivery_order")
        cursor.execute("SELECT address, cast(sum(red) as unsigned) red, cast(sum(green) as unsigned) green, cast(sum(blue) as unsigned) blue FROM scheduling WHERE pending='2' group by address order by delivery_order")
        orders=cursor.fetchall()

       
        if len(orders)==0:
            next_address=0
        else:
            next_address = orders[0]['address']
        #if address ==next_address:
        #    print("more package to unload")
        socketio.emit('message', com+' '+str(next_address), namespace='/robot')
        socketio.emit('refresh', orders, namespace='/unloading')

        ####inventory replenishment
        inventory=Counter({'red':24, 'green':24, 'blue':24})
        init_r, init_g, init_b = 24, 24, 24
        shipping_r, shipping_g, shipping_b = 0,0,0
        cursor.execute("SELECT red, blue, green FROM scheduling where pending='2'")
        shipping=cursor.fetchall()

        shipping_sum=Counter()
        for s in shipping:
            shipping_sum.update(s)
        #shipping_sum=sum(map(Counter, shipping), Counter())
        inventory.subtract(shipping_sum)
        cursor.execute("UPDATE inventory  SET red='%s', green='%s', blue='%s'" % (inventory['red'], inventory['green'], inventory['blue']))
        db.commit()
        socketio.emit('inventory', inventory,namespace='/loading')
        socketio.emit('inventory', inventory,namespace='/monitoring')
    cursor.close()

@socketio.on('button', namespace='/loading')
def on_button(data):
    global schedule_time, begin_time, end_time
    global inStop, robotConn, maint
    print('loading '+data)
    com, address = data.split()
#0: completed
#1: pending
#2: shipping
#3: scheduled
    cursor = db.cursor(pymysql.cursors.DictCursor)
    if com =="reset":
        inStop=True
        print(inStop)
        cursor.execute("SELECT id, cast(sum(red) as unsigned) red, cast(sum(green) as unsigned) green, cast(sum(blue) as unsigned) blue from scheduling where pending in ('2','3') group by id")
        scheduled=cursor.fetchall()
        for e in scheduled:
            cursor.execute("SELECT red, green, blue FROM orders WHERE id='%d'"%(e['id']))
            orig=cursor.fetchone()
            cursor.execute("UPDATE orders SET red='%d', green='%d', blue='%d' WHERE id='%d'"%(orig['red']+e['red'], orig['green']+e['green'],orig['blue']+e['blue'],e['id']))
            cursor.execute("DELETE FROM scheduling WHERE id='%d' AND pending in ('2','3')"%(e['id']))
        db.commit()

        socketio.emit('reset', (), namespace='/robot')
        socketio.emit('refresh', (), namespace='/loading')
        socketio.emit('refresh', (), namespace='/unloading')

    elif com == "complete":
        print(inStop, robotConn)
        if maint or not inStop or not robotConn:
            cursor.close()
            return
        inStop = False
        cursor.execute("UPDATE scheduling SET pending='2' WHERE pending='3'")
        db.commit()

        ##next address

        cursor.execute("SELECT address, cast(sum(red) as unsigned) red, cast(sum(green) as unsigned) green, cast(sum(blue) as unsigned) blue FROM scheduling WHERE pending='2' group by address order by delivery_order")
        c_orders = cursor.fetchall()
        #print("c_orders : ",c_orders)
        if len(c_orders)==0:
            next_address = 0
        else:
            next_address = c_orders[0]['address']
        ###inventory
        #cursor.execute("SELECT red, blue, green, pending=2 FROM orderdb.orders")
        #c_orders = cursor.fetchall()

        #current_orders=sum(map(Counter, c_orders), Counter())
        current_orders=Counter()
        for c in c_orders:
            current_orders.update(c)
        cursor.execute("insert into clicklogs(status, red, green, blue, schedule, begin, end) values('load','%d','%d','%d','%s','%s','%s')"%(current_orders['red'],current_orders['green'],current_orders['blue'],schedule_time, begin_time,datetime.now()))
        db.commit()

        cursor.execute("SELECT red, blue, green FROM inventory")
        #inventory = Counter(cursor.fetchall()[0])
        inventory = Counter({'red':24, 'green':24, 'blue':24})
        inventory.subtract(current_orders)

        update_inventory = "UPDATE inventory SET red='%d', green='%d', blue='%d'" % (inventory['red'], inventory['green'], inventory['blue'])
        cursor.execute(update_inventory)
        db.commit()
        socketio.emit('refresh', c_orders, namespace='/unloading')
        socketio.emit('refresh', None, namespace='/loading')
        socketio.emit('inventory', inventory,namespace='/loading')
        socketio.emit('inventory', inventory,namespace='/monitoring')
        
        socketio.emit("message", com+' '+str(next_address), namespace='/robot')
    #elif com == "schedule":
    if com == "schedule" or com == "complete":
        schedule_time=datetime.now()
        cursor.execute("SELECT id, red, green, blue from scheduling where pending='3'")
        scheduled=cursor.fetchall()
        for e in scheduled:
            cursor.execute("SELECT red, green, blue FROM orders WHERE id='%d'"%(e['id']))
            orig=cursor.fetchall()[0]
            cursor.execute("UPDATE orders SET red='%d', green='%d', blue='%d' WHERE id='%d'"%(orig['red']+e['red'], orig['green']+e['green'],orig['blue']+e['blue'],e['id']))
            cursor.execute("DELETE FROM scheduling WHERE id='%d' AND pending='3'"%(e['id']))
        db.commit()
        cursor.execute("SELECT id, address, red, green, blue FROM orders WHERE pending='1'")
        pend_list=cursor.fetchall()

        ###schedule
        update_list, schedule_list = schedule.schedule([p for p in pend_list if p['red']+p['green']+p['blue']!=0], 24)
        for s in schedule_list:
            cursor.execute("INSERT into scheduling(id,address,red,green,blue,delivery_order,is_last,pending) VALUES ('%d','%d','%d','%d','%d','%d','%d','3')"\
                           %(s['id'],s['address'],s['red'],s['green'],s['blue'],s['delivery_order'],s['is_last']))
            #print("init_schedule: ", s)

        for e in update_list:
            cursor.execute("UPDATE orders SET red='%d', green='%d', blue='%d' WHERE id='%d'"%(e['red'],e['green'],e['blue'],e['id']))
            #print("init_update: ", e)
        db.commit()

        cursor.execute("SELECT id, address, red, green, blue FROM scheduling WHERE pending='3'")
        pend_list = cursor.fetchall()
        c_orders=Counter()
        for p in pend_list:
            c_orders.update(p)
        #c_orders=sum(map(Counter, pend_list), Counter())

        socketio.emit('refresh', c_orders, namespace='/loading')
    elif com =="replenish":
        ####inventory replenishment
        inventory=Counter({'red':24, 'green':24, 'blue':24})
        init_r, init_g, init_b = 24, 24, 24
        shipping_r, shipping_g, shipping_b = 0,0,0
        cursor.execute("SELECT red, blue, green FROM scheduling where pending='2'")
        shipping=cursor.fetchall()

        #shipping_sum=sum(map(Counter, shipping), Counter())
        shipping_sum=Counter()
        for s in shipping:
            shipping_sum.update(s)
        inventory.subtract(shipping_sum)
        cursor.execute("UPDATE inventory  SET red='%s', green='%s', blue='%s'" % (inventory['red'], inventory['green'], inventory['blue']))
        db.commit()
        socketio.emit('inventory', inventory,namespace='/loading')
        socketio.emit('inventory', inventory,namespace='/monitoring')

    cursor.close()
#from app.modules import buttonio

        

from app.modules import index, login, loading, unloading, monitoring

app.register_blueprint(index.bp)
app.register_blueprint(login.bp)
app.register_blueprint(loading.bp)
app.register_blueprint(unloading.bp)
app.register_blueprint(monitoring.bp)


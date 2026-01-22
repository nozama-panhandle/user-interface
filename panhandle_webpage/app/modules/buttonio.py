from flask import Blueprint
from flask_socketio import SocketIO
from app.modules import database


@socketio.on('button')
def on_button(data):
    print(data)
    com, address = data.split()

# --- Pending flag info --- #
# Pending 0: completed      #
# Pending 1: pending        #
# Pending 2: shipping       #
# Pending 3: scheduled      #

    db = database.Database()

    if com =="reset":
        reset_update_orders = "UPDATE orders SET pending='1' WHERE pending='2'"
        db.execute(reset_update_orders)
        db.commit()
    elif com == "complete":
        complete_update_orders = "UPDATE orders SET pending='2' WHERE pending='3'"
        db.execute(complete_update_orders)
        db.commit()

        ##next address
        #cursor.execute("SELECT address, red, blue, green FROM orders WHERE pending='2' ORDER BY delivery_order")
        complete_select_orders = "SELECT address, red, blue, green FROM orders WHERE pending='2'"
        c_orders = db.executeAll(complete_select_orders)

        print("kanghae")
        print("c_orders : ",c_orders)
        print("kanghae")
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

        complete_select_inventory = "SELECT red, blue, green FROM inventory"
        inventory = db.executeAll(complete_select_inventory)

        inventory_r = inventory[0]['red']
        inventory_g = inventory[0]['green']
        inventory_b = inventory[0]['blue']

        inventory_r -= current_orders_r
        inventory_g -= current_orders_g
        inventory_b -= current_orders_b

        complete_update_inventory_r = "UPDATE inventory SET red='%d' " % (inventory_r)
        db.execute(complete_update_inventory_r)
        db.commit()
        complete_update_inventory_g = "UPDATE inventory SET green='%d'" % (inventory_g)
        db.execute(complete_update_inventory_g)
        db.commit()
        complete_update_inventory_b = "UPDATE inventory SET blue='%d'" % (inventory_b)
        db.execute(complete_update_inventory_b)
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
        db.execute("UPDATE orders SET pending='0' WHERE pending='2' and address='%s'"%address)
        db.commit()
        ###next scheduled number
        clear_select_orders = "SELECT address FROM orders WHERE pending='2' order by delivery_order"
        next_address = db.executeAll(clear_select_orders)
       
        if len(next_address)==0:
            next_address=0
        else:
            next_address = next_address[0]['address']
        #if address == next_address:
        #    print("more package to unload")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host_ip, host_port))
        s.send((com+' '+str(next_address)).encode('ascii'))
        s.close()
    elif com == "schedule":
        schedule_update_orders_pend = "UPDATE orders SET pending='1' WHERE pending='3'"
        db.execute(schedule_update_orders_pend)
        db.commit()
        
        schedule_select_orders = "SELECT id FROM orders WHERE pending='1'"
        pend_list = db.executeAll(schedule_select_orders)
        print(pend_list)

        schedule_update_orders_id = "UPDATE orders SET pending='3', delivery_order='0' WHERE id='%s'" % (pend_list[0]['id'])
        db.execute(schedule_update_orders_id)
        db.commit()
    elif com == "replenish":
        ####inventory replenishment
        init_r, init_g, init_b = 26, 26, 26
        shipping_r, shipping_g, shipping_b = 0,0,0

        replenish_select_orders = "SELECT red, blue, green FROM orders where pending='2'"
        shipping = db.executeAll(replenish_select_orders)

        for i in range(len(shipping)):
            shipping_r += shipping[i]['red']
            shipping_g += shipping[i]['green']
            shipping_b += shipping[i]['blue']
        shipping_r = init_r - shipping_r
        shipping_g = init_g - shipping_g
        shipping_b = init_b - shipping_b

        replenish_update_inventory_r = "UPDATE inventory  SET red='%s'" % (shipping_r)
        db.execute(replenish_update_inventory_r)
        db.commit()

        replenish_update_inventory_g = "UPDATE inventory  SET green='%s'" % (shipping_g)
        db.execute(replenish_update_inventory_g)
        db.commit()

        replenish_update_inventory_b = "UPDATE inventory  SET blue='%s'" % (shipping_b)
        db.execute(replenish_update_inventory_b)
        db.commit()

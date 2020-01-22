from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask import current_app as app
from app.modules import database

bp = Blueprint("loading_bp", __name__, url_prefix="/")

@bp.route("/loading", methods = ["GET"])
def loading():
    db = database.Database()
    select_orders = "SELECT red, blue, green, pending=1 FROM orderdb.orders"
    orders = db.executeAll(select_orders)

    # try:
    current_orders = orders[0:3]

    current_orders_r = 0
    current_orders_g = 0
    current_orders_b = 0

    for i in range(len(current_orders)):
        current_orders_r += current_orders[i]['red']
        current_orders_g += current_orders[i]['green']
        current_orders_b += current_orders[i]['blue']

    current_orders_dict = {'red': current_orders_r, 'green': current_orders_g, 'blue': current_orders_b}

    # try:
    next_orders = orders[3:6]

    next_orders_r = 0
    next_orders_g = 0
    next_orders_b = 0

    for i in range(len(next_orders)):
        next_orders_r += next_orders[i]['red']
        next_orders_g += next_orders[i]['green']
        next_orders_b += next_orders[i]['blue']

    next_orders_dict = {'red': next_orders_r, 'green': next_orders_g, 'blue': next_orders_b}
   
    ##inventory
    select_inventory = "SELECT red, blue, green FROM orderdb.inventory"
    inventory = db.executeAll(select_inventory)
    
    inventory_r = inventory[0]['red']
    inventory_g = inventory[0]['green']
    inventory_b = inventory[0]['blue']

    inventory_dict = {'red': inventory_r, 'green': inventory_g, 'blue': inventory_b}

    inventory[0]['red'] -= current_orders_r
    inventory[0]['green'] -= current_orders_g
    inventory[0]['blue'] -= current_orders_b

    update_inventory_r = "UPDATE orderdb.inventory SET red='%d' " % (inventory[0]['red'])
    db.execute(update_inventory_r)
    db.commit()
    update_inventory_g = "UPDATE orderdb.inventory SET green='%d'" % (inventory[0]['green'])
    db.execute(update_inventory_g)
    db.commit()
    update_inventory_b = "UPDATE orderdb.inventory SET blue='%d'" % (inventory[0]['blue'])
    db.execute(update_inventory_b)
    db.commit()
    

    ####inventory replenishment
    init_r, init_g, init_b = 26, 26, 26
    shipping_r, shipping_g, shipping_b = 0,0,0
    sql = "SELECT red, blue, green, pending=2 FROM orderdb.orders"
    shipping = db.executeAll(sql)
    for i in range(len(shipping)):
         shipping_r += shipping[i]['red']
         shipping_g += shipping[i]['green']
         shipping_b += shipping[i]['blue']
    shipping_r = init_r - shipping_r 
    shipping_g = init_g - shipping_g
    shipping_b = init_b - shipping_b  
   
    sql = "UPDATE orderdb.orders  SET red='%d'" % (shipping_r)
    db.execute(sql)
    db.commit()
    sql = "UPDATE orderdb.orders  SET green='%d'" % (shipping_g)
    db.execute(sql)
    db.commit()
    sql = "UPDATE orderdb.orders  SET blue='%d'" % (shipping_b)
    db.execute(sql)
    db.commit()



    return render_template("/pages/loading.html",
                           title="Loading",
                           current_order=current_orders_dict,
                           next_order=next_orders_dict,
                           inventory=inventory_dict)

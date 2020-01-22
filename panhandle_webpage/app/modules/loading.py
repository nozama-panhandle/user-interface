from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask import current_app as app
from app.modules import database

bp = Blueprint("loading_bp", __name__, url_prefix="/")

@bp.route("/loading", methods = ["GET"])
def loading():
    db_select = database.Database()
    sql = "SELECT red, blue, green, pending=1 FROM orderdb.orders"
    selected_data = db_select.executeAll(sql)

    # try:
    current_data = selected_data[0:3]
    print(current_data[0]['red'])
    print(type(current_data[0]))
    print(len(current_data))

    current_red_sum = 0
    current_green_sum = 0
    current_blue_sum = 0

    for i in range(len(current_data)):
        current_red_sum += current_data[i]['red']
        current_green_sum += current_data[i]['green']
        current_blue_sum += current_data[i]['blue']

    # try:
    next_data = selected_data[3:6]

    next_red_sum = 0
    next_green_sum = 0
    next_blue_sum = 0

    for i in range(len(next_data)):
        next_red_sum += next_data[i]['red']
        next_green_sum += next_data[i]['green']
        next_blue_sum += next_data[i]['blue']


    return render_template("/pages/loading.html",
                           current_red=current_red_sum,
                           current_green=current_green_sum,
                           current_blue=current_blue_sum,
                           next_red=next_red_sum,
                           next_green=next_green_sum,
                           next_blue=next_blue_sum)

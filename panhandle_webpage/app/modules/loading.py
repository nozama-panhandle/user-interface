from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask import current_app as app
from app.modules import database

bp = Blueprint("loading_bp", __name__, url_prefix="/")

@bp.route("/loading", methods = ["GET"])
def loading():
    db_select = database.Database()
    sql = "SELECT red, blue, green, pending=1 FROM orderdb.orders"
    selected_data = db_select.executeAll(sql)

    try:
        data_per_3 = selected_data[0:2]
        print(data_per_3[0]['red'])
        print(type(data_per_3[0]))

        red_sum = 0
        green_sum = 0
        blue_sum = 0

        for i in range(len(data_per_3)):
            red_sum += data_per_3[i]['red']
            green_sum += data_per_3[i]['green']
            blue_sum += data_per_3[i]['blue']
    except:
        data_per_3 = selected_data[0::]

    return render_template("/pages/loading.html",
                           current_red=red_sum,
                           current_green=green_sum,
                           current_blue=blue_sum)

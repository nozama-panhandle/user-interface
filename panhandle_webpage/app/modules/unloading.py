from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask import current_app as app
from app.modules import database

bp = Blueprint("unloading_bp", __name__, url_prefix="/")

@bp.route("/unloading", methods = ["GET"])
def unloading():
    db_select = database.Database()
    sql = "SELECT red, blue, green, pending=1, address FROM orderdb.orders"
    selected_data = db_select.executeAll(sql)

    return render_template("/pages/unloading.html",
                           current_unload=selected_data[0],
                           next_unload=selected_data[1:])

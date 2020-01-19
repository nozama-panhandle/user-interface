from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask import current_app as app
from app.modules import database

bp = Blueprint("unloading_bp", __name__, url_prefix="/")

@bp.route("/unloading", methods = ["GET"])
def unloading():
    db_select = database.Database()
    sql = "SELECT address FROM orderdb.orders"
    row = db_select.executeAll(sql)

    print(row)

    return render_template("/pages/unloading.html",
                           data=row[0])

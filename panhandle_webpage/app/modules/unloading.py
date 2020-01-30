from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask import current_app as app
from app.modules import database

bp = Blueprint("unloading_bp", __name__, url_prefix="/")

@bp.route("/unloading", methods = ["GET"])
def unloading():
    db_select = database.Database()
    sql = "SELECT red, blue, green, address FROM orderdb.orders WHERE pending='2'"
    selected_data = db_select.executeAll(sql)

    print("Length is:", len(selected_data))

    if len(selected_data) == 0:
        current_package = {'red':0, 'blue':0, 'green':0, 'address':0}
        next_package = [{'red':0, 'blue':0, 'green':0, 'address':0}]
    elif len(selected_data) ==  1:
        current_package = selected_data[0]
        # current_package = [{'red':0, 'blue':0, 'green':0, 'address':0}]
        next_package = [{'red':0, 'blue':0, 'green':0, 'address':0}]
    else:
        current_package = selected_data[0]
        next_package = selected_data[1:]

    print("current package:", current_package)

    print("current package length:", len(current_package))

    
    print("next package:", next_package)

    print("next package length:", len(next_package))

    return render_template("/pages/unloading.html",
                           title="Unloading",
                           current_unload=current_package,
                           next_unload=next_package)

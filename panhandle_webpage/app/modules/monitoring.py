from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask import current_app as app

bp = Blueprint("monitoring_bp", __name__, url_prefix="/")

@bp.route("/dashboard", methods = ["GET"])
def maintenance():
    return render_template("/pages/monitoring.html",
                           title="Dashboard")

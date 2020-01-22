from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask import current_app as app

bp = Blueprint("maintenance_bp", __name__, url_prefix="/")

@bp.route("/maintenance", methods = ["GET"])
def maintenance():
    return render_template("/pages/maintenance.html",
                           title="Maintenance")

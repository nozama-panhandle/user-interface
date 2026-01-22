from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask import current_app as app
from app.modules import database

bp = Blueprint("unloading_bp", __name__, url_prefix="/")

@bp.route("/unloading", methods = ["GET"])
def unloading():
    return render_template("/pages/unloading.html",
                           title="Unloading")

from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask import current_app as app
from app.modules import database

bp = Blueprint("loading_bp", __name__, url_prefix="/")

@bp.route("/loading", methods = ["GET"])
def loading():
    return render_template("/pages/loading.html",
                           title="Loading")

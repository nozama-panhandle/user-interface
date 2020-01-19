from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask import current_app as app

bp = Blueprint("index_bp", __name__, url_prefix="/")

@bp.route("/", methods = ["GET"])
def index():
    return render_template("/pages/index.html")

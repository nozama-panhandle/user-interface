from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask import current_app as app

bp = Blueprint("board_bp", __name__, url_prefix="/")

@bp.route("/board", methods = ["GET"])
def loading():
    return

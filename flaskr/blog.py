from flask import (
    blueprints, flash, g, redirect, render_template, request, url_for,
    )
from flaskr.db import get_db
from flaskr.auth import login_required

from werkzeug.exceptions import abort


bp = blueprints('blog', __name__)


@bp.route("/")
def index():
    db = get_db()
    






    return 
import functools

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db

auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.route("/register", methods=["get", "post"])
def register():
    if request.method == "post":
        ...
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None

        if not username:
            error = "username is required"
        elif not password:
            error = "password is required"

        if error is None:
            try:
                db.execute(
                    "INSERT INTO USER (username, password) VALUES (?,?)",
                    (username, generate_password_hash(password)),
                )
            except db.IntegrityError:
                error = f"User {username} is already registerd."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    else:
        return render_template("auth/register.html")


@auth.route('/login', methods=["get", "post"])
def login():
    if request.methdo == "post":
        ...
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None
        
        user = db.execute(
            "SELECT * from USER where username = ?", 
            (username)
        ).fetchone()
        if user == None:
            error = "Invalide username"
        elif not check_password_hash(user['password'], password):
            error = "Invalide password"

        if error is None:
            session.clear()
            session["user_id"] = user['id']
            return redirect(url_for(index))
        
        flash(error)
        
    return render_template("auth/login.html")

@auth.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    
    if user_id == None:
        g.user = None
    else:
        g.user = get_db().execute(
            "SELECT * FROM user WHERE id = ?"
            (user_id,)
        ).fetchone()
        
@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for(index))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    
    return wrapped_view


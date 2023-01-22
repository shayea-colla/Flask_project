from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,
    )
from .db import get_db
from .auth import login_required

from werkzeug.exceptions import abort


bp = Blueprint('blog', __name__)






@bp.route("/")
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
        ).fetchall()
    return render_template("blog/index.html", posts=posts)

@bp.route('/create', methods=("GET", "POST"))
@login_required
def create():
    
    if request.method == "POST":
        title = request.form["title"]
        body  = request.form["body"]
        
        db = get_db()
        error = None
        
        if not title:
            error = "title is required"
        if not body:
            error = "body is required"
        
        if error == None:
            db.execute(
                'INSERT INTO post (title, body, author_id) VALUES (?,?,?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('index'))
        
        flash(error)

    
    return render_template("blog/create.html")


@bp.route("/update/<int:id>", methods=("GET", "POST"))
@login_required
def update(id):
    post = get_post(id)
    
    if request.method == "POST":
        title = request.form["title"]
        body  = request.form["body"]
        db = get_db()
        error = None
        
        if not title:
            error = "title is required"
        if not body: 
            error = "body is required"
        
        if error == None:
            db.execute(
                "UPDATE post SET title = ?, body = ? "
                "WHERE id = ?", 
                (title, body , id)
            )
            db.commit()
    else:
        return render_template('blog/update.html', post=post)






def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post == None:
        abort(404, f"post id {id} doesn't exist")
    
    if check_author and post['author_id'] != g.user['id']:
        abort(403)
    
    return post



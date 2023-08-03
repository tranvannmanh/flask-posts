import functools
from flask import (
    Blueprint,
    g,
    abort,
    redirect,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash
from . import database
from . import models

bp = Blueprint('auth', __name__, url_prefix='/auth')
db = database.db
User = models.User

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        fname = request.json['fname']
        username = request.json['username']
        password = request.json['password']
        error = None

        if not username:
            error = 'Username is required'
        elif not password:
            error = 'Password is required.'

        user_exists = User.query.filter_by(username=username).first()
        if user_exists is not None:
            error = f"user {username} already exists."
    
    if error:
        return {
            "error": error,
            "success": False,
            "result": None
        }
    else:
        db.session.add(User(fname=fname, username=username, password=password))
        db.session.commit()

    return {
        "error": error,
        "success": True,
        "result": {
            "fname": fname,
            "username": username,
            "password": generate_password_hash(password)
        }
    }

# @bp.route('/login', methods=('GET', 'POST'))
# def login():
#     if request.method == 'POST':
#         username = request.json['username']
#         password = request.json['password']
#         error = None
#         user = 

#         if user is None:
#             error = 'Incorrect username.'
#         elif not check_password_hash(user['password'], password):
#             error = 'Incorrect password.'

#         if error is not None:
#             return {
#                 "success": True,
#                 "error": error,
#                 "result": None
#             }

#         # flash(error)

#     session.clear()
#     session['user_id'] = user['id']

#     return {
#         "success": True,
#         "error": error,
#         "result":
#         {
#             "username": username,
#             "password": password
#         }
#     }


# @bp.before_app_request
# def load_logged_in_user():
#     user_id = session.get('user_id')

#     if user_id is None:
#         g.user = None
#     else:
#         g.user = get_db().execute(
#             'SELECT * FROM user WHERE id = ?', (user_id,)
#         ).fetchone()


# @bp.route('/logout')
# def logout():
#     session.clear()
#     return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

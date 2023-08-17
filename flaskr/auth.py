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

bp = Blueprint('auth', __name__, url_prefix='/api/auth')
db = database.db
User = models.User

@bp.route('/register', methods=['POST'])
def register():
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
            "result": None,
            "message": error
        }
    else:
        user = User(fname=fname, username=username, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()

    session['user_id'] = user.id
    return {
        "error": error,
        "success": True,
        "result": {
            "user_id": user.id,
            "fname": fname,
            "username": username,
        },
        "message": f"đăng ký thành công"
    }

@bp.route('/session-login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    error = None
    user = User.query.filter_by(username=username).first()

    if user is None:
        error = 'Incorrect username.'
    elif not check_password_hash(user.password, password):
        error = 'Incorrect password.'

    if error is not None:
        return {
            "success": False,
            "error": error,
            "result": None,
            "message": error
        }

    session.clear()
    session['user_id'] = user.id

    return {
        "success": True,
        "error": error,
        "message": "Đăng nhập thành công",
        "result":
        {
            "username": user.username,
            "fname": user.fname,
            "user_id": user.id
        }
    }


@bp.route('/current-login', methods=['GET'])
def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return {
            "success": False,
            "error": None,
            "result": None
        }
    curr_user = User.query.filter_by(id=user_id).first()
    return {
            "success": True,
            "error": None,
            "result": {
                "fname": curr_user.fname,
                "username": curr_user.username
            }
    }

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

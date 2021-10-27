import functools

from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
# from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """Loads a user if there is currently a user logged in"""
    # If a user id is stored in the session, load the user into g.user
    loggedin_user = session.get("loggedin_user")

    if loggedin_user is None:
        g.user = None
    else:
        g.user = loggedin_user


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """ Logs in a user based on their username, if a user does not currently exist
        creates new user. If a user exists it logs them into the current account
        stores"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        error = None
        pwd_hash = generate_password_hash('changeme')

        if request.form['submit'] == 'Guest User':
            username = "guest"
        elif request.form['submit'] == 'Log In':
            if not username:
                error = "Enter login credentials."

        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session["loggedin_user"] = {'user_id': username, 'username': username, 'password': pwd_hash}
            return redirect(url_for("auth.welcome"))

        flash(error)

    return render_template("auth/login.html")


@bp.route('/welcome', methods=('GET', 'POST'))
@login_required
def welcome():
    """Loads the welcome page once the user has logged in"""
    return render_template("welcome.html")


@bp.route('/app_instructions', methods=('GET', 'POST'))
@login_required
def app_instructions():
    return render_template("instructions.html")


@bp.route("/logout")
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    return redirect(url_for("index"))

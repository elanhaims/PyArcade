# import requests

from flask import Blueprint

# from flask import flash
# from flask import g

from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

# from werkzeug.exceptions import abort

# import json
import requests

# from pyarcade.auth import login_required
# from pyarcade.proxy import MastermindGameProxy
# from pyarcade.mastermind import MastermindGame

# from pyarcade.mancala_proxy import MancalaProxy
# from pyarcade.mancala import MancalaGame
# from pyarcade.connect_four import ConnectFourGame
# from pyarcade.connect_four_proxy import ConnectFourProxy

from flask import session

from pyarcade.auth import login_required

bp = Blueprint("games", __name__)

MASTERMIND = 0
CONNECT4 = 1
MANCALA = 2

MASTERMIND_URL = "/mastermind"
CONNECT4_URL = "/connect4"
MANCALA_URL = "/mancala"
LIST_URL = "/list"
INVITES_URL = "/invites"

game_sessions = {}


@bp.route("/<int:game_id>/new", methods=("GET", "POST"))
@login_required
def new(game_id):
    """
    Flask route that leads to the new page for a game. \n
    The route is /game_id/new

    Args:
        game_id: an int specifying which game page the user wants to navigate to. \n
        An int of 0 routes to the Mastermind new page. \n
        An int of 1 routes to the Connect Four new page.

    """
    server_name = "http://" + request.host
    if game_id == MASTERMIND:
        return render_template("games/mastermind/new.html", game_id=game_id)
    elif game_id == CONNECT4:
        return render_template("games/connect4/new.html", game_id=game_id)
    elif game_id == MANCALA:
        """
        endpoint_url = server_name + MANCALA_URL
        game_session_id = __add_game_session(endpoint_url, game_id)
        return render_template("games/mancala/new.html", game_session_id=game_session_id)
        """
        return render_template("games/mancala/new.html", game_id=game_id)
    else:
        return redirect(url_for("auth.welcome"))


@bp.route("/<int:game_id>/home", methods=("GET", "POST"))
@login_required
def home(game_id):
    """
    Flask route that leads to the home page for a game. \n
    The route is /game_id/home

    Args:
        game_id: an int specifying which game home page the user wants to navigate to. \n
        An int of 0 routes to the Mastermind home page. \n
        An int of 1 routes to the Connect Four home page.
    """

    if game_id == MASTERMIND:
        return __navigate_to_game_home(game_id)
    elif game_id == CONNECT4:
        return __navigate_to_game_home(game_id)
    elif game_id == MANCALA:
        return __navigate_to_game_home(game_id)
    else:
        return redirect(url_for("auth.welcome"))


@bp.route("/<int:game_id>/instructions", methods=("GET", "POST"))
@login_required
def instructions(game_id):
    """
      Flask route that leads to the instructions page for a game. \n
      The route is /game_id/instructions

      Args:
          game_id: an int specifying which game instructions page the user wants to navigate to. \n
          An int of 0 routes to the Mastermind instructions page. \n
          An int of 1 routes to the Connect Four instructions page.
      """

    if game_id == MASTERMIND:
        return render_template("games/mastermind/instructions.html")
    elif game_id == CONNECT4:
        return render_template("games/connect4/instructions.html")
    elif game_id == MANCALA:
        return render_template("games/mancala/instructions.html")
    else:
        return redirect(url_for("auth.welcome"))


@bp.route("/<int:game_id>/highscores", methods=("GET", "POST", "HIGHSCORE"))
@login_required
def highscores(game_id):
    """
    Flask route that leads to the highscores page for a game. \n
    The route is /game_id/highscores

    Args:
        game_id: an int specifying which game highscores page the user wants to navigate to. \n
        An int of 0 routes to the Mastermind highscores page. \n
        An int of 1 routes to the Connect Four highscores page.
    """
    server_name = "http://" + request.host
    if game_id == MASTERMIND:
        endpoint_url = server_name + MASTERMIND_URL + "/highscores"
        highscores_data = __get_high_scores(endpoint_url)
        return render_template("games/mastermind/highscores.html", high_scores=highscores_data)
    elif game_id == CONNECT4:
        endpoint_url = server_name + CONNECT4_URL + "/highscores"
        highscores_data = __get_high_scores(endpoint_url)
        return render_template("games/connect4/highscores.html", high_scores=highscores_data)
    else:
        endpoint_url = server_name + MANCALA_URL + "/highscores"
        highscores_data = __get_high_scores(endpoint_url)
        return render_template("games/mancala/highscores.html", high_scores=highscores_data)


@bp.route("/<int:game_id>/create", methods=("GET", "POST"))
@login_required
def create(game_id):
    """
         Flask route that creates a new game session for a game. \n
         The route is /game_id/create

         Args:
             game_id: an int specifying which game the user wants to create a session for \n
             An int of 0 creates a Mastermind game session. \n
             An int of 1 creates a Connect Four game session. \n

         Routes to the view.html page for Mastermind. \n
         Routes to the edit.html page for Connect Four
         """

    server_name = "http://" + request.host

    if game_id == MASTERMIND:
        endpoint_url = server_name + MASTERMIND_URL
        __add_game_session(endpoint_url, game_id)
        return __navigate_to_game_home(game_id)
    elif game_id == CONNECT4:
        endpoint_url = server_name + CONNECT4_URL
        game_session = __add_game_session(endpoint_url, game_id)
        return render_template("games/connect4/edit.html", game_session=game_session)
    elif game_id == MANCALA:
        endpoint_url = server_name + MANCALA_URL
        game_session = __add_game_session(endpoint_url, game_id)
        return render_template("games/mancala/view.html", game_session=game_session)
    else:
        return redirect(url_for("auth.welcome"))


@bp.route("/<int:game_id>/<string:game_session_id>/view", methods=("GET", "POST"))
@login_required
def view(game_id, game_session_id):
    """
         Flask route that leads to the view page for a game session of a game. \n
         The route is /game_id/game_session_id/view

         Args:
             game_id: an int specifying which game the user is playing. \n
               An int of 0 is for Mastermind. \n
               An int of 1 is for Connect Four. \n
             game_session_id: an int specifying the game session the user wants to view.
         """

    server_name = "http://" + request.host
    if game_id == MASTERMIND:
        endpoint_url = server_name + MASTERMIND_URL
        session_id = game_session_id.replace('%20', ' ')
        json_data = {"game_id": game_id, "session_id": session_id}
        session_data = __retrieve_game_session(endpoint_url, json_data)
        return render_template("games/mastermind/view.html", session_data=session_data,
                               game_session_id=session_data["session_id"])
    elif game_id == CONNECT4:
        endpoint_url = server_name + CONNECT4_URL
        json_data = {"game_id": game_id, "session_id": game_session_id}
        session_data = __retrieve_game_session(endpoint_url, json_data)

        if (session_data["player_num"] != __get_logged_in_user()) or (session_data["status"]):
            return render_template("games/connect4/view.html", game_session=session_data)
        else:
            return render_template("games/connect4/edit.html", game_session=session_data)
    elif game_id == MANCALA:
        endpoint_url = server_name + MANCALA_URL
        json_data = {"game_id": game_id, "session_id": game_session_id}
        session_data = __retrieve_game_session(endpoint_url, json_data)

        if (session_data["player_num"] != __get_logged_in_user()) or (session_data["status"]):
            return render_template("games/mancala/view.html", game_session=session_data)
        else:
            return render_template("games/mancala/view.html", game_session=session_data)
    else:
        return redirect(url_for("auth.welcome"))


@bp.route("/<int:game_id>/<string:game_session_id>/remove", methods=("GET", "POST", "DELETE"))
@login_required
def remove(game_id, game_session_id):
    """
         Flask route that deletes a game session of a game. \n
         The route is /game_id/game_session_id/remove

         Args:
             game_id: an int specifying which game the user is playing. \n
               An int of 0 is for Mastermind. \n
               An int of 1 is for Connect Four. \n
             game_session_id: an int specifying the game session the user wants to delete.

         Routes to the home.html page for the game.
         """

    server_name = "http://" + request.host
    if game_id == MASTERMIND:
        endpoint_url = server_name + MASTERMIND_URL
        __delete_game_session(endpoint_url, game_id, game_session_id)
        return __navigate_to_game_home(game_id)
    elif game_id == CONNECT4:
        endpoint_url = server_name + CONNECT4_URL
        __delete_game_session(endpoint_url, game_id, game_session_id)
        return render_template("games/connect4/home.html", game_sessions=__get_game_sessions(game_id), game_id=game_id)
    elif game_id == MANCALA:
        endpoint_url = server_name + MANCALA_URL
        __delete_game_session(endpoint_url, game_id, game_session_id)
        return render_template("games/mancala/home.html", game_sessions=__get_game_sessions(game_id), game_id=game_id)
    else:
        return redirect(url_for("auth.welcome"))


@bp.route("/<int:game_id>/<string:game_session_id>/update", methods=("GET", "POST", "DELETE"))
@login_required
def update(game_id, game_session_id):
    """
         Flask route that updates a game session of a game. \n
         The route is /game_id/game_session_id/update. \n
         Currently only in use for Connect Four.

         Args:
             game_id: an int specifying which game the user is playing. \n
               An int of 0 is for Mastermind. \n
               An int of 1 is for Connect Four. \n
             game_session_id: an int specifying the game session the user wants to update.

         Routes to the view.html page for the game.
         """

    server_name = "http://" + request.host
    json_data = {"game_id": game_id, "session_id": game_session_id}

    if game_id == MASTERMIND:
        endpoint_url = server_name + MASTERMIND_URL
        json_data = __retrieve_game_session(endpoint_url, json_data)
        new_guess = (int(request.form["guess1"]),
                     int(request.form["guess2"]),
                     int(request.form["guess3"]),
                     int(request.form["guess4"]))
        json_data["guess"] = new_guess
        __update_game_session(endpoint_url, json_data)
        json_data = __retrieve_game_session(endpoint_url, json_data)
        return render_template("games/mastermind/view.html", game_session=json_data)

    elif game_id == CONNECT4:
        endpoint_url = server_name + CONNECT4_URL
        json_data = __retrieve_game_session(endpoint_url, json_data)

        json_data["player_num"] = request.args.get('player_num')
        json_data["column"] = request.args.get('column')
        __update_game_session(endpoint_url, json_data)
        json_data = __retrieve_game_session(endpoint_url, json_data)

        return render_template("games/connect4/view.html", game_session=json_data)
    else:
        return redirect(url_for("auth.welcome"))


@bp.route("/<int:game_id>/<string:game_session_id>/<int:guess_one>/<int:guess_two>/<int:guess_three>/<int:guess_four"
          ">/update",
          methods=("GET", "POST", "DELETE"))
@login_required
def update_mastermind(game_id, game_session_id, guess_one, guess_two, guess_three, guess_four):
    """
         Flask route that updates a game session of Mastermind. \n
         The route is /game_id/game_session_id/guess_one/guess_two/guess_three/guess_four/update

         Args:
             game_id: an int specifying which game the user is playing. \n
               An int of 0 is for Mastermind. \n
             game_session_id: an int specifying the game session the user wants to delete. \n
             guess_one: an int specifying the first digit of the guess. \n
             guess_two: an int specifying the second digit of the guess. \n
             guess_three: an int specifying the third digit of the guess. \n
             guess_four: an int specifying the fourth digit of the guess.

         Routes to the home.html page for the game.
         """

    if game_id == MASTERMIND:
        server_name = "http://" + request.host
        endpoint_url = server_name + MASTERMIND_URL
        session_id = game_session_id.replace('%20', ' ')
        json_data = {"game_id": game_id, "session_id": session_id}
        json_data = __retrieve_game_session(endpoint_url, json_data)
        guess_tuple = (int(guess_one), int(guess_two), int(guess_three), int(guess_four))
        json_data["guess"] = guess_tuple
        __update_game_session(endpoint_url, json_data)
        json_data = __retrieve_game_session(endpoint_url, json_data)
        return render_template("games/mastermind/view.html", game_session_id=session_id, game_id=game_id,
                               session_data=json_data)
    return redirect(url_for("auth.welcome"))


@bp.route("/<int:game_id>/<string:game_session_id>/<int:row>/<int:col>/<string:player_num>/update",
          methods=("GET", "POST", "DELETE"))
@login_required
def update_mancala(game_id, game_session_id, row, col, player_num):
    if game_id == MANCALA:
        server_name = "http://" + request.host
        endpoint_url = server_name + MANCALA_URL

        json_data = {"game_id": game_id, "session_id": game_session_id}
        json_data = __retrieve_game_session(endpoint_url, json_data)
        json_data['row'] = int(row)
        json_data['column'] = int(col)
        json_data['player_num'] = player_num
        __update_game_session(endpoint_url, json_data)
        json_data = __retrieve_game_session(endpoint_url, json_data)
        return render_template("games/mancala/view.html", game_session_id=game_session_id, game_id=game_id,
                               game_session=json_data)
    return redirect(url_for("auth.welcome"))


def __add_game_session(endpoint_url, game_id):
    json_data = __get_json_data(game_id)
    resp_obj = requests.post(endpoint_url, json=json_data)
    game_session = resp_obj.json()
    return game_session


def __get_game_sessions(game_id):
    server_name = "http://" + request.host
    endpoint_url = server_name + LIST_URL
    json_data = __get_json_data(game_id)
    resp_obj = requests.post(endpoint_url, json=json_data)
    return resp_obj.json()


def __delete_game_session(endpoint_url, game_id, game_session_id):
    resp_obj = requests.delete(endpoint_url, json={"game_id": game_id, "session_id": game_session_id})
    return resp_obj.json()


def __retrieve_game_session(endpoint_url, json_data):
    resp_obj = requests.get(endpoint_url, json=json_data).json()
    return resp_obj


def __get_game_invites(game_id):
    server_name = "http://" + request.host
    endpoint_url = server_name + INVITES_URL
    json_data = __get_json_data(game_id)
    resp_obj = requests.post(endpoint_url, json=json_data)
    return resp_obj.json()


def __update_game_session(endpoint_url, json_data):
    resp_obj = requests.put(endpoint_url, json=json_data).json()
    return resp_obj


def __update_connect_four_session(endpoint_url, game_session_id, player_num, column):
    resp_obj = requests.post(endpoint_url,
                             json={"session_id": game_session_id, "player_num": player_num, "column": column}).json()
    if resp_obj['player_num'] != 3:
        if resp_obj['player_num'] == 1:
            resp_obj['player_num'] = 2
        else:
            resp_obj['player_num'] = 1
    return resp_obj


def __get_high_scores(endpoint_url):
    resp_obj = requests.get(endpoint_url)
    high_scores = resp_obj.json()
    return high_scores


def __navigate_to_game_home(game_id):
    if game_id == MASTERMIND:
        return render_template("games/mastermind/home.html", game_sessions=__get_game_sessions(game_id),
                               game_id=game_id,
                               game_invites=__get_game_invites(game_id))
    elif game_id == CONNECT4:
        return render_template("games/connect4/home.html", game_sessions=__get_game_sessions(game_id),
                               game_id=game_id,
                               game_invites=__get_game_invites(game_id))
    elif game_id == MANCALA:
        return render_template("games/mancala/home.html", game_sessions=__get_game_sessions(game_id),
                               game_id=game_id,
                               game_invites=__get_game_invites(game_id))
    else:
        return redirect(url_for("auth.welcome"))


def __get_logged_in_user():
    return session.get("loggedin_user")["user_id"]


def __get_json_data(game_id):
    json_data = {"game_id": game_id}

    # Add user
    user = session.get("loggedin_user")
    json_data["user_id"] = user["user_id"]

    # Add Opponent
    if "opponent_id" in request.form:
        opponent_id = request.form["opponent_id"]
        json_data["opponent_id"] = opponent_id

    return json_data

import os, time

from flask import Flask, redirect, url_for, request
from . import auth
from . import games
from configparser import ConfigParser

from pyarcade.Games.mastermind_proxy import MastermindGameProxy
from pyarcade.Games.mastermind import MastermindGame
from pyarcade.Games.mancala_proxy import MancalaProxy
from pyarcade.Games.mancala import MancalaGame
from pyarcade.Games.connect_four import ConnectFourGame
from pyarcade.Games.connect_four_proxy import ConnectFourProxy
from pyarcade.dynamodb.connection_manager import ConnectionManager
from pyarcade.dynamodb.game_controller import GameController
import simplejson as json


def create_app(test_config=None):
    """
    Creates nd configures the application and creates connection to DynamoDB
    database. Creates blueprints for the authentication and games and redirects
    the user to the login screen.

    index():
        Checks if a game table has been created yet, if not
        it creates a new one

    read_mastermind():
        args:
            request: passes through parameters for read_game
        description:
            Retrieves information about the current mastermind game
            (look at delete_game in mastermind & mastermind_proxy for
            more information)

    post_mastermind():
        args:
            request: passes through parameters for create_game
        description:
            Creates a new session of mastermind and returns a session id
            (look at delete_game in mastermind & mastermind_proxy for
            more information)
    update_mastermind():
        args:
            request: passes through parameters for update_game
        description:
            Updates mastermind with the new play the user attempted
            (look at update_game in mastermind & mastermind_proxy for
            more information)

    delete_mastermind()
        args:
            request: passes through parameters for delete_game
        description:
            Deletes the selected game session of mastermind
            (look at delete_game in mastermind & mastermind_proxy for
            more information)

    get_mastermind_highscores():
        args:
            request: passes through parameters for high_scores
        description:
            Retrieves the high score list saved in mastermind
            (look at delete_game in mastermind & mastermind_proxy for
            more information)

    post_connect_four():
        args:
            request: passes through parameters for create_game
        description:
            Creates a new session of connect4 and returns a session id
            (look at create_game in connect_four & connect_four_proxy for
            more information)

    delete_connect_four():
        args:
            request: passes through parameters for delete_game
        description:
            Deletes the selected game session of connect4
            (look at delete_game in connect_four & connect_four_proxy for
            more information)

    update_connect_four():
        args:
            request: passes through parameters for update_game
        description:
            Updates connect4 with the new play the user attempted
            (look at update_game in connect_four & connect_four_proxy for
            more information)

    update_connect_four_new():
        args:
            request: passes through parameters for update_game
        description:
            Updates connect4 with the new play the user attempted
            alternative to update_connect_four
            (look at update_game in connect_four & connect_four_proxy for
            more information)

    read_connect_four():
        args:
            request: passes through parameters for read_game
        description:
            Retrieves information about the current connect4_game
            (look at read_game in connect_four & connect_four_proxy for
            more information)

    get_connect_four_highscores():
        args:
            request: passes through parameters for high_scores
        description:
            Retrieves the high score list saved in mancala_game
            (look at get_high_scores in connect_four for
            more information)

    read_mancala()
        args:
            request: passes through parameters for read_game
        description:
            Retrieves information about the current mancala game
            (look at read_game in mancala_game & mancala_proxy.py for
            more information)

    post_mancala:
        args:
            request: passes through parameters for create_game
        description:
            Creates a new session of mancala and returns a session id
            (look at create_game in mancala_game & mancala_proxy.py for
            more information)

    update_mancala():
        args:
            request: passes through parameters for update_game
        description:
            Updates mancala with the new play the user attempted
            (look at update_game in mancala_game & mancala_proxy.py for
            more information)

    delete_mancala():
        args:
            request: passes through parameters for delete_game
        description:
            Deletes the selected game session of mancala
            (look at delete_game in mancala_game & mancala_proxy.py for
            more information)

    get_mancala_highscores():
        args:
            request: passes through parameters for highscores
        description:
            Retrieves the high score list saved in mancala_game
            (look at update_game in mancala_game for
            more information)

    list():
        description:
            returns the list of game sessions that currently exist for the
            given game
    invites():
        description:
            gets the list of current invited game sessions
    """
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Read flask app config
    config = ConfigParser()
    config.read(os.path.join(app.instance_path, 'config.cfg'))

    # Set debug mode
    # app.debug = config['flask']['debug']

    # Set secret key
    app.secret_key = config['flask']['secret_key']

    # Read environment variable for whether to read config from EC2 instance metadata
    use_inst_metadata = ""
    if 'USE_EC2_INSTANCE_METADATA' in os.environ:
        use_inst_metadata = os.environ['USE_EC2_INSTANCE_METADATA']

    # Create connection manager to connect to dynamodb
    db_mode = config['dynamodb']['mode']
    db_port = config['dynamodb']['port']
    db_endpoint = None
    if db_mode == "local":
        db_config = None
    else:
        db_config = config

    # Create connection to DynamoDB database
    # ConnectionManager: Look in \final_project\pyarcade\dynamodb folder
    cm = ConnectionManager(mode=db_mode, config=db_config, endpoint=db_endpoint, port=db_port,
                           use_instance_metadata=use_inst_metadata)



    # IMPORTANT
    # GameController: used to perform all database actions
    # Look in \final_project\pyarcade\dynamodb folder
    controller = GameController(cm)

    mastermind_game = MastermindGame(controller)
    mastermind_proxy = MastermindGameProxy(mastermind_game)

    mancala_game = MancalaGame(controller)
    mancala_proxy = MancalaProxy(mancala_game)

    connect_four_game = ConnectFourGame(controller)
    connect_four_proxy = ConnectFourProxy(connect_four_game)

    # Register blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(games.bp)

    # Redirect to login page
    @app.route('/', methods=["GET", "POST"])
    def index():
        # check if games table exist, if not create it
        if controller.check_if_table_is_active() is None:
            cm.create_games_table()

            while not controller.check_if_table_is_active():
                time.sleep(3)

        return redirect(url_for("auth.login"))

    """
    *   Mastermind CRUD *
    """

    # Read - Mastermind
    @app.route('/mastermind', methods=['GET'])
    def read_mastermind():
        return json.dumps(mastermind_proxy.read_game(request.get_json()))

    # Create - Mastermind
    @app.route('/mastermind', methods=["POST"])
    def post_mastermind():
        return json.dumps(mastermind_proxy.create_game(request.get_json()))

    # Update - Mastermind
    @app.route('/mastermind', methods=['PUT'])
    def update_mastermind():
        return json.dumps(mastermind_proxy.update_game(request.get_json()))

    # Delete - Mastermind
    @app.route('/mastermind', methods=["DELETE"])
    def delete_mastermind():
        return json.dumps(mastermind_proxy.delete_game(request.get_json()))

    # HighScore - Mastermind
    @app.route('/mastermind/highscores', methods=['GET'])
    def get_mastermind_highscores():
        return json.dumps(mastermind_game.get_high_scores())

    """
    *   Connect Four CRUD   *
    """

    # Create - Connect Four
    @app.route('/connect4', methods=["POST"])
    def post_connect_four():
        return json.dumps(connect_four_proxy.create_game(request.get_json()))

    # Delete - Connect Four
    @app.route('/connect4', methods=["DELETE"])
    def delete_connect_four():
        return json.dumps(connect_four_proxy.delete_game(request.get_json()))

    # Update - Connect Four - ORIGINAL
    @app.route('/connect4/update', methods=['POST'])
    def update_connect_four():
        return json.dumps(connect_four_proxy.update_game(request.get_json()))

    # Update - Connect Four
    @app.route('/connect4', methods=['PUT'])
    def update_connect_four_new():
        return json.dumps(connect_four_proxy.update_game(request.get_json()))

    # Read - Connect Four
    @app.route('/connect4', methods=['GET'])
    def read_connect_four():
        return json.dumps(connect_four_proxy.read_game(request.get_json()))

    # HighScore - Connect Four
    @app.route('/connect4/highscores', methods=['GET'])
    def get_connect_four_highscores():
        return json.dumps(connect_four_game.get_high_scores())

    """
    *   Mancala CRUD *
    """

    # Read - Mancala
    @app.route('/mancala', methods=['GET'])
    def read_mancala():
        return json.dumps(mancala_proxy.read_game(request.get_json()))

    # Create - Mancala
    @app.route('/mancala', methods=["POST"])
    def post_mancala():
        return json.dumps(mancala_proxy.create_game(request.get_json()))

    # Update - Mancala
    @app.route('/mancala', methods=['PUT'])
    def update_mancala():
        return json.dumps(mancala_proxy.update_game(request.get_json()))

    # Delete - Mancala
    @app.route('/mancala', methods=["DELETE"])
    def delete_mancala():
        return json.dumps(mancala_proxy.delete_game(request.get_json()))

    # HighScore - Mancala
    @app.route('/mancala/highscores', methods=['GET'])
    def get_mancala_highscores():
        return json.dumps(mancala_game.get_high_scores())

    """
    *   List game sessions  *
    """

    @app.route('/list', methods=["POST"])
    def list():
        item_list = json.dumps(controller.all_user_sessions_for_games(request.get_json()))
        return item_list

    """
    *   List game invites  *
    """

    @app.route('/invites', methods=["POST"])
    def invites():
        item_list = json.dumps(controller.all_user_invitation_for_games(request.get_json()))
        return item_list

    return app

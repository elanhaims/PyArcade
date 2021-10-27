from pyarcade.Games.mancala import MancalaGame
from pyarcade.Games.mancala_proxy import MancalaProxy
import unittest

from configparser import ConfigParser
import os
from flask import Flask
from pyarcade.dynamodb.connection_manager import ConnectionManager
from pyarcade.dynamodb.game_controller import GameController

# create and configure the app
app = Flask(__name__, instance_relative_config=True)

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

# Read flask app config
config = ConfigParser()
# config.read(os.path.join(app.instance_path, 'config.cfg'))
config['dynamodb'] = {'dynamodb_service_endpoint': 'dynam', 'dynamodb_port': '8000'}
config['aws'] = {'aws_secret_access_key': 'tbd', 'aws_access_key_id': 'tbd', 'aws_region': 'us-east-1'}
config['flask'] = {'secret_key': 'changeme'}

# Set secret key
app.secret_key = config['flask']['secret_key']

# Get app config info from environment variable
# this will override the parameters in config.cfg
db_config = config
if 'DYNAMODB_SERVICE_ENDPOINT' in os.environ:
    db_config['dynamodb']['dynamodb_service_endpoint'] = os.environ['DYNAMODB_SERVICE_ENDPOINT']
if 'DYNAMODB_PORT' in os.environ:
    db_config['dynamodb']['dynamodb_port'] = os.environ['DYNAMODB_PORT']
if 'AWS_REGION' in os.environ:
    db_config['aws']['aws_region'] = os.environ['AWS_REGION']
if 'AWS_ACCESS_KEY_ID' in os.environ:
    db_config['aws']['aws_access_key_id'] = os.environ['AWS_ACCESS_KEY_ID']
if 'AWS_SECRET_ACCESS_KEY' in os.environ:
    db_config['aws']['aws_secret_access_key'] = os.environ['AWS_SECRET_ACCESS_KEY']

# Create connection to DynamoDB database
# ConnectionManager: Look in \final_project\pyarcade\dynamodb folder
cm = ConnectionManager(config=db_config)

# IMPORTANT
# GameController: used to perform all database actions
# Look in \final_project\pyarcade\dynamodb folder
controller = GameController(cm)


class MancalaProxyCreateGameTests(unittest.TestCase):
    INVALID_INPUT = {'session_id': 0}

    # Tests that the game_id passed through is 2
    def test_create_game_proper_game_id(self):
        game = MancalaGame(controller)
        proxy = MancalaProxy(game)

        create_game_info = proxy.create_game({'game_id': 2, 'user_id': "a", 'opponent_id': "b"})
        session_id = create_game_info['session_id']

        self.assertEqual(session_id != 0, True)

    # Tests that the create_game doesn't take a non-integer value for game_id
    def test_create_game_returns_invalid_when_game_id_is_float(self):
        game = MancalaGame(controller)
        proxy = MancalaProxy(game)

        invalid_create_game = proxy.create_game({'game_id': 2.0})

        self.assertEqual(invalid_create_game, MancalaProxyCreateGameTests.INVALID_INPUT)

    # Tests that the create_game doesn't take a non-integer value for game_id
    def test_create_game_returns_invalid_when_game_id_is_not_two(self):
        game = MancalaGame(controller)
        proxy = MancalaProxy(game)

        invalid_create_game = proxy.create_game({'game_id': 1})

        self.assertEqual(invalid_create_game, MancalaProxyCreateGameTests.INVALID_INPUT)


class MancalaProxyReadGameTests(unittest.TestCase):
    INVALID_INPUT = {'session_id': 0}

    # Tests that read_game is input a valid session_id
    def test_read_game_invalid_session_id_that_exists(self):
        game = MancalaGame(controller)
        proxy = MancalaProxy(game)

        session_one = proxy.create_game({'game_id': 2, 'user_id': "a", 'opponent_id': "b"})['session_id']
        session_two = proxy.create_game({'game_id': 2, 'user_id': "a", 'opponent_id': "b"})['session_id']

        proxy.update_game(({'session_id': session_one, 'row': 1, 'column': 5, 'player_num': 'a'}))
        proxy.update_game(({'session_id': session_one, 'row': 0, 'column': 3, 'player_num': 'b'}))
        proxy.update_game(({'session_id': session_one, 'row': 1, 'column': 1, 'player_num': 'a'}))

        proxy.update_game(({'session_id': session_two, 'row': 1, 'column': 2, 'player_num': 'a'}))
        proxy.update_game(({'session_id': session_two, 'row': 0, 'column': 2, 'player_num': 'b'}))
        proxy.update_game(({'session_id': session_two, 'row': 1, 'column': 1, 'player_num': 'a'}))

        read_game_info = proxy.read_game({'game_id': 2})

        self.assertEqual(read_game_info, MancalaProxyReadGameTests.INVALID_INPUT)

    # Tests that read_game is input a valid session_id
    def test_read_game_valid_session_id(self):
        game = MancalaGame(controller)
        proxy = MancalaProxy(game)

        session_one = proxy.create_game({'game_id': 2, 'user_id': "a", 'opponent_id': "b"})['session_id']

        proxy.update_game(({'session_id': session_one, 'row': 1, 'column': 5, 'player_num': 'a'}))
        proxy.update_game(({'session_id': session_one, 'row': 0, 'column': 3, 'player_num': 'b'}))
        proxy.update_game(({'session_id': session_one, 'row': 1, 'column': 1, 'player_num': 'a'}))

        read_game_info = proxy.read_game({'game_id': 2, 'session_id': session_one})

        self.assertEqual(read_game_info['session_id'], session_one)


class MancalaProxyUpdateGameTests(unittest.TestCase):
    INVALID_INPUT = {'session_id': 0}

    # Tests that update_game passes onto game given a valid input
    def test_update_game_valid_input(self):
        game = MancalaGame(controller)
        proxy = MancalaProxy(game)

        session_id = proxy.create_game({'game_id': 2, 'user_id': "a", 'opponent_id': "b"})['session_id']

        proxy.update_game(({'session_id': session_id, 'row': 1, 'column': 5, 'player_num': 'a'}))
        valid_update = proxy.update_game(({'session_id': session_id, 'row': 0, 'column': 3, 'player_num': 'b'}))

        self.assertNotEqual(valid_update, MancalaProxyUpdateGameTests.INVALID_INPUT)

    # Tests that update_game doesn't take an invalid row as an input
    def test_update_game_invalid_row_input(self):
        game = MancalaGame(controller)
        proxy = MancalaProxy(game)

        session_id = proxy.create_game({'game_id': 2, 'user_id': "a", 'opponent_id': "b"})['session_id']

        proxy.update_game(({'session_id': session_id, 'row': 1, 'column': 5, 'player_num': 'a'}))
        invalid_update = proxy.update_game(({'session_id': session_id, 'row': 2, 'column': 3, 'player_num': 'b'}))

        self.assertEqual(invalid_update, MancalaProxyUpdateGameTests.INVALID_INPUT)

    # Tests that update_game doesn't take an invalid column as an input
    def test_update_game_invalid_column_input(self):
        game = MancalaGame(controller)
        proxy = MancalaProxy(game)

        session_id = proxy.create_game({'game_id': 2, 'user_id': "a", 'opponent_id': "b"})['session_id']

        invalid_update = proxy.update_game(({'session_id': session_id, 'row': 0, 'column': 7, 'player_num': 'b'}))

        self.assertEqual(invalid_update, MancalaProxyUpdateGameTests.INVALID_INPUT)

    # Tests that update_game doesn't allow a player to start their move from either one of the mancala locations
    def test_update_game_invalid_start_loc_is_mancala_loc(self):
        game = MancalaGame(controller)
        proxy = MancalaProxy(game)

        session_id = proxy.create_game({'game_id': 2, 'user_id': "a", 'opponent_id': "b"})['session_id']

        invalid_update = proxy.update_game(({'session_id': session_id, 'row': 0, 'column': 0, 'player_num': 'b'}))
        invalid_update2 = proxy.update_game(({'session_id': session_id, 'row': 1, 'column': 6, 'player_num': 'b'}))

        self.assertEqual(invalid_update, MancalaProxyUpdateGameTests.INVALID_INPUT)
        self.assertEqual(invalid_update2, MancalaProxyUpdateGameTests.INVALID_INPUT)

    # Tests that update_game doesn't allow an invalid player to make a move
    def test_update_game_invalid_player_num(self):
        game = MancalaGame(controller)
        proxy = MancalaProxy(game)

        session_id = proxy.create_game({'game_id': 2, 'user_id': "a", 'opponent_id': "b"})['session_id']

        proxy.update_game(({'session_id': session_id, 'row': 1, 'column': 5, 'player_num': 'a'}))
        invalid_update = proxy.update_game(({'session_id': session_id, 'row': 7, 'column': 3, 'player_num': 3}))

        self.assertEqual(invalid_update, MancalaProxyUpdateGameTests.INVALID_INPUT)

    # Tests that update_game doesn't allow an invalid player to make a move
    def test_update_game_no_session_id(self):
        game = MancalaGame(controller)
        proxy = MancalaProxy(game)

        session_id = proxy.create_game({'game_id': 2, 'user_id': "a", 'opponent_id': "b"})['session_id']

        invalid_update = proxy.update_game(({'row': 1, 'column': 5, 'player_num': 'a'}))

        self.assertEqual(invalid_update, MancalaProxyUpdateGameTests.INVALID_INPUT)


class MancalaProxyDeleteGameTests(unittest.TestCase):
    INVALID_INPUT = {'session_id': 0}

    # Tests that delete_game is input a valid session_id
    def test_delete_game_valid_session(self):
        game = MancalaGame(controller)
        proxy = MancalaProxy(game)

        session_one = proxy.create_game({'game_id': 2, 'user_id': "a", 'opponent_id': "b"})['session_id']
        session_two = proxy.create_game({'game_id': 2, 'user_id': "a", 'opponent_id': "b"})['session_id']

        proxy.update_game(({'session_id': session_one, 'row': 1, 'column': 5, 'player_num': 'a'}))
        proxy.update_game(({'session_id': session_one, 'row': 0, 'column': 3, 'player_num': 'b'}))
        proxy.update_game(({'session_id': session_one, 'row': 1, 'column': 1, 'player_num': 'a'}))

        proxy.update_game(({'session_id': session_two, 'row': 1, 'column': 2, 'player_num': 'a'}))
        proxy.update_game(({'session_id': session_two, 'row': 0, 'column': 2, 'player_num': 'b'}))
        proxy.update_game(({'session_id': session_two, 'row': 1, 'column': 1, 'player_num': 'a'}))

        delete_game_info = proxy.delete_game({'game_id': 2, 'session_id': session_two})

        self.assertNotEqual(delete_game_info, MancalaProxyDeleteGameTests.INVALID_INPUT)

    # Tests that delete_game doesn't pass arguments onto the game if session_id isn't an integer
    def test_delete_game_invalid_float_session_id(self):
        game = MancalaGame(controller)
        proxy = MancalaProxy(game)

        session_one = proxy.create_game({'game_id': 2, 'user_id': "a", 'opponent_id': "b"})['session_id']
        session_two = proxy.create_game({'game_id': 2, 'user_id': "a", 'opponent_id': "b"})['session_id']

        proxy.update_game(({'session_id': session_one, 'row': 1, 'column': 5, 'player_num': 'a'}))
        proxy.update_game(({'session_id': session_one, 'row': 0, 'column': 3, 'player_num': 'b'}))
        proxy.update_game(({'session_id': session_one, 'row': 1, 'column': 1, 'player_num': 'a'}))

        proxy.update_game(({'session_id': session_two, 'row': 1, 'column': 2, 'player_num': 'a'}))
        proxy.update_game(({'session_id': session_two, 'row': 0, 'column': 2, 'player_num': 'b'}))
        proxy.update_game(({'session_id': session_two, 'row': 1, 'column': 1, 'player_num': 'a'}))

        delete_game_info = proxy.delete_game({'game_id': 2, 'session_id': session_one})['session_id']

        self.assertEqual(session_one, delete_game_info)

    # Tests that delete_game doesn't pass arguments onto the game if session_id isn't an integer
    def test_delete_game_no_session_id(self):
        game = MancalaGame(controller)
        proxy = MancalaProxy(game)

        session_one = proxy.create_game({'game_id': 2, 'user_id': "a", 'opponent_id': "b"})['session_id']

        proxy.update_game(({'session_id': session_one, 'row': 1, 'column': 5, 'player_num': 'a'}))
        proxy.update_game(({'session_id': session_one, 'row': 0, 'column': 3, 'player_num': 'b'}))
        proxy.update_game(({'session_id': session_one, 'row': 1, 'column': 1, 'player_num': 'a'}))

        delete_game_info = proxy.delete_game({'game_id': 2})

        self.assertEqual(MancalaProxyDeleteGameTests.INVALID_INPUT, delete_game_info)

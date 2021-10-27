from pyarcade.Games.connect_four import ConnectFourGame
from pyarcade.Games.connect_four_proxy import ConnectFourProxy
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


class ConnectFourProxyTests(unittest.TestCase):
    INVALID_INPUT = {'session_id': 0}

    # Tests that the game_id passed through is 2
    def test_create_game_proper_game_id(self):
        game = ConnectFourGame(controller)
        proxy = ConnectFourProxy(game)

        create_game_info = proxy.create_game({'game_id': 1, 'user_id': "a", 'opponent_id': "b"})
        session_id = create_game_info['session_id']

        self.assertEqual(session_id != 0, True)

        # Tests that the game_id passed through is 2

    def test_create_game_game_id_not_int(self):
        game = ConnectFourGame(controller)
        proxy = ConnectFourProxy(game)

        create_game_info = proxy.create_game({'game_id': 1.0, 'user_id': "a", 'opponent_id': "b"})

        self.assertEqual(ConnectFourProxy.INVALID_INPUT, create_game_info)

    def test_create_game_gives_unique_sequence(self):
        session_ids = []
        game = ConnectFourGame(controller)
        proxy = ConnectFourProxy(game)
        for idx in range(100):
            session_ids.append(proxy.create_game({'game_id': 1, 'user_id': "a", 'opponent_id': "b"})["session_id"])
        self.assertEqual(len(set(session_ids)), 100)

    # Tests that the current game state of a specific session is output
    def test_read_game_outputs_valid_session_info(self):
        game = ConnectFourGame(controller)
        proxy = ConnectFourProxy(game)
        new_session = proxy.create_game({'game_id': 1, 'user_id': "a", 'opponent_id': "b"})
        session_id = new_session['session_id']

        read_result = proxy.read_game({'game_id': 1, 'session_id': session_id})

        self.assertEqual(read_result['session_id'], session_id)

    # Tests that the current game state of a specific session is output
    def test_read_game_no_session_id(self):
        game = ConnectFourGame(controller)
        proxy = ConnectFourProxy(game)
        new_session = proxy.create_game({'game_id': 1, 'user_id': "a", 'opponent_id': "b"})

        read_result = proxy.read_game({'game_id': 1})

        self.assertEqual(ConnectFourProxy.INVALID_INPUT, read_result)

    def test_update_no_session_id(self):
        game = ConnectFourGame(controller)
        proxy = ConnectFourProxy(game)

        session_1 = proxy.create_game({'game_id': 1, 'user_id': "a", 'opponent_id': "b"})

        session_1['column'] = 1
        res = proxy.update_game({'game_id': 1, 'player_num': 'a', 'column': 1})

        self.assertEqual(ConnectFourProxy.INVALID_INPUT, res)

    def test_read_and_update_game_1(self):
        game = ConnectFourGame(controller)
        proxy = ConnectFourProxy(game)

        session_1 = proxy.create_game({'game_id': 1, 'user_id': "a", 'opponent_id': "b"})

        session_1['column'] = 1
        proxy.update_game(session_1)
        session_1 = proxy.read_game({'game_id': 1, 'session_id': session_1['session_id']})
        session1_board = session_1['board']

        self.assertEqual(session1_board[5][0], 'a')

    def test_read_and_update_game_2(self):
        game = ConnectFourGame(controller)
        proxy = ConnectFourProxy(game)

        session_1 = proxy.create_game({'game_id': 1, 'user_id': "a", 'opponent_id': "b"})

        session_1['column'] = 1
        proxy.update_game(session_1)
        session_1 = proxy.read_game({'game_id': 1, 'session_id': session_1['session_id']})
        session_1['column'] = 2
        proxy.update_game(session_1)
        session_1 = proxy.read_game({'game_id': 1, 'session_id': session_1['session_id']})

        self.assertEqual(session_1['board'][5][1], 'b')

    def test_wins_1(self):
        game = ConnectFourGame(controller)
        proxy = ConnectFourProxy(game)

        session_1 = proxy.create_game({'game_id': 1, 'user_id': "a", 'opponent_id': "b"})

        session_1['column'] = 1
        proxy.update_game(session_1)
        session_1 = proxy.read_game({'game_id': 1, 'session_id': session_1['session_id']})
        session_1['column'] = 2
        proxy.update_game(session_1)
        session_1 = proxy.read_game({'game_id': 1, 'session_id': session_1['session_id']})
        session_1['column'] = 1
        proxy.update_game(session_1)
        session_1 = proxy.read_game({'game_id': 1, 'session_id': session_1['session_id']})
        session_1['column'] = 2
        proxy.update_game(session_1)
        session_1 = proxy.read_game({'game_id': 1, 'session_id': session_1['session_id']})
        session_1['column'] = 1
        proxy.update_game(session_1)
        session_1 = proxy.read_game({'game_id': 1, 'session_id': session_1['session_id']})
        session_1['column'] = 2
        proxy.update_game(session_1)
        session_1 = proxy.read_game({'game_id': 1, 'session_id': session_1['session_id']})
        session_1['column'] = 1
        proxy.update_game(session_1)
        session_1 = proxy.read_game({'game_id': 1, 'session_id': session_1['session_id']})

        self.assertEqual(session_1['status'], True)
        self.assertEqual(session_1['player_status']['a'], True)

    def test_delete(self):
        game = ConnectFourGame(controller)
        proxy = ConnectFourProxy(game)

        session_1 = proxy.create_game({'game_id': 1, 'user_id': "a", 'opponent_id': "b"})
        delete_session1_info = proxy.delete_game({'game_id': 1, 'session_id': session_1["session_id"]})
        self.assertEqual(session_1['session_id'], delete_session1_info['session_id'])

    def test_delete_no_session_id(self):
        game = ConnectFourGame(controller)
        proxy = ConnectFourProxy(game)

        proxy.create_game({'game_id': 1, 'user_id': "a", 'opponent_id': "b"})
        delete_session1_info = proxy.delete_game({'game_id': 1})
        self.assertEqual(ConnectFourProxy.INVALID_INPUT, delete_session1_info)

from pyarcade.Games.mastermind import MastermindGame
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


class MastermindFourTest(unittest.TestCase):
    # Tests that create game returns the first valid session_id of 1
    def test_create_game_returns_proper_session_id(self):
        game = MastermindGame(controller)
        session_info = game.create_game({'game_id': 0, 'user_id': "a", 'opponent_id': "b"})
        session_id = session_info['session_id']
        self.assertEqual(type("str"), type(session_id))

    def test_create_game_gives_unique_sequence(self):
        session_ids = []
        game = MastermindGame(controller)
        for idx in range(100):
            session_ids.append(game.create_game({'game_id': 0, 'user_id': "a", 'opponent_id': "b"})["session_id"])
        self.assertEqual(len(set(session_ids)), 100)

    def test_update_game(self):
        game = MastermindGame(controller)

        session_1 = game.create_game({'game_id': 0})

        session_1['guess'] = [1, 2, 3, 4]
        game.update_game(session_1)
        session_1 = game.read_game({'game_id': 0, 'session_id': session_1['session_id']})

        session_1['guess'] = [1, 1, 1, 1]
        game.update_game(session_1)
        session_1 = game.read_game({'game_id': 0, 'session_id': session_1['session_id']})

        session_1['guess'] = [2, 2, 1, 1]
        game.update_game(session_1)
        session_1 = game.read_game({'game_id': 0, 'session_id': session_1['session_id']})

        self.assertEqual(session_1['play_counter'], 3)

    def test_win_game(self):
        game = MastermindGame(controller)

        session_1 = game.create_game({'game_id': 0})

        session_1['guess'] = session_1['target']
        game.update_game(session_1)
        session_1 = game.read_game({'game_id': 0, 'session_id': session_1['session_id']})

        self.assertEqual(session_1['done'], True)

    def test_delete_game(self):
        game = MastermindGame(controller)

        session_1 = game.create_game({'game_id': 0})

        delete_session1_info = game.delete_game({'game_id': 0, 'session_id': session_1["session_id"]})
        self.assertEqual(session_1['session_id'], delete_session1_info['session_id'])


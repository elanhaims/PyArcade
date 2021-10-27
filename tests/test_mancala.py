from pyarcade.Games.mancala import MancalaGame
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


class MancalaTestCreateGame(unittest.TestCase):
    # Tests that create game returns the first valid session_id of 1
    def test_create_game_returns_proper_session_id(self):
        game = MancalaGame(controller)
        session_info = game.create_game({'game_id': 2, 'user_id': "a", 'opponent_id': "b"})
        session_id = session_info['session_id']
        self.assertEqual(type("str"), type(session_id))

    # Tests that create_game outputs the default board
    def test_create_game_gives_default_board(self):
        game = MancalaGame(controller)
        default_board = [[0, 4, 4, 4, 4, 4, 4],
                         [4, 4, 4, 4, 4, 4, 0]]
        session_info = game.create_game({'game_id': 2, 'user_id': "a", 'opponent_id': "b"})
        session_id = session_info['session_id']
        session_board = game.read_game({'game_id': 2, 'session_id': session_id})["board"]
        self.assertEqual(session_board, default_board)

    # Tests that create_game initializes the right players (players 1 and 2)
    def test_create_game_initializes_right_players(self):
        game = MancalaGame(controller)
        valid_players = ['a', 'b']

        session_info = game.create_game({'game_id': 2, 'user_id': "a", 'opponent_id': "b"})
        session_id = session_info['session_id']

        session_players = game.read_game({'game_id': 2, 'session_id': session_id})['players']

        self.assertEqual(valid_players, session_players)

    # Tests that the status is initialized to False after every call to create_game
    def test_create_game_status_initialized_to_false(self):
        game = MancalaGame(controller)

        session_info = game.create_game({'game_id': 2, 'user_id': "a", 'opponent_id': "b"})
        session_id = session_info['session_id']

        session_status = game.read_game({'game_id': 2, 'session_id': session_id})['status']

        self.assertFalse(session_status)

    # Tests that the initial scores for both players are set to zero
    def test_create_game_scores_are_initialized_both_to_zero(self):
        game = MancalaGame(controller)
        initial_score = {'a': 0, 'b': 0}
        session_info = game.create_game({'game_id': 2, 'user_id': "a", 'opponent_id': "b"})
        session_id = session_info['session_id']

        session_score = game.read_game({'game_id': 2, 'session_id': session_id})['score']
        session_score['a'] = int(session_score['a'])
        session_score['b'] = int(session_score['b'])
        self.assertEqual(initial_score, session_score)


class MancalaTestReadGame(unittest.TestCase):

    # Tests that the proper game is read upon given a valid session_id
    def test_read_game_returns_proper_session(self):
        game = MancalaGame(controller)
        game.create_game({'game_id': 2, 'user_id': "a", 'opponent_id': "b"})

        session_info2 = game.create_game({'game_id': 2, 'user_id': "a", 'opponent_id': "b"})

        session_id2 = session_info2['session_id']

        game.update_game(({'session_id': session_id2, 'row': 1, 'column': 2, 'player_num': 'a'}))
        game.update_game(({'session_id': session_id2, 'row': 0, 'column': 2, 'player_num': 'b'}))
        game.update_game(({'session_id': session_id2, 'row': 1, 'column': 1, 'player_num': 'a'}))

        session2_info = game.read_game({'game_id': 2, 'session_id': session_id2})
        check_session_two = {'board': session2_info['board'], 'session_id': session2_info['session_id'],
                             'game_over': session2_info['status'], 'scores': session2_info['score']}
        session2_read = game.read_game({'game_id': 2, 'session_id': session_id2})

        session2_read_info = {'board': session2_read['board'], 'session_id': session2_read['session_id'],
                              'game_over': session2_read['status'], 'scores': session2_read['score']}
        self.assertEqual(check_session_two, session2_read_info)

    # Tests that the scores of read_game changes per update_game
    def test_read_game_scores_is_updated_properly(self):
        game = MancalaGame(controller)

        session_id = game.create_game({'game_id': 2, 'user_id': "a", 'opponent_id': "b"})['session_id']

        game.update_game({'session_id': session_id, 'row': 1, 'column': 2, 'player_num': 'a'})
        game.update_game({'session_id': session_id, 'row': 0, 'column': 2, 'player_num': 'a'})
        game.update_game({'session_id': session_id, 'row': 0, 'column': 1, 'player_num': 'b'})
        game.update_game({'session_id': session_id, 'row': 1, 'column': 1, 'player_num': 'a'})
        game.update_game({'session_id': session_id, 'row': 1, 'column': 5, 'player_num': 'a'})

        game_score = game.read_game({'game_id': 2, 'session_id': session_id})['score']
        game_score['a'] = int(game_score['a'])
        game_score['b'] = int(game_score['b'])

        current_score = {'a': 3, 'b': 2}

        self.assertEqual(current_score, game_score)


class MancalaTestUpdateGame(unittest.TestCase):

    # Test that update game goes counter-clockwise when making an upper row move while placing only one stone in each
    # hole as they drop their stones for their move
    def test_update_game_upper_row_goes_counter_clockwise(self):
        game = MancalaGame(controller)

        session_id = game.create_game({'game_id': 2, 'user_id': "a", 'opponent_id': "b"})['session_id']
        game.update_game({'session_id': session_id, 'row': 0, 'column': 6, 'player_num': 'a'})
        update1 = game.read_game({'game_id': 2, 'session_id': session_id})
        correct_board_after_update1 = [[0, 4, 5, 5, 5, 5, 0],
                                       [4, 4, 4, 4, 4, 4, 0]]
        self.assertEqual(update1['board'], correct_board_after_update1)

    # Test that update game makes a valid move that requires placing a stone in the upper mancala and then moving down.
    def test_update_game_upper_row_goes_counter_clockwise_passing_through_upper_mancala(self):
        game = MancalaGame(controller)

        session_id = game.create_game({'game_id': 2, 'user_id': "a", 'opponent_id': "b"})['session_id']
        game.update_game({'session_id': session_id, 'row': 0, 'column': 2, 'player_num': 'a'})
        update_info = game.read_game({'game_id': 2, 'session_id': session_id})
        correct_board_after_update = [[1, 5, 0, 4, 4, 4, 4],
                                      [5, 5, 4, 4, 4, 4, 0]]
        self.assertEqual(update_info['board'], correct_board_after_update)

    # Test that update game goes counter-clockwise when making an bottom row move while placing only one stone in each
    # hole as they drop their stones for their move
    def test_update_game_bottom_row_goes_counter_clockwise(self):
        game = MancalaGame(controller)

        session_id = game.create_game({'game_id': 2, 'user_id': "a", 'opponent_id': "b"})['session_id']
        game.update_game({'session_id': session_id, 'row': 1, 'column': 0, 'player_num': 'a'})
        update1 = game.read_game({'game_id': 2, 'session_id': session_id})
        correct_board_after_update1 = [[0, 4, 4, 4, 4, 4, 4],
                                       [0, 5, 5, 5, 5, 4, 0]]
        self.assertEqual(update1['board'], correct_board_after_update1)

    # Test that update game makes a valid move that requires placing a stone in the upper mancala and then moving down.
    def test_update_game_bottom_row_goes_counter_clockwise_passing_through_lower_mancala(self):
        game = MancalaGame(controller)

        session_id = game.create_game({'game_id': 2, 'user_id': "a", 'opponent_id': "b"})['session_id']
        game.update_game({'session_id': session_id, 'row': 1, 'column': 5, 'player_num': 'a'})
        update_info = game.read_game({'game_id': 2, 'session_id': session_id})
        correct_board_after_update = [[0, 4, 4, 4, 5, 5, 5],
                                      [4, 4, 4, 4, 4, 0, 1]]
        self.assertEqual(update_info['board'], correct_board_after_update)

    # Tests that update_game returns player1 if the last stone player1 placed on their most recent move was in
    # their own mancala
    def test_update_game_returns_player1_as_next_player_when_last_move_is_own_mancala(self):
        game = MancalaGame(controller)

        session_id = game.create_game({'game_id': 2, 'user_id': "a", 'opponent_id': "b"})['session_id']

        game.update_game({'session_id': session_id, 'row': 1, 'column': 2, 'player_num': 'a'})
        update1_info = game.read_game({'game_id': 2, 'session_id': session_id})
        next_player = update1_info['next_player']

        self.assertEqual('a', next_player)

    # Tests that update_game doesn't return the same player if the player's last stone was placed into
    # the opposite mancala
    def test_update_game_does_not_return_same_player_as_next_if_last_stone_is_opposite_mancala(self):
        game = MancalaGame(controller)

        session_id = game.create_game({'game_id': 2, 'user_id': "a", 'opponent_id': "b"})['session_id']

        game.update_game({'session_id': session_id, 'row': 1, 'column': 2, 'player_num': 'b'})
        update1_info = game.read_game({'game_id': 2, 'session_id': session_id})
        next_player_after_update1 = update1_info['next_player']

        game.update_game({'session_id': session_id, 'row': 0, 'column': 4, 'player_num': 'a'})
        update2_info = game.read_game({'game_id': 2, 'session_id': session_id})
        next_player_after_update2 = update2_info['next_player']

        self.assertEqual(next_player_after_update1, 'a')
        self.assertEqual(next_player_after_update2, 'b')

        # Tests that an end state is encountered after an update to a board


class MancalaTestDeleteGame(unittest.TestCase):

    # Tests that delete_game deletes the proper session
    def test_delete_game_deletes_the_right_session(self):
        game = MancalaGame(controller)

        session_one = game.create_game({'game_id': 2, 'user_id': "a", 'opponent_id': "b"})['session_id']

        session_two = game.create_game({'game_id': 2, 'user_id': "a", 'opponent_id': "b"})['session_id']

        game.update_game({'session_id': session_one, 'row': 1, 'column': 2, 'player_num': 'a'})
        game.update_game({'session_id': session_one, 'row': 0, 'column': 2, 'player_num': 'a'})
        game.update_game({'session_id': session_one, 'row': 0, 'column': 1, 'player_num': 'b'})

        game.update_game({'session_id': session_two, 'row': 1, 'column': 2, 'player_num': 'a'})
        game.update_game({'session_id': session_two, 'row': 0, 'column': 2, 'player_num': 'a'})
        game.update_game({'session_id': session_two, 'row': 0, 'column': 1, 'player_num': 'b'})
        game.update_game({'session_id': session_two, 'row': 1, 'column': 1, 'player_num': 'a'})
        game.update_game({'session_id': session_two, 'row': 1, 'column': 5, 'player_num': 'b'})

        delete_session1_info = game.delete_game({'game_id': 2, 'session_id': session_one})
        deleted_session1_session = delete_session1_info['session_id']

        self.assertEqual(session_one, deleted_session1_session)

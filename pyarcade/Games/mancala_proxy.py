from pyarcade.game_interface import GameInterface
from pyarcade.Games.mancala import MancalaGame


class MancalaProxy(GameInterface):
    """ MancalaProxy is meant to be a mediator between client code
    attempting to play the game Mancala and the Mancala implementation.
    More specifically, this class's responsibility is to validate requests
    before passing them on to a Mancala instance. Separating the responsibility
    of validating inputs to a game and actually running a game helps us follow
    the single-responsibility principle.

    Args:
        game_instance: A reference to the game being played.
    """
    GAME_ID_KEY = 'game_id'
    SESSION_ID_KEY = 'session_id'
    PLAYER_NUM_KEY = 'player_num'
    COLUMN_KEY = 'column'
    ROW_KEY = 'row'
    INVALID_INPUT = {SESSION_ID_KEY: 0}

    def __init__(self, game_instance: MancalaGame):
        self.game_instance = game_instance

    def create_game(self, request: dict) -> dict:
        """
        Args:
            request: dictionary containing single key-value pair. The key is "game_id".
            The value should be the integer 1.

        Returns:
            reply: dictionary containing a single key-value pair. The key is
            "session_id". The value is an integer unique to all ongoing game
            sessions. If the request is invalid, a session_id of zero should be
            returned. Otherwise, pass the request onto the game.
        """
        game_id = request[MancalaProxy.GAME_ID_KEY]
        game_id_is_int = type(game_id) == int

        if game_id != 2 or not game_id_is_int:
            return MancalaProxy.INVALID_INPUT

        return self.game_instance.create_game(request)

    def read_game(self, request: dict) -> dict:
        """
        Args:
            request: dictionary containing single key-value pair. The key is
            "session_id". The value is an integer unique to all ongoing game sessions.

        Returns: reply: dictionary containing four keys. "board": The most current version of the board of the given
        session_id "session_id": The unique session id provided with the original request "game_over": returns True
        if the game is over "scores": returns a Tuple corresponding to the scores of both players.  For example,
        a score of (10, 12) means player 1 scores 10 and player 2 scored 12
        """
        if MancalaProxy.SESSION_ID_KEY in request.keys():
            return self.game_instance.read_game(request)
        else:
            return MancalaProxy.INVALID_INPUT

    def update_game(self, request: dict) -> dict:
        """
        Args: request: dictionary containing four key-value pairs. - The first key is "session_id". The value is a
        integer unique to all ongoing game sessions. - The second key is "row", an integer ranging from 0-1. The
        value should be one of those integers corresponding to the row the player wants to begin their move from. -
        The third key is "column", an integer ranging from 0-6. The value should be one of those integers
        corresponding to the row the player wants to begin their move from. - The fourth key is "player_num." The
        value should be an integer 1 or 2 corresponding to the player making the move.

        Returns:
            reply: dictionary containing four keys.
                "board": An updated version of the board after making their move
                "status": True or False depending on whether an empty row is encountered
                "next_player": The player number corresponding to the player who will make the next move
                "session_id": The unique session id provided with the original request
        """
        if not self.__valid_input(request):
            return MancalaProxy.INVALID_INPUT
        else:
            if not self.valid_data_update(request):
                return MancalaProxy.INVALID_INPUT
            return self.game_instance.update_game(request)

    def delete_game(self, request: dict) -> dict:
        """
        Args:
            request: dictionary containing single key-value pair. The key is
            "session_id". The value is an integer unique to all ongoing
            game sessions.

        Returns:
            reply: dictionary containing single key-value pair. The key is
            "session_id". The value is an integer unique to all ongoing game
            sessions. If the session_id is invalid, then a session_id of
            zero is returned. Otherwise, pass the request onto the game.
        """
        if MancalaProxy.SESSION_ID_KEY in request.keys():
            return self.game_instance.delete_game(request)
        else:
            return MancalaProxy.INVALID_INPUT

    # Check if input data is valid. Returns True for valid input data and False for invalid input data
    def valid_data_update(self, request: dict) -> bool:

        row = request[MancalaProxy.ROW_KEY]
        column = request[MancalaProxy.COLUMN_KEY]
        valid_row_and_col = self.__check_valid_row_and_col(row, column)

        return valid_row_and_col

    # Check if input is valid. Returns True for valid input and False for invalid input
    @staticmethod
    def __valid_input(request: dict) -> bool:
        if MancalaProxy.SESSION_ID_KEY not in request.keys() \
                or MancalaProxy.PLAYER_NUM_KEY not in request.keys() \
                or MancalaProxy.ROW_KEY not in request.keys() \
                or MancalaProxy.COLUMN_KEY not in request.keys():
            return False
        return True

    # Check whether the input row and column is valid and not in a mancala
    @staticmethod
    def __check_valid_row_and_col(row: int, col: int) -> bool:
        valid_coord = False
        if row == 0:
            if col in [1, 2, 3, 4, 5, 6]:
                valid_coord = True
        elif row == 1:
            if col in [0, 1, 2, 3, 4, 5]:
                valid_coord = True
        return valid_coord

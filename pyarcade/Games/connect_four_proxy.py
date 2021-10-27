from pyarcade.game_interface import GameInterface
from pyarcade.Games.connect_four import ConnectFourGame


class ConnectFourProxy(GameInterface):
    """ ConnectFourProxy is meant to be a mediator between client code
    attempting to play the game Connect Four and the Connect Four implementation.
    More specifically, this class's responsibility is to validate requests
    before passing them on to a Connect Four instance. Separating the responsibility
    of validating inputs to a game and actually running a game helps us follow
    the single-responsibility principle.

    Args:
        game_instance: A reference to the game being played.

    """
    GAME_ID_KEY = 'game_id'
    SESSION_ID_KEY = 'session_id'
    PLAYER_NUM_KEY = 'player_num'
    COLUMN_KEY = 'column'
    INVALID_INPUT = {SESSION_ID_KEY: 0}

    def __init__(self, game_instance: ConnectFourGame):
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
        game_id = request[ConnectFourProxy.GAME_ID_KEY]
        game_id_is_int = type(game_id) == int

        if game_id != 1 or not game_id_is_int:
            return ConnectFourProxy.INVALID_INPUT
        else:
            new_session_dict = {ConnectFourProxy.GAME_ID_KEY: game_id}
            return self.game_instance.create_game(request)

    def read_game(self, request: dict) -> dict:
        """
        Args:
            request: dictionary containing single key-value pair. The key is
            "session_id". The value is an integer unique to all ongoing game sessions.

        Returns:
            reply: dictionary containing a single key-value pair. The key is
            "session_id". The value is an integer unique to all ongoing game
            sessions. If the request is invalid, a session_id of zero should be
            returned. Otherwise, pass the request onto the game.

        """
        if ConnectFourProxy.SESSION_ID_KEY not in request.keys():
            return ConnectFourProxy.INVALID_INPUT
        else:
            return self.game_instance.read_game(request)

    def update_game(self, request: dict) -> dict:
        """
        Args:
            request: dictionary containing two key-value pairs. One key is
            "session_id". The value is a integer unique to all ongoing game
            sessions. \n
            The second key is "player_num." The value should be an integer
            1 or 2 corresponding to the player making the move. \n
            The third key is "column", an integer ranging from 1-7.  The value should be one of those
            integers corresponding to the column the player wants to drop their coin in.

        Returns:
            reply: dictionary containing a single key-value pair. The key is
            "session_id". The value is a integer unique to all ongoing game
            sessions. If the request is invalid, a session_id of zero should be
            returned. Otherwise, pass the request onto the game.

        """
        if not self.__valid_input(request):
            return ConnectFourProxy.INVALID_INPUT
        else:
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
        if ConnectFourProxy.SESSION_ID_KEY in request.keys():
            return self.game_instance.delete_game(request)
        else:
            return ConnectFourProxy.INVALID_INPUT

    @staticmethod
    def __valid_input(request: dict) -> bool:
        if ConnectFourProxy.SESSION_ID_KEY not in request.keys() \
                or ConnectFourProxy.PLAYER_NUM_KEY not in request.keys() \
                or ConnectFourProxy.COLUMN_KEY not in request.keys() \
                or int(request[ConnectFourProxy.COLUMN_KEY]) not in range(1, 8):
            return False
        else:
            return True

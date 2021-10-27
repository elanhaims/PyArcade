from pyarcade.game_interface import GameInterface
from pyarcade.Games.mastermind import MastermindGame


class MastermindGameProxy(GameInterface):
    """ MastermindGameProxy is meant to be a mediator between client code
    attempting to play the game Mastermind and the Mastermind implementation.
    More specifically, this class's responsibility is to validate requests
    before passing them on to a Mastermind instance. Separating the responsibility
    of validating inputs to a game and actually running a game helps us follow
    the single-responsibility principle.

    Args:
        game_instance: A reference to the game being played.
    """
    GAME_ID_KEY = 'game_id'
    SESSION_ID_KEY = 'session_id'
    GUESS_KEY = 'guess'
    INVALID_INPUT = {SESSION_ID_KEY: 0}

    def __init__(self, game_instance: MastermindGame):
        self.game_instance = game_instance

    def create_game(self, request: dict) -> dict:
        """
        Args:
            request: dictionary containing single key-value pair. The key is "game_id".
            The value should be zero.

        Returns:
            reply: dictionary containing a single key-value pair. The key is
            "session_id". The value is an integer unique to all ongoing game
            sessions. If the request is invalid, a session_id of zero should be
            returned. Otherwise, pass the request onto the game.
        """
        game_id = request[MastermindGameProxy.GAME_ID_KEY]
        game_id_is_int = type(game_id) == int

        if game_id != 0 or not game_id_is_int:
            return MastermindGameProxy.INVALID_INPUT
        else:
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
        if MastermindGameProxy.SESSION_ID_KEY in request.keys():
            return self.game_instance.read_game(request)
        else:
            return MastermindGameProxy.INVALID_INPUT

    def update_game(self, request: dict) -> dict:
        """
        Args:
            request: dictionary containing two key-value pairs. One key is
            "session_id". The value is a integer unique to all ongoing game
            sessions. The second key is "guess." The value should be a tuple
            of four integers.

        Returns:
            reply: dictionary containing a single key-value pair. The key is
            "session_id". The value is a integer unique to all ongoing game
            sessions. If the request is invalid, a session_id of zero should be
            returned. Otherwise, pass the request onto the game.
        """
        if "session_id" in request.keys() and "guess" in request.keys():
            guess = request[MastermindGameProxy.GUESS_KEY]
        else:
            return MastermindGameProxy.INVALID_INPUT

        guess_is_four_tuple = len(guess) == 4

        each_guess_is_int = self.__check_each_guess_is_an_integer(guess)

        valid_input = guess_is_four_tuple and each_guess_is_int

        if valid_input:
            return self.game_instance.update_game(request)
        else:
            return MastermindGameProxy.INVALID_INPUT

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
        if MastermindGameProxy.SESSION_ID_KEY in request.keys():
            return self.game_instance.delete_game(request)
        else:
            return MastermindGameProxy.INVALID_INPUT

    # ------------------------------------------------------------------------------------------
    " Helper methods for this class can be found here "

    @staticmethod
    def __check_each_guess_is_an_integer(guess: tuple) -> bool:
        each_guess_is_int = True
        for g in guess:
            if type(g) != int:
                each_guess_is_int = False
        return each_guess_is_int

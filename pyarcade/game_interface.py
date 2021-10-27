class GameInterface:
    """ GameInterface is an abstract base class meant to define the interface for anything
    game-like in our software.

    You do not need to modify this file at all. Other classes will implement these functions.

    """
    def create_game(self, request: dict) -> dict:
        """
        Args:
            request: dictionary containing single key-value pair. The key is "game_id". The value
            is an integer denoting which game should be created

        Returns:
            reply: dictionary containing a single key-value pair. The key is "session_id". The value is a
            integer unique to all ongoing game sessions.

        """
        raise NotImplementedError

    def read_game(self, request: dict) -> dict:
        """
        Args:
            request: dictionary containing single key-value pair. The key is "session_id". The value is a
            integer unique to all ongoing game sessions.

        Returns:
            reply: dictionary containing a several key-value pairs that fully describe the game's state.
        """
        raise NotImplementedError

    def update_game(self, request: dict) -> dict:
        """
        Args:
            request: dictionary describing the "move" to be made in the game

        Returns:
            reply: dictionary describing the game's new state.
        """
        raise NotImplementedError

    def delete_game(self, request: dict) -> dict:
        """
        Args:
            request: dictionary containing a single key-value pair. The key is "session_id". The value is a
            integer unique to all ongoing game sessions.

        Returns:
            reply: dictionary containing a single key-value pair. The key is "session_id". The value is a
            integer unique to all ongoing game sessions.
        """
        raise NotImplementedError

from pyarcade.game_interface import GameInterface

from datetime import datetime
from random import randint


class MastermindGame(GameInterface):
    """ A class representing a Mastermind game session.

    Note:
        For now, Mastermind must have a hidden sequence of length 4 in
        which all 4 integers may take on values between 0 and 9.
    """
    SESSION_ID_KEY = 'session_id'
    GUESSES_KEY = 'guesses'
    STATUS_KEY = 'done'
    TARGET_KEY = 'target'
    PLAY_COUNTER_KEY = 'play_counter'
    STATUS = 'status'
    PENDING_STATUS = "PENDING"

    def __init__(self, db_controller):
        self.db = db_controller
        self.SESSION_INFO_MANAGER = {}
        self.SESSION_COUNTER = 0
        self.HIGHSCORE_LIST = [(float('inf'), "empty"), (float('inf'), "empty"), (float('inf'), "empty"),
                               (float('inf'), "empty"), (float('inf'), "empty"), (float('inf'), "empty"),
                               (float('inf'), "empty"), (float('inf'), "empty"), (float('inf'), "empty"),
                               (float('inf'), "empty")]

    def create_game(self, request: dict) -> dict:
        """ Upon calling create_game, the Mastermind game should initialize
        its hidden sequence

         Args:
             request: dictionary containing single key-value pair. The key is "game_id".

         Returns:
            reply: dictionary containing the session_id in the request.
        """

        new_game_session = request
        new_game_session[MastermindGame.TARGET_KEY] = self.__create_target_sequence()
        new_game_session[MastermindGame.GUESSES_KEY] = []
        new_game_session[MastermindGame.STATUS_KEY] = False
        new_game_session[MastermindGame.SESSION_ID_KEY] = str(datetime.now())
        new_game_session[MastermindGame.STATUS] = MastermindGame.PENDING_STATUS
        new_game_session[MastermindGame.PLAY_COUNTER_KEY] = 0

        self.db.create_game(new_game_session)
        return new_game_session

    def read_game(self, request: dict) -> dict:
        """
        Args:
            request: dictionary containing single key-value pair. The key is
            "session_id". The value is an integer unique to all ongoing game sessions.

        Returns:
            reply: dictionary containing three keys. \n
                "guesses": all previous guesses and their respective numbers of
                cows and bulls for this game_session. All guesses should be kept
                as a list of tuples under the key "guesses."
                A guess of (0, 1, 2, 3) that has one cow and two bulls should be
                APPENDED to the list as ((0, 1, 2, 3), (1, 2)). \n
                "session_id": session_id provided with the original request. \n
                "done": True or False depending on whether the game is over.

            So the overall reply could look like: \n
            {"guesses": [((0, 1, 2, 3), (1, 2), ((3, 2, 1, 0), (2, 1))], "session_id": 1, "done": False}
        """
        read_game = self.db.get_game_session(request)
        return read_game

    def update_game(self, request: dict) -> dict:
        """
        Args:
            request: dictionary containing two key-value pairs. One key is
            "session_id". The value is an integer unique to all ongoing game
            sessions. \n
            The second key is "guess." The value should be a tuple
            of four integers.

        Returns:
            reply: dictionary containing three keys.
                "guesses": all previous guesses and their respective numbers of
                cows and bulls for this game_session. All guesses should be kept
                as a list of tuples under the key "guesses."
                A guess of (0, 1, 2, 3) that has one cow and two bulls should be
                APPENDED to the list as ((0, 1, 2, 3), (1, 2)). \n
                "session_id": session_id provided with the original request. \n
                "done": True or False depending on whether the game is over.

            So the overall reply could look like:
            {"guesses": [((0, 1, 2, 3), (1, 2), ((3, 2, 1, 0), (2, 1))], "session_id": 1, "done": False}
        """
        session_info = request

        # Calculate the number of cows and bulls respectively for a certain guess against the session's target key
        cows_bulls_info_with_guess = self.__calculate_cows_and_bulls(session_info['guess'],
                                                                     session_info[MastermindGame.TARGET_KEY])

        # Update the session manager with the newly calculated info for the specified session
        session_info[MastermindGame.GUESSES_KEY].append(cows_bulls_info_with_guess)

        session_info[MastermindGame.PLAY_COUNTER_KEY] += 1

        # Check if user has guessed the right sequence by checking if the bull value is 4
        is_game_over = cows_bulls_info_with_guess[1][1] == 4

        # If game is over update the status keys accordingly
        if is_game_over:
            session_info[MastermindGame.STATUS_KEY] = True
            self.update_high_scores(session_info[MastermindGame.PLAY_COUNTER_KEY], session_info["session_id"])
        else:
            session_info[MastermindGame.STATUS_KEY] = False

        # return updated_status
        resp = self.db.update_game(session_info)
        return resp

    def update_high_scores(self, count, name):
        prev_score = (count, name)

        for i in range(len(self.HIGHSCORE_LIST)):
            if prev_score[0] < self.HIGHSCORE_LIST[i][0]:
                temp_score = self.HIGHSCORE_LIST[i]
                self.HIGHSCORE_LIST[i] = prev_score
                prev_score = temp_score

    def get_high_scores(self):
        return {"scores": self.HIGHSCORE_LIST}

    def delete_game(self, request: dict) -> dict:
        """
        Args:
            request: dictionary containing single key-value pair. The key
            is "session_id". The value is an integer unique to all ongoing
            game sessions.

        Returns:
            reply: dictionary containing the session_id in the request.
        """

        self.db.delete_game_session(request)
        return request

    # -------------------------------------------------------------------------
    # Private Helper methods used in the mastermind.py functions

    # Method used to generate random sequence that player will try to guess
    @staticmethod
    def __create_target_sequence():
        sequence = [randint(1, 9)]

        for index in range(1, 4):
            value = randint(1, 9)
            while value in sequence:
                value = randint(1, 9)
            sequence.append(value)
        return sequence

    # Method used to create the number of bulls in a guess
    @staticmethod
    def __calculate_bulls(guess: tuple, target: tuple) -> int:
        bull_counter = 0
        seq_iterator = 0
        while seq_iterator < 4:
            if target[seq_iterator] == guess[seq_iterator]:
                bull_counter += 1
            seq_iterator += 1
        return bull_counter

    # Method used to create the number of cows in a guess
    @staticmethod
    def __calculate_cows(guess: tuple, target: tuple) -> int:
        cow_counter = 0
        seq_iterator = 0

        guess_no_bulls = []
        target_no_bulls = []

        # Create a new list without the bulls
        while seq_iterator < 4:
            if target[seq_iterator] == guess[seq_iterator]:
                seq_iterator += 1
            else:
                guess_no_bulls.append(guess[seq_iterator])
                target_no_bulls.append(target[seq_iterator])
                seq_iterator += 1

        # Calculate the number of cows by comparing both lists without bulls
        for guess in guess_no_bulls:
            if guess in target_no_bulls:
                cow_counter += 1

        return cow_counter

    # Method used to calculate both the number of cows and bulls
    def __calculate_cows_and_bulls(self, guess: tuple, target: tuple):
        cows = self.__calculate_cows(guess, target)
        bulls = self.__calculate_bulls(guess, target)
        return guess, (cows, bulls)

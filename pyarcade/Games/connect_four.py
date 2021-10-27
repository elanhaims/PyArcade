from pyarcade.game_interface import GameInterface
from datetime import datetime


class ConnectFourGame(GameInterface):
    """ A class representing a Connect Four game session.

    Note:
        For now, Connect Four must have a board initialized with 7 rows and 6 columns .
    """
    BOARD_KEY = 'board'
    PLAYERS_KEY = 'players'
    STATUS_KEY = 'status'
    PLAYER_STATUS_KEY = 'player_status'
    COLUMN_KEY = 'column'
    SESSION_ID_KEY = 'session_id'
    PLAYER_NUM_KEY = 'player_num'
    PLAY_COUNTER_KEY = 'play_counter'
    PLAYER_1_TURNS = 'player_1_turns'
    PLAYER_2_TURNS = 'player_2_turns'

    def __init__(self, db_controller):
        self.db = db_controller
        self.SESSION_INFO_MANAGER = {}
        self.SESSION_COUNTER = 0
        # score record would be a list of lists
        # e.g. [[0, 4, "Peter"], [2, 6, "Tom"]]
        # first value: session_id
        # second value: steps used to win
        # third value: name inserted by the user, currently set as ""
        self.SESSION_SCORE_RECORD = []
        self.HIGHSCORE_LIST = [(float('inf'), "empty"), (float('inf'), "empty"), (float('inf'), "empty"),
                               (float('inf'), "empty"), (float('inf'), "empty"), (float('inf'), "empty"),
                               (float('inf'), "empty"), (float('inf'), "empty"), (float('inf'), "empty"),
                               (float('inf'), "empty")]

    def create_game(self, request: dict) -> dict:
        """ Upon calling create_game, the Mastermind game should initialize
        an empty board

         Args:
             request: dictionary containing single key-value pair. The key is "game_id".

         Returns:
            reply: dictionary containing the session_id in the request.
        """

        new_game_session = request

        new_game_session[ConnectFourGame.SESSION_ID_KEY] = str(datetime.now())
        new_game_session[ConnectFourGame.BOARD_KEY] = self.__create_empty_board()

        new_game_session[ConnectFourGame.PLAYERS_KEY] = [request["user_id"], request["opponent_id"]]

        new_game_session[ConnectFourGame.PLAYER_STATUS_KEY] = {
            request["user_id"]: False,
            request["opponent_id"]: False
        }

        new_game_session[ConnectFourGame.PLAY_COUNTER_KEY] = 0
        new_game_session[ConnectFourGame.STATUS_KEY] = False

        new_game_session[ConnectFourGame.PLAYER_NUM_KEY] = request["user_id"]

        new_game_session[ConnectFourGame.PLAYER_1_TURNS] = 0
        new_game_session[ConnectFourGame.PLAYER_2_TURNS] = 0

        self.SESSION_COUNTER += 1
        self.SESSION_INFO_MANAGER[self.SESSION_COUNTER] = new_game_session

        self.db.create_game(new_game_session)
        return new_game_session

    def read_game(self, request: dict) -> dict:
        """
        Args:
            request: dictionary containing single key-value pair. The key is
            "session_id". The value is an integer unique to all ongoing game sessions.

        Returns:
            reply: dictionary containing four keys.
                "board": The most current version of the board of the given session_id \n
                "session_id": The unique session id provided with the original request \n
                "game_over": returns True if the game is over \n
                "player_num": the previous player who made a turn

            So the overall reply could look like: \n
            {"board": [[0, 0, 0, 0, 0, 0, 0], \n
                       [0, 0, 0, 0, 0, 0, 0], \n
                       [0, 0, 0, 0, 0, 0, 0], \n
                       [0, 0, 0, 2, 0, 0, 0], \n
                       [0, 0, 2, 1, 0, 0, 0], \n
                       [0, 0, 1, 2, 1, 0, 0]], "session_id": 1, "game_over": False}

        """

        game_session = self.db.get_game_session(request)
        return game_session

    def update_game(self, request: dict) -> dict:
        """
        Args:
            request: dictionary containing three key-value pairs. \n
                -One key is "session_id". The value is an integer unique to all ongoing game
                    sessions.  \n
                -The second key is 'player_num' The value should either
                    be 1 or 2, corresponding to player 1 and 2 respectively. \n
                -The third key is 'column' which corresponds to the column (on the scale of 1-7, not 0-6)
                    the player wants to place their coin is.

        Returns:
            reply: dictionary containing four keys. \n
                "board": An updated version of the board after placing the coin in
                         the specified column. \n
                "status": True or False depending on whether the move returned a match of 4 \n
                "session_id": The unique session id provided with the original request \n
                "player_num": The respective player making the move (passed in from the args) \n

            So the overall reply could look like: \n
            {"board": [[0, 0, 0, 0, 0, 0, 0], \n
                       [0, 0, 0, 0, 0, 0, 0], \n
                       [0, 0, 0, 0, 0, 0, 0], \n
                       [0, 0, 0, 2, 0, 0, 0], \n
                       [0, 0, 2, 1, 0, 0, 0], \n
                       [0, 0, 1, 2, 1, 0, 0]], "match": False, "session_id": 1, "player_num": 1}
        """
        session_id = request[ConnectFourGame.SESSION_ID_KEY]
        game_session = request

        # Note the column variable is on a scale from 1-7 not 0-6
        column = int(request[ConnectFourGame.COLUMN_KEY])
        board = game_session[ConnectFourGame.BOARD_KEY]
        player_num = request[ConnectFourGame.PLAYER_NUM_KEY]
        player_key = request["user_id"]
        opponent_key = request["opponent_id"]

        next_valid_row_info = self.__get_next_available_row(board, column)
        column_is_full = next_valid_row_info is None

        player_status = game_session[ConnectFourGame.PLAYER_STATUS_KEY][player_key]
        opponent_status = game_session[ConnectFourGame.PLAYER_STATUS_KEY][opponent_key]

        if column_is_full or player_status or opponent_status:
            game_status = player_status or opponent_status

            if game_session[ConnectFourGame.PLAYER_NUM_KEY] == "3":
                player_num = "3"
            else:
                player_num = player_key if request[ConnectFourGame.PLAYER_NUM_KEY] == opponent_key else opponent_key

            game_session[ConnectFourGame.STATUS_KEY] = game_status
            game_session[ConnectFourGame.PLAYER_NUM_KEY] = player_num
            resp = self.db.update_game(game_session)
            return resp

        updated_game_state = self.__update_board(board, player_num, column)
        game_session[ConnectFourGame.PLAY_COUNTER_KEY] += 1

        # Note that row check is on the scale from 1-6
        row_check = next_valid_row_info['row_coin_is_placed']

        updated_board_state = updated_game_state['updated_board']

        # update the turns the current player has taken

        if player_num == 1:
            game_session[ConnectFourGame.PLAYER_1_TURNS] += 1
        elif player_num == 2:
            game_session[ConnectFourGame.PLAYER_2_TURNS] += 1

        # Check whether a match of 4 exists on the board
        match_exists = self.__check_all_matches(updated_board_state, player_num, row_check, column)

        new_player_num = player_key if player_num == opponent_key else opponent_key
        prev_player_num = game_session[ConnectFourGame.PLAYER_NUM_KEY]
        game_session[ConnectFourGame.PLAYER_NUM_KEY] = new_player_num

        if match_exists:
            game_session[ConnectFourGame.PLAYER_STATUS_KEY][player_num] = match_exists
            game_session[ConnectFourGame.STATUS_KEY] = match_exists
            game_session[ConnectFourGame.PLAYER_NUM_KEY] = prev_player_num
            self.update_high_scores(game_session[ConnectFourGame.PLAY_COUNTER_KEY], session_id)

            if player_num == 1:
                self.SESSION_SCORE_RECORD.append([session_id, game_session[ConnectFourGame.PLAYER_1_TURNS], ""])
            elif player_num == 2:
                self.SESSION_SCORE_RECORD.append([session_id, game_session[ConnectFourGame.PLAYER_2_TURNS], ""])
            self.SESSION_SCORE_RECORD.sort(key=lambda x: x[1])

        # Check if board is full
        elif self.__check_if_board_is_full(updated_board_state):
            player_num = 3
            game_session[ConnectFourGame.PLAYER_NUM_KEY] = player_num

        if player_num == player_key:
            game_session[ConnectFourGame.PLAYER_1_TURNS] += 1
        elif player_num == opponent_key:
            game_session[ConnectFourGame.PLAYER_2_TURNS] += 1

        game_session[ConnectFourGame.BOARD_KEY] = updated_board_state
        resp = self.db.update_game(game_session)
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
    # Private Helper methods used in the connect_four.py functions

    # Method used to generate an empty board
    @staticmethod
    def __create_empty_board():
        empty_board = [[0, 0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0, 0]]
        return empty_board

    # Returns the row the coin will be placed in (scaled from 1-6, NOT 0-5)
    @staticmethod
    def __update_board(board, player_id, column):
        coin = player_id
        i = -1
        while i > -7:
            if board[i][column - 1] == 0:
                board[i][column - 1] = coin
                # Get the proper row_idx (on scale of 1-6) of where coin is placed
                return {'updated_board': board}
            i = i - 1
        return board

    @staticmethod
    def __get_next_available_row(board, column):
        i = -1
        while i > -7:
            if board[i][column - 1] == 0:
                row_num_idx = 7 - (i * -1)
                return {'row_coin_is_placed': row_num_idx}
            i = i - 1

    @staticmethod
    def __check_if_board_is_full(board):
        for column in range(7):
            i = -1
            while i > -7:
                if board[i][column] == 0:
                    return False
                i = i - 1
        return True

    # Method used to find a diagonal pointing right (from the bottom most diagonal point)
    @staticmethod
    def __find_right_diagonal(board, player_num, row_start, col_start):
        coin = player_num
        diagonal_match = True

        #   Adjust indices so that it follows the (0-5) format for row indices and (0-6) format for column indices
        row_idx = row_start - 1
        col_idx = col_start - 1
        row_idx_bound = row_idx - 3

        if row_start < 4:
            diagonal_match = False
            return diagonal_match
        else:
            #       Check bottom left diagonal for four matches after placing a coin in a certain column
            while row_idx >= row_idx_bound:
                if board[row_idx][col_idx] != coin:
                    diagonal_match = False
                    break
                col_idx = col_idx + 1
                row_idx = row_idx - 1
            return diagonal_match

    # Method used to find a diagonal pointing left (from the bottom most diagonal point)
    @staticmethod
    def __find_left_diagonal(board, player_num, row_start, col_start):
        coin = player_num
        diagonal_match = True

        #   Adjust indices so that it follows the (0-5) format for row indices and (0-6) format for column indices
        row_idx = row_start - 1
        col_idx = col_start - 1
        row_idx_bound = row_idx - 3

        if row_start < 4:
            diagonal_match = False
            return diagonal_match
        else:
            #       Check bottom left diagonal for four matches after placing a coin in a certain column
            while row_idx >= row_idx_bound:
                if board[row_idx][col_idx] != coin:
                    diagonal_match = False
                    break
                col_idx = col_idx - 1
                row_idx = row_idx - 1
            return diagonal_match

    # Find a horizontal match in a row upon inputting the left-most horizontal coin location
    @staticmethod
    def __find_horizontal_match_in_row(board, player, row_start, col_start):
        coin = player
        horizontal_match = True

        # Adjust indices so that it follows the (0-5) format for row indices and (0-6) format for column indices
        row_idx = row_start - 1
        col_idx = col_start - 1
        col_idx_bound = col_idx + 3

        if col_start > 4:
            horizontal_match = False
        else:
            while col_idx <= col_idx_bound:
                if board[row_idx][col_idx] != coin:
                    horizontal_match = False
                    break
                col_idx += 1
        return horizontal_match

    # Find a vertical match in a row upon inputting the bottom-most vertical coin location
    @staticmethod
    def __find_vertical_match_in_column(board, player, row_start, col_start):
        coin = player
        vertical_match = True

        # Adjust indices so that it follows the (0-5) format for row indices and (0-6) format for column indices
        row_idx = row_start - 1
        col_idx = col_start - 1
        row_idx_bound = row_idx - 3

        if row_start < 4:
            vertical_match = False
        else:
            while row_idx >= row_idx_bound:
                if board[row_idx][col_idx] != coin:
                    vertical_match = False
                    break
                row_idx = row_idx - 1
        return vertical_match

    # Find all possible horizontal matches upon giving an input row to check
    def __find_all_horizontals_in_row(self, board, player, row_start):
        col_idx = 1
        row_idx = row_start
        horizontal_match = False

        while col_idx <= 4:
            match_exists = self.__find_horizontal_match_in_row(board, player, row_idx, col_idx)
            if match_exists:
                horizontal_match = True
                break
            col_idx += 1
        return horizontal_match

    # Find all possible vertical matches upon giving an input column to check
    def __find_all_verticals_in_column(self, board, player, col_start):
        col_idx = col_start
        row_idx = 5
        vertical_match = False

        while row_idx >= 3:
            match_exists = self.__find_vertical_match_in_column(board, player, row_idx + 1, col_idx)
            if match_exists:
                vertical_match = True
                break
            row_idx = row_idx - 1
        return vertical_match

    # Method used to find if there is a right diagonal for a certain player
    def __find_all_right_diagonals(self, board, player):
        row_idx = 5
        col_idx = 0

        while row_idx >= 3:
            while col_idx <= 3:
                diag_exists = self.__find_right_diagonal(board, player, row_idx + 1, col_idx + 1)
                if diag_exists:
                    return True
                else:
                    col_idx = col_idx + 1
            row_idx = row_idx - 1
            col_idx = 0
        return False

    #  Method used to find if there is a left diagonal for a certain player
    def __find_all_left_diagonals(self, board, player):
        row_idx = 5
        col_idx = 6

        while row_idx >= 3:
            while col_idx >= 3:
                diag_exists = self.__find_left_diagonal(board, player, row_idx + 1, col_idx + 1)
                if diag_exists:
                    return True
                else:
                    col_idx = col_idx - 1
            row_idx = row_idx - 1
            col_idx = 6
        return False

    # Method to check if there exists any diagonal for the specified player
    def __check_diagonals(self, board, player):
        diag_exists = False
        right_diag_exists = self.__find_all_right_diagonals(board, player)
        left_diag_exists = self.__find_all_left_diagonals(board, player)
        if right_diag_exists or left_diag_exists:
            diag_exists = True
        return diag_exists

    # Method to check if there exists any kind of match (diagonal, horizontal, vertical)
    def __check_all_matches(self, board, player, row_start, col_start):
        horiz_match = self.__find_all_horizontals_in_row(board, player, row_start)
        vert_match = self.__find_all_verticals_in_column(board, player, col_start)
        diag_match = self.__check_diagonals(board, player)
        match_exists = horiz_match or vert_match or diag_match
        return match_exists

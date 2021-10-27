from pyarcade.game_interface import GameInterface
from datetime import datetime


class MancalaGame(GameInterface):
    """ A class representing a Mancala game session.

    Note: For now, Mancala must have a board initialized with 2 rows and 6 game columns and 1 stone collection
    column.  Each game column has 4 stones each.
    """
    BOARD_KEY = 'board'
    PLAYERS_KEY = 'players'
    STATUS_KEY = 'status'
    COLUMN_KEY = 'column'
    ROW_KEY = 'row'
    PLAY_COUNTER_KEY = 'play_counter'
    SESSION_ID_KEY = 'session_id'
    SCORE_KEY = 'score'
    NEXT_PLAYER_KEY = 'next_player'
    PLAYER_NUM_KEY = 'player_num'

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
        an empty board

         Args:
             request: dictionary containing single key-value pair. The key is "game_id".

         Returns:
            reply: dictionary containing the session_id in the request.
        """
        new_game_session = request
        new_game_session[MancalaGame.PLAY_COUNTER_KEY] = 0
        new_game_session[MancalaGame.BOARD_KEY] = self.__create_starting_board()
        new_game_session[MancalaGame.PLAYERS_KEY] = [request["user_id"], request["opponent_id"]]
        new_game_session[MancalaGame.STATUS_KEY] = False
        new_game_session[MancalaGame.SCORE_KEY] = {request["user_id"]: 0, request["opponent_id"]: 0}
        new_game_session[MancalaGame.SESSION_ID_KEY] = str(datetime.now())
        new_game_session[MancalaGame.PLAYER_NUM_KEY] = request["user_id"]
        new_game_session[MancalaGame.NEXT_PLAYER_KEY] = request["user_id"]

        self.SESSION_COUNTER += 1
        self.SESSION_INFO_MANAGER[self.SESSION_COUNTER] = new_game_session

        self.db.create_game(new_game_session)
        return new_game_session

    def read_game(self, request: dict) -> dict:
        """
        Args:
            request: dictionary containing single key-value pair. The key is
            "session_id". The value is an integer unique to all ongoing game sessions.

        Returns: reply: dictionary containing four keys. "board": The most current version of the board of the given
        session_id "session_id": The unique session id provided with the original request "game_over": returns True
        if the game is over "scores": returns a Tuple corresponding to the scores of both players.  For example,
        a score of (10, 12) means player 1 scores 10 and player 2 scored 12

        So the overall reply could look like:
            {"board": [[2, 0, 0, 4, 4, 4, 5]
                       [6, 0, 6, 6, 5, 5, 1]], "session_id": 1, "game_over": False}
        """
        """
        session_id = request[MancalaGame.SESSION_ID_KEY]
        game_session = self.SESSION_INFO_MANAGER[session_id]

        board_current_state = game_session[MancalaGame.BOARD_KEY]

        # This variable checks to see if the session that is being read is over or not
        check_game_status = game_session[MancalaGame.STATUS_KEY]

        # Get scores of specified session
        scores_info = game_session[MancalaGame.SCORE_KEY]

        return {MancalaGame.BOARD_KEY: board_current_state,
                MancalaGame.SESSION_ID_KEY: session_id,
                'game_over': check_game_status,
                'scores': scores_info}
        """
        game_session = self.db.get_game_session(request)
        return game_session

    def update_game(self, request: dict) -> dict:
        """
        Args: request: dictionary containing 4 key-value pairs. - The first key is "session_id". The value is an
        integer unique to all ongoing game sessions. - The second key is 'row' The value should be the row number (
        either 0 or 1) of the hole the player wants to begin their move from - The third key is 'column' The value
        should be the column number (from 0-6) of the hole the player wants to begin their move from - The final key
        is 'player_num' and corresponds to the player making the move

        Returns:
            reply: dictionary containing four keys.
                "board": An updated version of the board after making their move
                "status": True or False depending on whether an empty row is encountered
                "session_id": The unique session id provided with the original request

        So the overall reply could look like:
            {"board": [[2, 0, 0, 4, 4, 4, 5]
                       [6, 0, 6, 6, 5, 5, 1]], "status": False, "next_player": 1,"session_id": 1}
        """
        # Retrieve session_id from the arguments
        session_id = request[MancalaGame.SESSION_ID_KEY]

        # Get the specified session from the session info manager
        game_session = self.db.get_game_session({'game_id': 2, "session_id": session_id})

        # Parse out the values from the argument dictionary
        col = request[MancalaGame.COLUMN_KEY]
        row = request[MancalaGame.ROW_KEY]
        player_num = request[MancalaGame.PLAYER_NUM_KEY]

        # Get current state of the board
        board = game_session[MancalaGame.BOARD_KEY]

        # Get players key array. Item at 0 is player's key, item at 1 is opponent key
        players_key_arr = game_session[MancalaGame.PLAYERS_KEY]

        updated_board_state_info = {'updated_board': [[]], 'next_player': None}
        game_session[MancalaGame.PLAY_COUNTER_KEY] = game_session[MancalaGame.PLAY_COUNTER_KEY] + 1

        # Updates the board after specifying the location from where to begin the move
        if row == 0:
            num_stones = self.__get_number_of_stones(board, row, col)
            self.__pick_up_stones(board, row, col)
            updated_board_state_info = self.__update_board_to_left(board, row, col, num_stones, player_num,
                                                                   players_key_arr)
        elif row == 1:
            num_stones = self.__get_number_of_stones(board, row, col)
            self.__pick_up_stones(board, row, col)
            updated_board_state_info = self.__update_board_to_right(board, row, col, num_stones, player_num,
                                                                    players_key_arr)

        # Get just the updated board
        updated_board = updated_board_state_info['updated_board']

        # Get last stone coordinates
        last_stone_loc = updated_board_state_info['last_stone_loc']

        last_stone_row, last_stone_col = last_stone_loc

        # Check whether the last hole the player dropped their stone in was empty.
        # This is an important condition because if the hole was empty prior to placing their last stone in
        # that move then that player gets to move all of the stones in the row across that hole into their
        # own mancala

        is_last_hole_empty = self.__check_hole_is_empty(updated_board, last_stone_row, last_stone_col)
        is_last_hole_mancala = self.__check_hole_is_any_mancala(last_stone_row, last_stone_col)

        if is_last_hole_empty and (is_last_hole_mancala is False):
            updated_board = self.__place_stones_from_opposite_row_into_mancala(updated_board, last_stone_row,
                                                                               last_stone_col, player_num,
                                                                               players_key_arr)
            updated_board_state_info['next_player'] = player_num

        # Get current scores of both players before the most recent move was made
        session_scores = game_session[MancalaGame.SCORE_KEY]
        updated_scores = self.__get_scores(updated_board)

        # Get both players new score after the most recent move
        new_player1_score = updated_scores[0]
        new_player2_score = updated_scores[1]

        # Update session manager with the number of stones collected for each player
        session_scores[players_key_arr[0]] = new_player1_score
        session_scores[players_key_arr[1]] = new_player2_score

        # Get the player who will make the next move
        next_player = updated_board_state_info['next_player']
        game_session['next_player'] = next_player

        # Checks whether the game is over after the most recent move and updates session manager if the respective
        # session is over
        game_status = self.__is_over(updated_board)
        if game_status[0] is True:
            self.update_high_scores(request[MancalaGame.PLAY_COUNTER_KEY], session_id)
            game_session[MancalaGame.STATUS_KEY] = game_status[0]
            # if game is over make the winner as next player
            # winner is the player with max score
            # if it is a tie, next player is None
            if session_scores[players_key_arr[0]] > session_scores[players_key_arr[1]]:
                game_session['next_player'] = players_key_arr[0]
            elif session_scores[players_key_arr[0]] < session_scores[players_key_arr[1]]:
                game_session['next_player'] = players_key_arr[1]
            else:
                game_session['next_player'] = None

        # Update the session manager with the new board
        game_session[MancalaGame.BOARD_KEY] = updated_board

        return self.db.update_game(game_session)

    def get_high_scores(self):
        """
        Returns:
            reply: dictionary containing a list of tuple of score and user as value at index 0
        """
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
    # Private Helper methods used in the mancala.py functions

    # Updated high score list with new win
    def update_high_scores(self, count, name):
        prev_score = (count, name)
        for i in range(len(self.HIGHSCORE_LIST)):
            if prev_score[0] < self.HIGHSCORE_LIST[i][0]:
                temp_score = self.HIGHSCORE_LIST[i]
                self.HIGHSCORE_LIST[i] = prev_score
                prev_score = temp_score

    # Create an empty 2x7 game board.  The column's with zero is the collection hole for each player
    @staticmethod
    def __create_starting_board():
        board = [[0, 4, 4, 4, 4, 4, 4],
                 [4, 4, 4, 4, 4, 4, 0]]
        return board

    # Returns the number of stones present at a specified location
    @staticmethod
    def __get_number_of_stones(board: list, row: int, col: int) -> int:
        num_stones = int(board[row][col])
        return num_stones

    # Empties the stones at the specified location
    @staticmethod
    def __pick_up_stones(board: list, row: int, col: int):
        board[row][col] = 0

    # Checks whether an empty row exists
    @staticmethod
    def __empty_row_exists(board: list) -> bool:
        empty_row_exists = False
        empty_row = [0, 0, 0, 0, 0, 0]
        if board[0][1:] == empty_row:
            empty_row_exists = True
        elif board[1][0:6] == empty_row:
            empty_row_exists = True
        return empty_row_exists

    # Checks whether the hole at the specified location is an empty hole
    @staticmethod
    def __check_hole_is_empty(board: list, row: int, col: int) -> bool:
        is_empty = False
        if board[row][col] == 1:
            is_empty = True
        return is_empty

    # Checks whether the hole at the specified location is the player's own mancala
    @staticmethod
    def __check_hole_is_mancala(row: int, col: int, player_num: int, players_key_arr: list) -> bool:
        is_mancala = False
        if row == 1 and col == 6 and player_num == players_key_arr[0]:
            is_mancala = True
        elif row == 0 and col == 0 and player_num == players_key_arr[1]:
            is_mancala = True
        return is_mancala

    # Checks whether the hole at the specified location is ANY of the mancalas
    @staticmethod
    def __check_hole_is_any_mancala(row: int, col: int) -> int:
        is_mancala = False
        if row == 1 and col == 6:
            is_mancala = True
        elif row == 0 and col == 0:
            is_mancala = True
        return is_mancala

    # Returns the other player number
    @staticmethod
    def __get_other_player_number(player_num: int, players_key_arr: list) -> int:
        if player_num == players_key_arr[0]:
            return players_key_arr[1]
        else:
            return players_key_arr[0]

    # Returns the opposite row number when inputted an argument row
    @staticmethod
    def __get_opposite_row(row: int) -> int:
        if row == 0:
            return 1
        else:
            return 0

    # Returns the opposite col number when inputted an argument row, col
    # if row is one increase col by 1, else decrease col by 2
    @staticmethod
    def __get_opposite_col(row: int, col: int) -> int:
        if row == 0:
            return col - 1
        else:
            return col + 1

    # Returns whether a game is over, if game is over it returns the row in which the empty row was found.
    # If the game is not over, the function just returns (False, None)
    def __is_over(self, board: list) -> tuple:
        game_over = (False, None)
        does_empty_row_exist = self.__empty_row_exists(board)
        if does_empty_row_exist:
            empty_row = [0, 0, 0, 0, 0, 0]
            if board[0][1:] == empty_row:
                game_over = (True, 0)
            elif board[1][0:6] == empty_row:
                game_over = (True, 1)
        return game_over

    # Returns how many stones each player has collected
    def __get_scores(self, board) -> tuple:
        game_over = self.__is_over(board)
        player1_score = board[1][6]
        player2_score = board[0][0]

        if game_over[0] is True:
            # If the empty row is the row corresponding to player 2's side.  Add the remaining stones player 1's score
            if game_over[1] == 0:
                player1_score = player1_score + sum(board[1][0:6])
            # If the empty row is the row corresponding to player 1's side.  Add the remaining stones player 2's score
            elif game_over[1] == 1:
                player2_score = player2_score + sum(board[0][1:])
        scores = (player1_score, player2_score)
        return scores

    # Place stones in opposite location into specified player's mancala
    def __place_stones_from_opposite_row_into_mancala(self, board: list, row: int, col: int, player_num,
                                                      players_key_arr: list) -> list:
        if player_num == players_key_arr[0]:
            mancala = board[1][6]
            opposite_row = self.__get_opposite_row(row)
            opposite_col = self.__get_opposite_col(row, col)
            num_of_stones_in_opposite_hole = self.__get_number_of_stones(board, opposite_row, opposite_col)
            self.__pick_up_stones(board, opposite_row, opposite_col)
            updated_mancala = mancala + num_of_stones_in_opposite_hole
            board[1][6] = updated_mancala
        elif player_num == players_key_arr[1]:
            mancala = board[0][0]
            opposite_row = self.__get_opposite_row(row)
            opposite_col = self.__get_opposite_col(row, col)
            num_of_stones_in_opposite_hole = self.__get_number_of_stones(board, opposite_row, opposite_col)
            self.__pick_up_stones(board, opposite_row, opposite_col)
            updated_mancala = mancala + num_of_stones_in_opposite_hole
            board[0][0] = updated_mancala
        return board

    # Update the board when the user picks a location in the second row
    def __update_board_to_right(self, board: list, row: int, col: int, num_stones: int, player_num,
                                players_key_arr: list) -> list:
        next_player = player_num
        update_dict = {}
        col_idx = col + 1
        last_stone_row = row
        last_stone_col = col_idx
        while num_stones > 0:
            if num_stones == 1:
                last_stone_row = row
                last_stone_col = col_idx - 1
            if col_idx <= 6:
                board[row][col_idx] += 1
            else:
                board_info = self.__update_board_to_left(board, 0, 7, num_stones, player_num, players_key_arr)
                last_stone_row = 0
                last_stone_col = 7 - num_stones
                board = board_info['updated_board']
                break
            col_idx += 1
            last_stone_col = last_stone_col + 1
            num_stones = num_stones - 1

        if last_stone_col < 0:
            last_stone_col = 0

        last_hole_is_mancala = self.__check_hole_is_mancala(last_stone_row, last_stone_col, player_num, players_key_arr)
        if last_hole_is_mancala is False:
            next_player = self.__get_other_player_number(player_num, players_key_arr)

        update_dict['updated_board'] = board
        update_dict['next_player'] = next_player
        update_dict['last_stone_loc'] = (last_stone_row, last_stone_col)

        return update_dict

    def __update_board_to_left(self, board: list, row: int, col: int, num_stones: int, player_num,
                               players_key_arr: list) -> list:
        next_player = player_num
        update_dict = {}
        col_idx = col - 1
        last_stone_row = row
        last_stone_col = col_idx
        while num_stones > 0:
            if num_stones == 1:
                last_stone_row = row
                last_stone_col = col_idx + 1
            if col_idx >= 0:
                if col_idx == 0:
                    last_stone_col = 0
                board[row][col_idx] += 1
            else:
                board_info = self.__update_board_to_right(board, 1, -1, num_stones, player_num, players_key_arr)
                last_stone_row = 1
                last_stone_col = num_stones - 1
                board = board_info['updated_board']
                break

            col_idx = col_idx - 1
            last_stone_col = last_stone_col - 1
            num_stones = num_stones - 1

        if last_stone_col < 0:
            last_stone_col = 0

        last_hole_is_mancala = self.__check_hole_is_mancala(last_stone_row, last_stone_col, player_num, players_key_arr)

        if last_hole_is_mancala is False:
            next_player = self.__get_other_player_number(player_num, players_key_arr)
        
        update_dict['updated_board'] = board
        update_dict['next_player'] = next_player
        update_dict['last_stone_loc'] = (last_stone_row, last_stone_col)

        return update_dict

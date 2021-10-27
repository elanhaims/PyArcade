from .setup_dynamo_db import get_dynamo_db_connection, create_games_table


class ConnectionManager:
    def __init__(self, mode=None, config=None, endpoint=None, port=None, use_instance_metadata=False):
        # db points to the dynamodb database
        self.db = None
        # IMPORTANT: and there is only 1 table for all games which is the games table
        self.games_table = None

        if mode == "local":
            if config is not None:
                raise Exception('Cannot specify config when in local mode')
            if endpoint is None:
                endpoint = 'localhost'
            if port is None:
                port = 8000
            self.db = get_dynamo_db_connection(endpoint=endpoint, port=port, local=True)
        elif mode == "service":
            self.db = get_dynamo_db_connection(config=config, endpoint=endpoint,
                                            use_instance_metadata=use_instance_metadata)
        else:
            raise Exception("Invalid arguments, please refer to usage.")
        self.setup_games_table()

    def setup_games_table(self):
        try:
            self.games_table = self.db.Table('Games')
        except Exception:
            raise Exception("There was an issue trying to retrieve the Games table.")

    def get_games_table(self):
        if self.games_table is None:
            self.setup_games_table()
        return self.games_table

    def create_games_table(self):
        self.games_table = create_games_table(self.db)

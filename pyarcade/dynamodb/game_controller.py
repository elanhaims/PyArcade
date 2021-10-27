import boto3
import os
from boto3.dynamodb.conditions import Key, Attr


class GameController:
    """
    This GameController class basically acts as a singleton providing the necessary
    DynamoDB API calls.
    """

    def __init__(self, connection_manager):
        self.cm = connection_manager
        self.Resource_not_found = 'com.amazonaws.dynamodb.v20120810#ResourceNotFoundException'
        if os.environ.get('AM_I_IN_A_DOCKER_CONTAINER', False):
            self.dynamodb_client = boto3.client('dynamodb', endpoint_url="http://dynamodb-local:8000",
                                                region_name="us-east-1",
                                                aws_access_key_id="AKIAZ67MLYI6E5IPUP4M",
                                                aws_secret_access_key="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")
        else:
            self.dynamodb_client = boto3.client('dynamodb', endpoint_url="http://localhost:8000",
                                                region_name="us-east-1",
                                                aws_access_key_id="AKIAZ67MLYI6E5IPUP4M",
                                                aws_secret_access_key="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")

    def create_game(self, json_data):
        response = self.cm.get_games_table().put_item(Item=json_data)
        return response

    def update_game(self, json_data):
        response = self.cm.get_games_table().put_item(Item=json_data)
        return response

    def all_game_sessions(self, json_data):
        response = self.cm.get_games_table().query(
            KeyConditionExpression=Key('game_id').eq(json_data["game_id"])
        )
        return response['Items']

    def get_game_session(self, json_data):
        response = self.cm.get_games_table().get_item(
            Key={
                'game_id': json_data["game_id"],
                'session_id': json_data["session_id"]
            }
        )
        item = response['Item']
        return item

    def delete_game_session(self, json_data):
        response = self.cm.get_games_table().delete_item(
            Key={
                'game_id': json_data["game_id"],
                'session_id': json_data["session_id"]
            }
        )

    def all_user_sessions_for_games(self, json_data):
        response = self.cm.get_games_table().query(
            IndexName="user_game_index",
            KeyConditionExpression=Key('user_id').eq(json_data["user_id"]) & Key('game_id').eq(json_data["game_id"])
        )
        return response['Items']

    def all_user_invitation_for_games(self, json_data):
        response = self.cm.get_games_table().scan(
            FilterExpression=Attr('game_id').eq(json_data["game_id"]) & Attr('opponent_id').eq(json_data["user_id"])
        )
        items = response['Items']
        return items

    def check_if_table_is_active(self):
        table_name = 'Games'
        existing_tables = self.dynamodb_client.list_tables()['TableNames']
        return_flag = None
        if table_name in existing_tables:
            return_flag = True

        return return_flag

    def get_game(self, gameId):
        """
        Basic get_item call on the Games Table, where we specify the primary key
        GameId to be the parameter gameId.
        Returns None on an ItemNotFound Exception.
        """
        try:
            item = self.cm.get_games_table().get_item(GameId=gameId)
        except "ItemNotFound" as inf:
            return None
        except Exception as e:
            print("----Exception----")
            print(e)
            return None

        return item

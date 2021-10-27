import boto3
import os


def get_dynamo_db_connection(config=None, endpoint=None, port=None, local=False, use_instance_metadata=False):
    if os.environ.get('AM_I_IN_A_DOCKER_CONTAINER', False):
        db = boto3.resource('dynamodb', endpoint_url="http://dynamodb-local:8000")
        return db
    else:
        db = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
        return db


def create_games_table(db):
    if not db:
        if os.environ.get('AM_I_IN_A_DOCKER_CONTAINER', False):
            db = boto3.resource('dynamodb', endpoint_url="http://dynamodb-local:8000")
        else:
            db = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")

    table = db.create_table(
        TableName='Games',
        KeySchema=[
            {
                'AttributeName': 'game_id',
                'KeyType': 'HASH'  # Partition key
            },
            {
                'AttributeName': 'session_id',
                'KeyType': 'RANGE'  # Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'game_id',
                'AttributeType': 'N'
            },
            {
                'AttributeName': 'session_id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'user_id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'opponent_id',
                'AttributeType': 'S'
            }
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "user_game_index",
                "KeySchema": [
                    {
                        'AttributeName': 'user_id',
                        'KeyType': 'HASH'  # Partition key
                    },
                    {
                        'AttributeName': 'game_id',
                        'KeyType': 'RANGE'  # Sort key
                    }
                ],
                "Projection": {
                    "ProjectionType": "ALL"
                },
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 1,
                    "WriteCapacityUnits": 1,
                }
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    )

    return table

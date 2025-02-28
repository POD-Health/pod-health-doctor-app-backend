import json
import uuid
from utils.dynamo_utils import DynamoDBTable
from config.constants import USER_TABLE
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def addUser(event, context):
    try:
        logger.info("Processing addUser request")

        # Parse request body
        body = json.loads(event.get('body', '{}'))
        if not body:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Invalid request body."}),
            }


        # Assign a unique userId if not provided
        if 'userId' not in body or not body['userId']:
            body['userId'] = str(uuid.uuid4())

        # Save to DynamoDB
        table = DynamoDBTable(USER_TABLE)
        table.put_item(body)

        logger.info(f"User added successfully: {body['userId']}")
        return {
            "statusCode": 200,
             headers: {
      "Access-Control-Allow-Origin": "*", 
      "Access-Control-Allow-Credentials": true, 
    },
            "body": json.dumps(body),
        }

    except Exception as e:
        logger.error(f"Error in addUser: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"message": f"Error processing request: {str(e)}"}),
        }
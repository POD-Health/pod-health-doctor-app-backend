import json
import logging
from utils.dynamo_utils import DynamoDBTable
from config.constants import USER_TABLE
from boto3.dynamodb.conditions import Key

# Initialize logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
        "Access-Control-Allow-Methods": "GET,OPTIONS"
    }

def getUserByEmail(event, context):
    # Handle OPTIONS request for CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return {
            "statusCode": 200,
            "headers": get_cors_headers(),
            "body": json.dumps({"message": "OK"})
        }

    try:
        logger.info("Processing getUserByEmail request")

        email_id = event.get('pathParameters', {}).get('emailid')

        if not email_id:
            return {
                "statusCode": 400,
                "headers": get_cors_headers(),
                "body": json.dumps({"message": "Email parameter is required."}),
            }

        # Convert email to lowercase before querying
        email_id = email_id.lower()

        # Query DynamoDB with the extracted 'emailid'
        table = DynamoDBTable(USER_TABLE)

        response = table.query(
            IndexName='email-index',
            KeyConditionExpression=Key('email').eq(email_id)
        )

        # Check if user was found
        if 'Items' not in response or len(response['Items']) == 0:
            return {
                "statusCode": 404,
                "headers": get_cors_headers(),
                "body": json.dumps({"message": "User not found."}),
            }

        user = response['Items'][0]

        logger.info(f"User found successfully: {user['userId']}")
        return {
            "statusCode": 200,
            "headers": get_cors_headers(),
            "body": json.dumps(user),
        }

    except Exception as e:
        logger.error(f"Error in getUserByEmail: {str(e)}")
        return {
            "statusCode": 500,
            "headers": get_cors_headers(),
            "body": json.dumps({"message": f"Error processing request: {str(e)}"}),
        }
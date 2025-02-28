import json
import uuid
from utils.dynamo_utils import DynamoDBTable
from config.constants import USER_TABLE, DEFAULT_TEMPLATE
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def addUser(emailid, event):
    """
    Add a new user to DynamoDB
    
    Args:
        emailid (str): User's email address
        event (dict): The Cognito trigger event
    
    Returns:
        dict: Original event for Cognito trigger or error response
    """
    try:
        # Generate unique user ID
        userId = str(uuid.uuid4())
        
        # Get current timestamp
        timestamp = datetime.utcnow().isoformat()

        # Prepare user data
        data = {
            "userId": userId,
            "email": emailid,
            "defaultTemplate": DEFAULT_TEMPLATE,
            "createdAt": timestamp,
            "updatedAt": timestamp,
            "isActive": True,
        }

        # If this is a Cognito trigger, add additional attributes
        if event.get('request', {}).get('userAttributes'):
            user_attributes = event['request']['userAttributes']
            if 'sub' in user_attributes:
                data['cognitoUserId'] = user_attributes['sub']
            if 'name' in user_attributes:
                data['name'] = user_attributes['name']
            if 'phone_number' in user_attributes:
                data['phoneNumber'] = user_attributes['phone_number']

        # Save to DynamoDB
        table = DynamoDBTable(USER_TABLE)
        table.put_item(data)

        logger.info(f"User added successfully: {userId}")
        
        # If this is a Cognito trigger, return the event
        if event.get('triggerSource'):
            return event
            
        # For direct API calls, return success response
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "User added successfully",
                "userId": userId
            })
        }

    except Exception as e:
        logger.error(f"Error in addUser: {str(e)}")
        # If this is a Cognito trigger, we should raise the error
        if event.get('triggerSource'):
            raise e
            
        # For direct API calls, return error response
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": f"Error processing request: {str(e)}"
            })
        }

import json
import boto3
import os
import logging  # Importing logging for structured log handling
from datetime import datetime
import uuid  # Importing uuid for unique user ID generation

# Initialize logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
user_table = dynamodb.Table('DoctorApp_users')

def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event))

    try:
        # Check if the trigger source is PostConfirmation_ConfirmSignUp
        if event.get('triggerSource') == 'PostConfirmation_ConfirmSignUp':
            logger.info("Trigger source is PostConfirmation_ConfirmSignUp")
            
            # Get user attributes from the Cognito event
            user_attributes = event['request'].get('userAttributes', {})
            logger.info("User attributes: %s", json.dumps(user_attributes))
            
            # Extract relevant information
            email = user_attributes.get('email')
            
            if not email:
                logger.error("Missing email in user attributes")
                raise ValueError("Missing required user attributes")
            
            # Generate a unique UUID for the user ID
            user_id = str(uuid.uuid4())
            logger.info("Generated userId: %s", user_id)
            
            # Create timestamp for user creation
            current_time = datetime.utcnow().isoformat()
            
            # Prepare user record
            user_item = {
                'userId': user_id,
                'email': email,
                'createdAt': current_time,
                'updatedAt': current_time,
                'status': 'ACTIVE',
            }
            logger.info("User item to store: %s", json.dumps(user_item))
            
            # Store user in DynamoDB
            user_table.put_item(Item=user_item)
            logger.info("User successfully stored in DynamoDB")

        # Return the event regardless of the trigger source
        logger.info("Returning event: %s", json.dumps(event))
        return event

    except Exception as e:
        logger.error("Error processing event: %s", str(e), exc_info=True)
        raise

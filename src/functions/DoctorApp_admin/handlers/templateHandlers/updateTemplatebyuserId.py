import json
import boto3
import logging
from botocore.exceptions import ClientError

# Set up DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('DoctorApp_users')

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def updateTemplatebyuserId(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Parse the request body
        body = json.loads(event.get('body', '{}'))
        logger.info(f"JSON Body: {body}")
        
        # Extract required fields
        userId = body.get('userId')  # Assuming doctorId maps to userId
        email = body.get('email')      # Extract the email (sort key)
        template = body.get('defaultTemplate')
        
        # Validate required fields
        if not userId or not email or template is None:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "message": "Missing required fields: userId, email, and template are required"
                })
            }

        # Prepare update expression and attribute values
        update_expression = "SET defaultTemplate = :defaultTemplate"
        expression_attribute_values = {
            ':defaultTemplate': template
        }

        # Perform the UpdateItem operation
        response = table.update_item(
            Key={
                'email': email
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues='ALL_NEW'  # Returns the item with its new values
        )
        
        logger.info(f"UpdateItem successful: {json.dumps(response)}")

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "message": "Template updated successfully",
                "userId": userId,
                "updatedItem": response.get('Attributes', {})
            })
        }

    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logger.error(f"DynamoDB ClientError: {error_code} - {error_message}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "message": "Database operation failed",
                "error": error_message
            })
        }
    except json.JSONDecodeError as e:
        logger.error(f"JSON Decode Error: {str(e)}")
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "message": "Invalid JSON in request body",
                "error": str(e)
            })
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "message": "Internal Server Error",
                "error": str(e)
            })
        }

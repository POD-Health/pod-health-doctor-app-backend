import json
import boto3
import logging
from botocore.exceptions import ClientError

# Set up DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('reportTemplates')

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def getAlltemplates(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Verify table exists and is accessible
        table.table_status
        logger.info("Successfully connected to DynamoDB table")
        
        # Scan DynamoDB table to retrieve all templates
        logger.info("Starting table scan")
        response = table.scan()
        templates = response.get('Items', [])
        logger.info(f"Retrieved {len(templates)} templates")

        if not templates:
            logger.info("No templates found in the database")
            return {
                "statusCode": 404,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({"message": "No templates found"})
            }

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(templates)
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
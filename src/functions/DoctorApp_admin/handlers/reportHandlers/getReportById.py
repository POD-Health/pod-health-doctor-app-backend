import json
import logging
from utils.dynamo_utils import DynamoDBTable
from config.constants import REPORT_TABLE
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def getReportById(event, context):
    """
    Retrieve a medical report by reportId
    """
    try:
        logger.info("Starting getReportById request")
        
        # Extract reportId from path parameters
        report_id = event.get('pathParameters', {}).get('reportId')
        
        if not report_id:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Report ID is required."}),
            }

        # Initialize DynamoDB table
        table = DynamoDBTable(REPORT_TABLE)
        
        # Query parameters
        query_params = {
            'KeyConditionExpression': Key('reportId').eq(report_id),
            'Limit': 1
        }

        try:
            logger.info(f"Querying DynamoDB for report_id: {report_id}")
            response = table.query(**query_params)
            
            items = response.get('Items', [])
            
            # Check if we got any results
            if not items:
                return {
                    "statusCode": 404,
                    "body": json.dumps({
                        "message": "Report not found.",
                        "reportId": report_id
                    }),
                }

            logger.info(f"Successfully retrieved report: {report_id}")
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps({
                    "message": "Report retrieved successfully",
                    "reportId": report_id,
                    "report": items[0]
                }),
            }

        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"DynamoDB error: {error_code} - {str(e)}")
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "message": "Database error occurred",
                    "error": error_code
                }),
            }

    except Exception as e:
        logger.error(f"Error in getReportById: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Error processing request",
                "error": str(e)
            }),
        }
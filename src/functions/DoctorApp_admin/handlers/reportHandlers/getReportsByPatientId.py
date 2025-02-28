import json
import logging
from utils.dynamo_utils import DynamoDBTable
from config.constants import REPORT_TABLE
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def getReportsByPatientId(event, context):
    """
    Retrieve all reports for a specific patient by patientId
    """
    try:
        logger.info("Starting getReportsByPatientId request")
        
        # Extract patientId from path parameters
        patient_id = event.get('pathParameters', {}).get('patientId')
        
        if not patient_id:
            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps({"message": "Patient ID is required."}),
            }

        # Initialize DynamoDB table
        table = DynamoDBTable(REPORT_TABLE)
        
        # Query parameters to filter by patientId using GSI
        query_params = {
            'IndexName': 'patientId-index',  # Name of your GSI
            'KeyConditionExpression': Key('patientId').eq(patient_id)
        }

        try:
            logger.info(f"Querying DynamoDB for patient_id: {patient_id}")
            response = table.query(**query_params)
            
            items = response.get('Items', [])
            
            # Check if we got any results
            if not items:
                return {
                    "statusCode": 404,
                    "body": json.dumps({
                        "message": "No reports found for the given patient.",
                        "patientId": patient_id
                    }),
                }

            logger.info(f"Successfully retrieved reports for patient: {patient_id}")
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps({
                    "message": "Reports retrieved successfully",
                    "patientId": patient_id,
                    "reports": items
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
        logger.error(f"Error in getReportsByPatientId: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Error processing request",
                "error": str(e)
            }),
        }
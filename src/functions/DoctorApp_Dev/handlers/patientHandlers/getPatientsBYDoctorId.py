import json
import logging
from utils.dynamo_utils import DynamoDBTable
from config.constants import PATIENT_TABLE
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def getPatientsBYDoctorId(event, context):
    try:
        logger.info("Starting getPatientsBYDoctorId request")
        
        # Extract doctorId from path parameters
        doctor_id = event.get('pathParameters', {}).get('doctorId')
        
        if not doctor_id:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Doctor ID is required."}),
            }

        # Initialize DynamoDB table
        table = DynamoDBTable(PATIENT_TABLE)
        
        # Query parameters
        query_params = {
            'IndexName': 'doctorId-index',
            'KeyConditionExpression': Key('doctorId').eq(doctor_id),
            # 'Limit': 20
        }

        try:
            logger.info(f"Querying DynamoDB for doctor_id: {doctor_id}")
            response = table.query(**query_params)
            
            items = response.get('Items', [])
            
            # # Check if we got any results
            # if not items:
            #     return {
            #         "statusCode": 404,
            #         "body": json.dumps({
            #             "message": "No patients found for this doctor.",
            #             "doctorId": doctor_id
            #         }),
            #     }

            logger.info(f"Successfully retrieved {len(items)} patients")
            return {
                "statusCode": 200,
                 "headers": {
                "Access-Control-Allow-Origin": "*",  
            },
                "body": json.dumps({
                    "message": "Patients retrieved successfully",
                    "doctorId": doctor_id,
                    "patients": items,
                    "count": len(items),
                    "hasMore": 'LastEvaluatedKey' in response
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
        logger.error(f"Error in getPatientsBYDoctorId: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Error processing request",
                "error": str(e)
            }),
        }

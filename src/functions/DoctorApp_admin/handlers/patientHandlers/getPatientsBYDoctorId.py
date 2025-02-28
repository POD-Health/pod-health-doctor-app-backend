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
        # Extract query string parameters
        query_string_parameters = event.get('queryStringParameters', {}) or {}
        sort_key = query_string_parameters.get('sortKey', 'name')
        sort_order = query_string_parameters.get('sortOrder', 'asc')

        # GSI Indexes
        index_mapping = {
            'name': 'doctorId-name-index',
            'latestReportDate': 'doctorId-latestReportDate-index',
        }

        # getting the index name
        index_name = index_mapping[sort_key]
        
        # To determine if the sort order is ascending or descending
        if sort_order == 'asc':
            scan_index_forward = True
        elif sort_order == 'desc':
            scan_index_forward = False
        
        
        logger.info(f"Sorting by {sort_key} in descending order")

        # Initialize DynamoDB table
        table = DynamoDBTable(PATIENT_TABLE)
        
        query_params = {
            'IndexName': index_name,
            'KeyConditionExpression': Key('doctorId').eq(doctor_id),
            'ScanIndexForward': scan_index_forward,
        }

        try:
            logger.info(f"Querying DynamoDB for doctor_id: {doctor_id}")
            response = table.query(**query_params)
            
            items = response.get('Items', [])

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
                    "hasMore": 'LastEvaluatedKey' in response,
                    "usedIndex": index_name,
                    "sortKey": sort_key,
                    "sortOrder": sort_order
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

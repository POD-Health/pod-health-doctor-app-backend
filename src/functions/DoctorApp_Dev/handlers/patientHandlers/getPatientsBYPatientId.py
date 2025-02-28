import json
import logging
from utils.dynamo_utils import DynamoDBTable
from config.constants import PATIENT_TABLE
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def getPatientsBYPatientId(event, context):
    """
    Retrieve patient details by patient ID
    """
    try:
        logger.info("Starting getPatientsBYPatientId request")
        
        # Extract patientId from path parameters
        patient_id = event.get('pathParameters', {}).get('patientId')
        
        if not patient_id:
            logger.error("Patient ID missing in request")
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "Patient ID is required"
                })
            }
            
        # Initialize DynamoDB table
        table = DynamoDBTable(PATIENT_TABLE)
        
        try:
            # Get patient record
            response = table.get_item({
                "patientId": patient_id
            })
            
            patient = response.get('Item')
            
            if not patient:
                logger.info(f"No patient found with ID: {patient_id}")
                return {
                    "statusCode": 404,
                    "body": json.dumps({
                        "message": f"Patient with ID {patient_id} not found"
                    })
                }
            
            logger.info(f"Successfully retrieved patient data for ID: {patient_id}")
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "patient": patient
                })
            }
            
        except ClientError as e:
            error_message = e.response['Error']['Message']
            logger.error(f"DynamoDB error: {error_message}")
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "message": "Failed to retrieve patient data",
                    "error": error_message
                })
            }
            
    except Exception as e:
        logger.error(f"Unexpected error in getPatientsBYPatientId: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Internal server error",
                "error": str(e)
            })
        }
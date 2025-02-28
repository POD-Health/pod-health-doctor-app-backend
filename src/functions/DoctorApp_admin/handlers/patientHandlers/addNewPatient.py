import json
import uuid
import logging
from utils.dynamo_utils import DynamoDBTable
from config.constants import PATIENT_TABLE
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def addNewPatient(event, context):
    try:
        logger.info("Processing addNewPatient request")
        
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        if not body:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Invalid request body."}),
            }

        # Validate required fields
        required_fields = ['doctorId', 'name', 'dateOfBirth', 'email', 'gender']
        missing_fields = [field for field in required_fields if field not in body]
        
        if missing_fields:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "Missing required fields",
                    "fields": missing_fields
                }),
            }

        # Assign a unique patientId if not provided
        if 'patientId' not in body or not body['patientId']:
            body['patientId'] = str(uuid.uuid4())
            body['createdAt'] = datetime.utcnow().isoformat()
            body['updatedAt'] = datetime.utcnow().isoformat()

        # Save to DynamoDB using the utility class
        table = DynamoDBTable(PATIENT_TABLE)
        table.put_item(body)

        logger.info(f"Patient added successfully: {body['patientId']}")
        return {
            "statusCode": 201,
             "headers": {
                "Access-Control-Allow-Origin": "*",  
            },
            "body": json.dumps({
                "message": "Patient created successfully",
                "patient": body
            }),
        }

    except Exception as e:
        logger.error(f"Error in addNewPatient: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Error processing request",
                "error": str(e)
            }),
        }
import json
import boto3
import uuid
from botocore.exceptions import ClientError
import logging

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('doctorApp_patients')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def addNewPatient(event):
    try:
        body = json.loads(event['body'])
        
        required_fields = ['doctorId', 'name', 'address', 'dateOfBirth', 'email', 'gender']
        if not all(field in body for field in required_fields):
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Bad Request: Missing required fields"})
            }

        patientId = body.get('patientId', str(uuid.uuid4()))

        patient_item = {
            'patientId': patientId,
            'doctorId': body['doctorId'],
            'name': body['name'],
            'address': body['address'],
            'dateOfBirth': body['dateOfBirth'],
            'email': body['email'],
            'gender': body['gender'],
        }

        table.put_item(Item=patient_item)

        return {
            "statusCode": 201,
            "body": json.dumps({
                "message": "Patient created successfully",
                "patient": patient_item
            })
        }
    except ClientError as e:
        logger.error(f"Error inserting patient into DynamoDB: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Internal Server Error", "error": str(e)})
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Internal Server Error", "error": str(e)})
        }

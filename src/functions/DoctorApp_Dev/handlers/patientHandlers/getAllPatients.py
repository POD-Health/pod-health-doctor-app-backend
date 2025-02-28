import json
import boto3
import logging

# Set up DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('doctorApp_patients')

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def getAllPatients(event):
    try:
        # Scan DynamoDB table to retrieve all patients
        response = table.scan()
        patients = response.get('Items', [])

        if not patients:
            return {
                "statusCode": 404,
                "body": json.dumps({"message": "No patients found"})
            }

        return {
            "statusCode": 200,
            "body": json.dumps(patients)
        }

    except Exception as e:
        logger.error(f"Error retrieving patients: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Internal Server Error", "error": str(e)})
        }

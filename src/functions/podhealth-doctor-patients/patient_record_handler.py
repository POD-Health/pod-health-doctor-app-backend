import boto3
import json
import logging
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('DoctorAppPatients')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def add_patient_record(event):
    try:
        body = json.loads(event['body'])
        logger.info(f"Adding patient record for patientId: {body['patientId']}")
        
        # Create base item with required fields
        item = {
            'doctorId': body['doctorId'],
            'patientId': body['patientId'],
            'name': body['name'],
            'email': body['email'],
            'dateOfBirth': body['dateOfBirth'],
            'gender': body['gender']
        }
        
        # Add optional fields if they exist
        optional_fields = ['avatar', 'address', 'reports', 'sessions']
        for field in optional_fields:
            if field in body and body[field] is not None:
                item[field] = body[field]
        
        # Store in DynamoDB
        table.put_item(Item=item)
        logger.info(f"Successfully added record for patientId: {body['patientId']}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({
                'message': 'Record added successfully',
                'patient_id': body['patientId']
            })
        }
    except KeyError as ke:
        logger.error(f"Missing required field: {str(ke)}")
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps(f'Missing required field: {str(ke)}')
        }
    except Exception as e:
        logger.error(f"Error adding patient record: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps(f'Error: {str(e)}')
        }

def fetch_patient_records(event):
    try:
        doctorId = event.get('queryStringParameters', {}).get('doctorId')
        logger.info(f"Fetching patient records for doctorId: {doctorId}")
        
        if not doctorId:
            logger.error("Missing doctorId in query parameters")
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                },
                'body': json.dumps('Missing doctorId in query parameters')
            }
        
        response = table.query(
            KeyConditionExpression=Key('doctorId').eq(doctorId)
        )
        
        # Return all fields for each patient
        records = []
        for item in response['Items']:
            patient_record = {
                'id': item['patientId'],
                'name': item['name'],
                'email': item['email'],
                'dateofbirth': item['dateOfBirth'],
                'gender': item['gender']
            }
            
            # Add optional fields if they exist
            optional_fields = ['avatar', 'address', 'reports', 'sessions']
            for field in optional_fields:
                if field in item:
                    patient_record[field] = item[field]
            
            records.append(patient_record)
        
        logger.info(f"Successfully fetched {len(records)} patient records for doctorId: {doctorId}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps(records)
        }
    except Exception as e:
        logger.error(f"Error fetching patient records: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps(f'Error: {str(e)}')
        }

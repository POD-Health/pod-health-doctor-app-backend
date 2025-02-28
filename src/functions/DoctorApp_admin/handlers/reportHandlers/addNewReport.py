import json
import uuid
import logging
from datetime import datetime
from utils.dynamo_utils import DynamoDBTable
from config.constants import REPORT_TABLE
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def addNewReport(event, context):
    """
    Add a new medical report with audio transcription and summary,
    allowing partial saves in case of failure at any step.
    """
    try:
        logger.info("Processing addNewReport request")
        
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        if not body:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Invalid request body"})
            }
        
        # Validate required fields
        required_fields = ['audioFile', 'patientId', 'doctorId']
        missing_fields = [field for field in required_fields if field not in body]
        if missing_fields:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "Missing required fields",
                    "fields": missing_fields
                })
            }
        
        # Generate unique report ID
        report_id = str(uuid.uuid4())
        
        # Prepare report data with initial status
        report_data = {
            'reportId': report_id,
            'patientId': body['patientId'],
            'doctorId': body['doctorId'],
            'audioFile': body['audioFile'],
            'transcription': body.get('transcription', ''),
            'reportData': body.get('reportData', ''),
            'additionalNotes': body.get('additionalNotes', ''),
            'reportDate': body.get('reportDate', datetime.utcnow().isoformat()),
            'reportType': body.get('reportType', 'Unknown'),
            'billingData': body.get('billingData', {}),
            'currentStatus': 'Pending',  # Initial status
            'createdAt': datetime.utcnow().isoformat(),
            'updatedAt': datetime.utcnow().isoformat()
        }
        
        # Determine report status based on required processing fields
        if not body.get('transcription'):
            report_data['currentStatus'] = 'Awaiting Transcription'
        elif not body.get('reportData'):
            report_data['currentStatus'] = 'Awaiting Report Data'
        elif not body.get('billingData'):
            report_data['currentStatus'] = 'failed'
        else:
            report_data['currentStatus'] = 'Complete'
        
        # Save to DynamoDB
        table = DynamoDBTable(REPORT_TABLE)
        table.put_item(report_data)
        
        logger.info(f"Report added successfully: {report_id}")

        patient_data = {
            'patientId': report_data['patientId'],
            'doctorId': report_data['doctorId'],
            'latestReportId': report_data['reportId'],
            'latestReportDate': report_data['createdAt']
        }
        
        # update the Latest Report details to patient table 
        updatePatientLatestReport(patient_data)
        
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({
                "message": "Report saved successfully",
                "report": report_data
            })
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in request body: {str(e)}")
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Invalid JSON in request body",
                "error": str(e)
            })
        }
    except Exception as e:
        logger.error(f"Error in addNewReport: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Error processing request",
                "error": str(e)
            })
        }

def updatePatientLatestReport(report_data):
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('doctorApp_patients')
        
        print('updatePatientLatestReport:',report_data)
        
        # Prepare the update expression and attribute values
        update_expression = "SET latestReportId = :rid, latestReportDate = :rdate"
        expression_attribute_values = {
            ':rid': report_data['latestReportId'],
            ':rdate': report_data['latestReportDate']
        }
        
        # Perform the update operation
        response = table.update_item(
            Key={
                'patientId': report_data['patientId'],
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="UPDATED_NEW"
        )

        print('updatePatientLatestReport:response:', response)
        
        return {
            'statusCode': 200,
            'body': 'Patient data updated successfully',
            'updatedAttributes': response['Attributes']
        }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': f"Error updating patient data: {str(e)}"
        }

    


    
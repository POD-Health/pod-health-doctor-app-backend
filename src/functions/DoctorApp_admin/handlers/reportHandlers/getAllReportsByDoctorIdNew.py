import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
report_table = dynamodb.Table('DoctorApp_Reports')
patient_table = dynamodb.Table('doctorApp_patients')

def getAllReportsByDoctorIdNew(event, context):
    try:
        # Extract doctorId from path parameters
        doctor_id = event.get('pathParameters', {}).get('doctorId')

        if not doctor_id:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Doctor ID is required."}),
            }

        page_size = int(event.get('pageSize', 1000))  # Default page size
        last_evaluated_key = event.get('lastEvaluatedKey')

        # Step 1: Query DoctorApp_Reports using GSI (doctorId, reportDate) - Sorted data
        report_query_params = {
            'IndexName': 'doctorId-reportDate-index',  # Ensure GSI exists
            'KeyConditionExpression': Key('doctorId').eq(doctor_id),
            'FilterExpression': Key('currentStatus').eq('Complete'),
            'Limit': page_size,
            'ScanIndexForward': False  # Retrieves latest reports first
        }
        if last_evaluated_key:
            report_query_params['ExclusiveStartKey'] = last_evaluated_key

        report_response = report_table.query(**report_query_params)
        reports = report_response.get('Items', [])

        if not reports:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'patientReports': [],
                    'count': 0,
                    'hasMore': False
                })
            }

        # Step 2: Fetch unique patient details using BatchGetItem
        patient_ids = list({report['patientId'] for report in reports})
        patient_data_map = {}

        if patient_ids:
            batch_keys = {'doctorApp_patients': {'Keys': [{'patientId': pid} for pid in patient_ids]}}
            patient_response = dynamodb.batch_get_item(RequestItems=batch_keys)

            for patient in patient_response.get('Responses', {}).get('doctorApp_patients', []):
                patient_data_map[patient['patientId']] = {
                    'patientId': patient.get('patientId'),
                    'name': patient.get('name'),
                    'gender': patient.get('gender'),
                    'dateOfBirth': patient.get('dateOfBirth'),
                    'email': patient.get('email'),
                }

        # Step 3: Merge report and patient data
        patient_reports = []
        for report in reports:
            patient_info = patient_data_map.get(report['patientId'], {})
            combined_record = {
                **patient_info,
                'reportId': report.get('reportId'),
                'currentStatus': report.get('currentStatus'),
                'reportType': report.get('reportType'),
                'updatedAt': report.get('updatedAt'),
                'reportDate': report.get('reportDate')
            }
            patient_reports.append(combined_record)

        # Step 4: Construct response with pagination
        response = {
            'patientReports': patient_reports,
            'count': len(patient_reports),
            'hasMore': 'LastEvaluatedKey' in report_response,
        }

        if 'LastEvaluatedKey' in report_response:
            response['lastEvaluatedKey'] = report_response['LastEvaluatedKey']

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True
            },
            'body': json.dumps(response)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True
            },
            'body': json.dumps({'message': f'Internal server error: {str(e)}'})
        }

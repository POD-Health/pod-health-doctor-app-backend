import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from collections import defaultdict
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
patient_table = dynamodb.Table('doctorApp_patients')
report_table = dynamodb.Table('DoctorApp_Reports')

def getAllReportsByDoctorId(event, context):
    try:
        # Extract doctorId from path parameters
        doctor_id = event.get('pathParameters', {}).get('doctorId')
        
        if not doctor_id:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Doctor ID is required."}),
            }

        page_size = event.get('pageSize', 1000)
        last_evaluated_key = event.get('lastEvaluatedKey', None)
        
        # 1. Get all patients for the doctor in one query
        patient_query_params = {
            'IndexName': 'doctorId-index',
            'KeyConditionExpression': Key('doctorId').eq(doctor_id),
            # 'Limit': page_size
        }
        if last_evaluated_key:
            patient_query_params['ExclusiveStartKey'] = last_evaluated_key
            
        patient_response = patient_table.query(**patient_query_params)
        patients = patient_response['Items']
        
        if not patients:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'patientReports': [],
                    'count': 0,
                    # 'pageSize': page_size,
                    'hasMore': False
                })
            }

        # 2. Create a mapping of patient data
        patient_map = {
            patient['patientId']: {
                'doctorId': patient.get('doctorId'),
                'patientId': patient.get('patientId'),
                'dateOfBirth': patient.get('dateOfBirth'),
                'email': patient.get('email'),
                'name': patient.get('name'),
                'gender': patient.get('gender')
            } for patient in patients
        }

        # 3. Batch get reports for all patients using parallel queries
        patient_reports = []
        patient_ids = list(patient_map.keys())
        
        # Using BatchGet to fetch reports in parallel
        def get_reports_batch(patient_ids_batch):
            response = report_table.query(
                IndexName='patientId-index',
                KeyConditionExpression=Key('patientId').eq(patient_ids_batch),
                FilterExpression=Attr('currentStatus').eq('Complete')
            )
            return response.get('Items', [])

        # Process reports in batches of 10 (DynamoDB recommendation)
        batch_size = 10
        all_reports = []
        for i in range(0, len(patient_ids), batch_size):
            batch = patient_ids[i:i + batch_size]
            for patient_id in batch:
                reports = get_reports_batch(patient_id)
                all_reports.extend(reports)

        # 4. Combine patient and report data
        for report in all_reports:
            patient_id = report.get('patientId')
            if patient_id in patient_map:
                patient_data = patient_map[patient_id]
                combined_record = {
                    **patient_data,
                    'reportId': report.get('reportId'),
                    'currentStatus': report.get('currentStatus'),
                    'reportType': report.get('reportType'),
                    'updatedAt': report.get('updatedAt'),
                    'reportDate': report.get('reportDate')
                }
                patient_reports.append(combined_record)

        # Sort the patient_reports by reportDate in descending order (latest first)
        sorted_patient_reports = sorted(
            patient_reports,
            key=lambda x: datetime.strptime(x['reportDate'], '%Y-%m-%dT%H:%M:%S.%fZ'),
            reverse=True
        )

        response = {
            'patientReports': sorted_patient_reports,
            'pageSize': page_size,
            'count': len(sorted_patient_reports)
        }

        if 'LastEvaluatedKey' in patient_response:
            response['lastEvaluatedKey'] = patient_response['LastEvaluatedKey']
            response['hasMore'] = True
        else:
            response['hasMore'] = False

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
            'body': json.dumps({
                'message': f'Internal server error: {str(e)}'
            })
        }

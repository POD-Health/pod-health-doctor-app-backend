import json

def generate_response(status_code, body, headers=None):
    headers = headers or {}
    headers.update({
        "Content-Type": "application/json"
    })
    return {
        'statusCode': status_code,
        'body': json.dumps(body),
        'headers': headers,
    }
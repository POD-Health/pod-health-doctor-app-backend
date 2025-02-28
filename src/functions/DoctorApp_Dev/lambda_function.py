import json
import logging
from handlers.userHandlers.getUserByEmail import getUserByEmail
from handlers.patientHandlers.addNewPatient import addNewPatient
from handlers.patientHandlers.getPatientsBYDoctorId import getPatientsBYDoctorId
from handlers.patientHandlers.getPatientsBYPatientId import getPatientsBYPatientId
from handlers.reportHandlers.addNewReport import addNewReport
from handlers.reportHandlers.getReportById import getReportById
from handlers.reportHandlers.getReportsByPatientId import getReportsByPatientId
from handlers.userHandlers.addUser import addUser
from handlers.templateHandlers.getAlltemplates import getAlltemplates

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Define route handlers
route_handlers = {
    "/user/{emailid}": {
        "GET": getUserByEmail
    },
    "/patients": {
        "POST": addNewPatient
    },
    "/patients/{doctorId}": {
        "GET": getPatientsBYDoctorId
    },
    "/patient/{patientId}": {
        "GET": getPatientsBYPatientId
    },
    "/reports": {
        "POST": addNewReport
    },
    "/reports/{reportId}": {
        "GET": getReportById
    },
     "/patient/{patientId}/reports": {
        "GET": getReportsByPatientId
    },
    "/templates": {
        "GET": getAlltemplates
    },
}

def lambda_handler(event, context):
    """
    Main Lambda handler function that processes incoming events
    
    Args:
        event (dict): The incoming event data
        context (object): Lambda context object
    
    Returns:
        dict: Response containing statusCode and body
    """
    logger.info(f"Received event: {json.dumps(event)}")

    # Handle Cognito trigger events
    if event.get('triggerSource') == 'PostConfirmation_ConfirmSignUp':
        try:
            # Extract user email from Cognito event
            user_email = event['request']['userAttributes']['email']
            
            # Add user to database
            add_user_response = addUser(user_email, event)
            return add_user_response

        except Exception as e:
            logger.error(f"Error processing user sign-up: {e}")
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "message": "Failed to add user after sign-up."
                })
            }

    # Handle API Gateway events
    resource = event.get('resource')
    method = event.get('httpMethod')

    # Validate request
    if not resource or not method:
        logger.error("Invalid request: Missing resource or method.")
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Invalid request. Resource or method missing."
            })
        }

    # Get appropriate handler
    handlers = route_handlers.get(resource, {})
    handler = handlers.get(method)

    # Execute handler if found
    if handler:
        try:
            return handler(event, context)
        except Exception as e:
            logger.error(f"Handler error: {e}")
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "message": "Internal server error."
                })
            }

    # Handle route not found
    logger.warning(f"No route found for resource: {resource}, method: {method}")
    return {
        "statusCode": 404,
        "body": json.dumps({
            "message": "Route not found"
        })
    }

import json
import logging
from handlers.userHandlers.addUser import addUser
from handlers.userHandlers.getUser import getUser
from handlers.patientHandlers.addNewPatient import addNewPatient
from handlers.patientHandlers.getAllPatients import getAllPatients

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Define route handlers
route_handlers = {
    "/user/{emailId}": {"GET": getUser},
    "/user": {"POST": addUser},
    "/patients": {"GET": getAllPatients},
    "/patients/addpatient": {"POST": addNewPatient},
}

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")

    resource = event.get('resource')
    method = event.get('httpMethod')

    if not resource or not method:
        logger.error("Invalid request: Missing resource or method.")
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Invalid request. Resource or method missing."}),
        }

    handlers = route_handlers.get(resource, {})
    handler = handlers.get(method)

    if handler:
        try:
            return handler(event, context)
        except Exception as e:
            logger.error(f"Handler error: {e}")
            return {
                "statusCode": 500,
                "body": json.dumps({"message": "Internal server error."}),
            }

    logger.warning(f"No route found for resource: {resource}, method: {method}")
    return {
        "statusCode": 404,
        "body": json.dumps({"message": "Route not found"}),
    }

def getUser(event, context):
    try:
        # Parse the request body
        body = json.loads(event.get("body", "{}"))
        email = body.get("email")

        # Validate email input
        if not email:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Email is required in the request body"})
            }
        
        # Log the request
        logger.info(f"Fetching user with email: {email}")
        
        # Query DynamoDB with the correct key
        response = table.get_item(Key={"email": email})
        user_data = response.get("Item")

        # Handle if user data is not found
        if not user_data:
            return {
                "statusCode": 404,
                "body": json.dumps({"message": f"User with email {email} not found"})
            }
        
        # Successfully retrieved user data
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "User retrieved successfully", "data": user_data})
        }

    except Exception as e:
        logger.error(f"Error retrieving user: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "An error occurred", "error": str(e)})
        }

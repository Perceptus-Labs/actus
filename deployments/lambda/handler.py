"""
AWS Lambda handler for V-JEPA-2 API.
"""

import os
import json
import logging
from mangum import Mangum
from main import app

# Configure logging for Lambda
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Mangum handler for FastAPI
handler = Mangum(app, lifespan="off")


def lambda_handler(event, context):
    """
    AWS Lambda handler function.

    Args:
        event: Lambda event
        context: Lambda context

    Returns:
        API Gateway response
    """
    try:
        logger.info(f"Lambda event: {json.dumps(event)}")

        # Handle the request through Mangum
        response = handler(event, context)

        logger.info(f"Lambda response status: {response.get('statusCode', 'unknown')}")
        return response

    except Exception as e:
        logger.error(f"Lambda handler error: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
            },
            "body": json.dumps({"error": "Internal server error", "detail": str(e)}),
        }

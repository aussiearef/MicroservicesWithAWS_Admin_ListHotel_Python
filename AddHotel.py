import json
import os
from typing import Dict
from http import HTTPStatus

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from jose import jwt
from jose.exceptions import JWTError
from aws_lambda_powertools import Logger
from aws_lambda_powertools.logging import log_level
from aws_lambda_powertools.tracing import Tracer
from pydantic import BaseModel

logger = Logger()
tracer = Tracer()


class Hotel(BaseModel):
    userId: str
    Id: str
    Name: str
    Price: int
    Rating: int
    CityName: str
    FileName: str

    class Config:
        orm_mode = True


def get_secret(secret_name: str, region_name: str = "us-east-1") -> Dict[str, str]:
    """Get secret from AWS Secrets Manager"""
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name="secretsmanager",
        region_name=region_name
    )

    # Get the secret value
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        logger.exception(e)
        raise e

    secret = json.loads(get_secret_value_response["SecretString"])
    return secret


def list_hotels(event, context):
    """List all hotels for a given user"""
    try:
        # Parse query string parameters
        query_params = event.get("queryStringParameters", {})
        token = query_params.get("token", "")
        if not token:
            raise ValueError("Query parameter 'token' not present.")

        # Decode JWT token and extract user ID
        secret = get_secret("my-secret")
        decoded_token = jwt.decode(token, secret["jwt_secret"], algorithms=[secret["jwt_algorithm"]])
        user_id = decoded_token.get("sub", "")

        # Connect to DynamoDB and retrieve hotels for the user
        dynamodb = boto3.resource("dynamodb")
        table_name = os.environ.get("HOTEL_TABLE_NAME")
        table = dynamodb.Table(table_name)
        hotels = table.query(
            KeyConditionExpression=Key("userId").eq(user_id)
        )["Items"]

        # Serialize response body
        hotels_data = [Hotel(**hotel).dict() for hotel in hotels]
        response_body = {"Hotels": hotels_data}

        # Construct APIGatewayProxyResponse object
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "OPTIONS,GET",
            "Content-Type": "application/json",
        }
        response = {
            "statusCode": HTTPStatus.OK,
            "headers": headers,
            "body": json.dumps(response_body),
        }

    except (JWTError, ValueError, ClientError) as e:
        logger.exception(e)
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "OPTIONS,GET",
            "Content-Type": "application/json",
        }
        response = {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "headers": headers,
            "body": json.dumps({"Error": str(e)}),
        }

    return response

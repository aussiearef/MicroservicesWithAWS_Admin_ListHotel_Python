import json
import os
import boto3
import jwt # pyJwt
from http import HTTPStatus
from typing import Any, Dict, List
from boto3.dynamodb.conditions import Key
from dynamodb_json import json_util as ddb_json

def main():
    token="< put id token here>"
    print(list_hotels(token))

def handler(event, context):
    token = event["queryStringParamets"]["token"]
    return list_hotels(token)

def list_hotels(token:str):
    response = {
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "OPTIONS, GET"
        },
        "statusCode": HTTPStatus.OK,
    }    

    if not token:
        response["statusCode"] = HTTPStatus.BAD_REQUEST
        response["body"] = json.dumps({"Error":"Query string parameter 'event' is missing"})
        return response
    
    token_details = jwt.decode(token, options={"verify_signature":False})
    user_id = token_details.get("sub")

    region = os.environ.get("AWS_REGION")
    db_client = boto3.resource("dynamodb" , region_name = region)
    table = db_client.Table("Hotels")

    response = table.scan(
        FilterExpression = Key("userId").eq(user_id)
    )

    hotels = ddb_json.loads(response["Items"])

    response["body"] = json.dumps({"Hotels": hotels})

    return response

if __name__=="__main__":
    main()

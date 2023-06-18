import json
import os
import boto3
import jwt # pyJwt
from http import HTTPStatus
from typing import Any, Dict, List
from boto3.dynamodb.conditions import Key
from dynamodb_json import json_util as ddb_json

def main():
    token="eyJraWQiOiJYYlpCd1dOd3MzNEJ3NEF0dEdqSzJnTzQ0WGsxN2grY2Y3WGJWTVR6Z0k4PSIsImFsZyI6IlJTMjU2In0.eyJhdF9oYXNoIjoiaXJjYlpkcGFwVnJZeVBNbUwzZlk2dyIsInN1YiI6ImVmYjA4M2I3LTZlNWQtNGEwMy1hNGEwLTYyNDRjMmI0YThkYSIsImNvZ25pdG86Z3JvdXBzIjpbIkFkbWluIl0sImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJhZGRyZXNzIjp7ImZvcm1hdHRlZCI6Ik15IGhvbWUifSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLmFwLXNvdXRoZWFzdC0yLmFtYXpvbmF3cy5jb21cL2FwLXNvdXRoZWFzdC0yXzJEbTBKdlNiTCIsImNvZ25pdG86dXNlcm5hbWUiOiJlZmIwODNiNy02ZTVkLTRhMDMtYTRhMC02MjQ0YzJiNGE4ZGEiLCJnaXZlbl9uYW1lIjoiSm9uIiwiYXVkIjoiMTA0cTV0OXQ5bW9qMDJnYTZ1ZmkzOWo2Y3QiLCJldmVudF9pZCI6ImEyODE4OGI5LTgxNWQtNGZhZC04ZmQ5LTFhNjZkNzQ4MjRkOCIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNjg3MDQ2OTAyLCJleHAiOjE2ODcwNTA1MDIsImlhdCI6MTY4NzA0NjkwMiwiZmFtaWx5X25hbWUiOiJEb2UiLCJqdGkiOiJmZTJmNTg1YS1iOGQxLTQxZjYtYTJhYS1jODY0OWYyZDRhNTEiLCJlbWFpbCI6ImFkbWluQG15ZG9tYWluLmNvbSJ9.MKAHWFr5nSCyE1EEmbLGTGtM3crynUow2pef5oU_zhylhWSTucOW5fKznpbfaThcAdG0qL1hNWhAUKAfXugr205Y1ucH0VvVSsLUGu1EmtkxtcVjzk0EFU9QKscNOkF1_xrX8krZGw9pEjwhB7JacaoYXiyZkuUzepo9xjNtdWJREo_52PrAjMvzSnL9_-RhyKx4RDMTCN4X_ecvcwW7s1Zk6MmRPcrmvLq9WgyGU4ChPzcu3L-1OaQ-wgb6ESgwF8h1VToHKWdFL5dnzqG_U4Q6PbktJ_MIgAeXXCJlyG_i3F1-90K-kWJ5uPcWGqR2IxjWWRSCmEyoNP_pCAYoKw"
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
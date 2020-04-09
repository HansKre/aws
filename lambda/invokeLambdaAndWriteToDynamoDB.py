import json
from decimal import Decimal
import boto3

# https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GettingStarted.Python.03.html
# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if abs(o) % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

def lambda_handler(event, context):
    # https://stackoverflow.com/questions/39456309/using-boto-to-invoke-lambda-functions-how-do-i-do-so-asynchronously
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html#Lambda.Client.invoke
    lambdaClient = boto3.client('lambda')
    
    response = lambdaClient.invoke(
        FunctionName = "immoScoutStats",
        InvocationType = 'RequestResponse'
    )
    
    # response from lambda invoked through boto3 is of type StreamingBody
    # thus, we need to convert before consuming
    # https://gist.github.com/pgolding/9083a6f3590067e3ffe694c947ef90a3
    # as a reference, from a web-request, we would it like this:
    # itemsToStore = json.loads(response['body'])
    
    responseAsJson = json.loads(response['Payload'].read().decode("utf-8"))
    itemsToStore = json.loads(responseAsJson['body'])
    
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    table = dynamodb.Table('ImmoScout24')
    
    statusCodes = []
    for item in itemsToStore:
        response = table.put_item(
            Item={
                'date': item['date'],
                'districtName': item['districtName'],
                "countApartmentBuy": item['countApartmentBuy'],
                "countApartmentRent": item['countApartmentRent'],
                "total": item['total'],
                "ratioBuy": Decimal(str(item['ratioBuy']))
            }
        )
        statusCodes.append(response['ResponseMetadata']['HTTPStatusCode'])
        # https://github.com/boto/boto3/issues/665
    
    # https://docs.python.org/3/library/json.html
    return {
        'statusCode': 200,
        'body': json.dumps(statusCodes, indent=4, cls=DecimalEncoder)
    }

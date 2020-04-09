import json
import decimal
import boto3
import csv

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

csvFileName = '/tmp/output.csv'
def createCsv(entries):
    createIfNotExisting = 'w'
    with open(csvFileName, createIfNotExisting, newline='\n') as csvFile:
        fieldnames = ['total', 'ratioBuy', 'countApartmentRent', 'date', 'countApartmentBuy', 'districtName']
        writer = csv.DictWriter(csvFile, fieldnames=fieldnames)
        writer.writeheader()
        for entry in entries:
            writer.writerow(entry)

def appendEntries(entries, response):
    returnValue = entries;
    for item in response['Items']:
        # convert string to int
        item['countApartmentBuy'] = int(item['countApartmentBuy'])
        item['countApartmentRent'] = int(item['countApartmentRent'])
        returnValue.append(item)
    return returnValue

def lambda_handler(event, context):
    
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    table = dynamodb.Table('ImmoScout24')
    
    # https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GettingStarted.Python.04.html
    # The scan method returns a subset of the items each time, called a page.
    # The LastEvaluatedKey value in the response is then passed to the scan
    # method via the ExclusiveStartKey parameter. When the last page is returned,
    # LastEvaluatedKey is not part of the response.
    entries = []
    # get the first page
    response = table.scan()
    entries = appendEntries(entries, response)
    
    # get all the subsequent pages
    while 'LastEvaluatedKey' in response:
        response = table.scan(
            ExclusiveStartKey=response['LastEvaluatedKey']
        )
        entries = appendEntries(entries, response)
    
    createCsv(entries)
    s3_client = boto3.client('s3')
    bucket = 'immoscout24-hans'
    outFileName = 'lambda-out/immoscoutstats.csv'
    s3_client.upload_file(csvFileName, bucket, outFileName)
    
    # create custom response body to avoid sending response['Items']
    body = []
    body.append({'Count':response['Count']})
    body.append({'ScannedCount':response['ScannedCount']})
    body.append({'ResponseMetadata':response['ResponseMetadata']})
    return {
        'statusCode': response['ResponseMetadata']['HTTPStatusCode'],
        'body': body
    }

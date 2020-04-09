import json
import datetime
from requests_oauthlib import OAuth1Session
import boto3

def getCredentials():
    try:
        ssm = boto3.client('ssm')

        parameter = ssm.get_parameter(Name='CONSUMER_KEY_IMMOSCOUT24_API', WithDecryption=True)
        CONSUMER_KEY = parameter['Parameter']['Value']

        parameter = ssm.get_parameter(Name='CONSUMER_SECRET_IMMOSCOUT24_API', WithDecryption=True)
        CONSUMER_SECRET = parameter['Parameter']['Value']
        
        if not CONSUMER_KEY:
            raise ValueError("CONSUMER_KEY cannot be empty.")
            
        if not CONSUMER_SECRET:
            raise ValueError("CONSUMER_SECRET cannot be empty.")
            
        return {
            'CONSUMER_KEY': CONSUMER_KEY,
            'CONSUMER_SECRET': CONSUMER_SECRET
        }
    except ValueError as err:
        print(err)

def getContent():  
    credentials = getCredentials()
    
    CONSUMER_KEY = credentials['CONSUMER_KEY']
    CONSUMER_SECRET = credentials['CONSUMER_SECRET']
    
    HOST = "rest.immobilienscout24.de"
    URI = "/restapi/api/search/v1.0/statistic?geocode=1276001039&realestatetypes=ApartmentBuy,ApartmentRent"
    URL = 'https://' + HOST + URI
    
    oauthRequest = OAuth1Session(CONSUMER_KEY,
                        client_secret=CONSUMER_SECRET)

    headers = {
            'Accept': "application/json",
            'Accept-Encoding': "gzip, deflate",
        }

    response = oauthRequest.get(URL, headers=headers)
    return response

def lambda_handler(event, context):
    
    response = getContent()
    
    if (response.status_code == 200):
        now = datetime.datetime.utcnow()
        now_s = now.strftime("%Y-%m-%d %H:%M:%S")

        jsonResponse = json.loads(response.content)
        jsonHierarchyElems = jsonResponse["common.geoHierarchyElementsStatistic"]["children"]["geoHierarchyElement"]
        
        returnValues = []
        
        for elem in jsonHierarchyElems:
            name = elem["name"]
            geoCodeId = elem["geoCodeId"]
            countApartmentBuy = elem["statistics"]["GeoHierarchyStatistic"][0]["@count"]
            countApartmentRent = elem["statistics"]["GeoHierarchyStatistic"][1]["@count"]
            total = int(countApartmentBuy) + int(countApartmentRent)
            
            if (total != 0):
                ratioBuy = round(int(countApartmentBuy) / total, 2)
            else:
                ratioBuy = 0

            returnValue = {
                'date': now_s,
                'districtName': name,
                'countApartmentBuy': countApartmentBuy,
                'countApartmentRent': countApartmentRent,
                'total': total,
                'ratioBuy': ratioBuy
            }

            returnValues.append(returnValue)
    
        #print(json.dumps(returnValues, indent = 4))
    
    else:
        raise ValueError("HTTP Status Code cannot be: " + response.status_code)
    
    return {
        'statusCode': response.status_code,
        'body': json.dumps(returnValues)
    }

import os
env = os.getenv('environment')
if (env == None):
    print(lambda_handler(1, 2))

import json
from lxml import html
import requests

finalResponse = ""

def getSearchUrl(currentAmazonPageNumber):
    return ('https://www.amazon.de/s?i=prime-instant-video&bbn=3279204031&rh=n%3A3279204031%2Cn%3A3010076031%2Cn%3A3015915031%2Cp_n_ways_to_watch%3A7448695031%2Cp_72%3A3289799031%2Cp_n_entity_type%3A9739119031&lo=list&dc&page='
            + str(currentAmazonPageNumber)
            + '&fst=as%3Aoff&qid=1564341535&rnid=9739118031&ref=sr_pg_4')
            
def scrape(tree):
    titleQuerySuffix = '/div/span/div/div/div[2]/div[2]/div/div[1]/div/div/div[1]/h2/a/span'
    # this Suffix retrieves the >first< director only: /div/span/div/div/div[2]/div[2]/div/div[2]/div[2]/div/div/ul/li[2]/span/a[1]
    # if we remove the [1] at the end, we can cycle through all the directors

    directorQuerySuffix = '/div/span/div/div/div[2]/div[2]/div/div[2]/div[2]/div/div/ul/li[2]/span/a'
    actorsQuerySuffix = '/div/span/div/div/div[2]/div[2]/div/div[2]/div[2]/div/div/ul/li[1]/span/a'

    # in case there are no actors or no director, the suffix is different
    directorActorsFallbackQuerySuffix = '/div/span/div/div/div[2]/div[2]/div/div[2]/div[2]/div/div/ul/li/span/a'

    movieCountOnPage = 1

    baseQuery = '//*[@id="search"]/div[1]/div[2]/div/span[4]/div[1]/div[' + str(movieCountOnPage) + ']'

    movieTitleElem = tree.xpath(baseQuery + titleQuerySuffix)
    directorElem = tree.xpath(baseQuery + directorQuerySuffix)
    actorsElem = tree.xpath(baseQuery + actorsQuerySuffix)
    
    finalResponse += (movieTitleElem[0].text + directorElem[0].text.strip() + "\l\r")

def lambda_handler(event, context):
    currentMovieOnPage = 1

    while currentMovieOnPage < 5:
        response = requests.get(
            getSearchUrl(currentMovieOnPage),
            headers={'Accept': 'text/html',
                     'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
                     'content-type': 'application/x-www-form-urlencoded',
                     'origin': 'https://www.amazon.de',
                     'sec-fetch-site': 'same-origin',
                     'sec-fetch-mode': 'cors',
                     'referer': 'https://www.amazon.de/s?i=prime-instant-video&bbn=3279204031&rh=n%3A3279204031%2Cn%3A3010076031%2Cn%3A3015915031%2Cp_n_ways_to_watch%3A7448695031%2Cp_72%3A3289799031%2Cp_n_entity_type%3A9739119031&lo=list&dc&fst=as%3Aoff&qid=1564341535&rnid=9739118031&ref=sr_pg_4',
                     'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7'
                    }
        )
        
        currentMovieOnPage += 1
        
        if response.status_code == 200:
            print('Success!')
            tree = html.fromstring(response.content)
            scrape(tree)
        elif response.status_code == 404:
            print('Not Found.')
        else:
            print (response.status_code)
            print (response.content)
    return {
        'statusCode': 200,
        'body': json.dumps('Result: ' + finalResponse)
    }

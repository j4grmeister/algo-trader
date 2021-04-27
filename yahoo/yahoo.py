import os
import requests

RAPID_API_KEY = os.environ['RAPID_API_KEY']
RAPID_API_HOST = os.environ['RAPID_API_HOST']

YAHOO_HEADERS = {'x-rapidapi-key': RAPID_API_KEY, 'x-rapidapi-host': RAPID_API_HOST}

def pull_movers(count=10):
    if count <= 0:
        print("ERROR! get_movers: count must be greater than 0")
        return
    elif count > 25:
        print("ERROR! get_movers: max count is 25")
        return
    response = requests.request(
        "GET",
        "https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/v2/get-movers",
        headers=YAHOO_HEADERS,
        params={
            "region":"US",
            "lang":"en-US",
            "count":"{0}".format(count),
            "start":"0"
        }
    )
    global yahoo_movers
    yahoo_movers = response['finance']['result']

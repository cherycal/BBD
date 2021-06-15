__author__ = 'chance'

import requests

#its bad practice to place your bearer token directly into the script (this is just done for illustration purposes)
BEARER_TOKEN = "pF84t0Xukgaaf4QL6khVTuBjsLBMdfH0ibuJSGa0CdUnr"

#define search twitter function
def search_twitter(query, tweet_fields, bearer_token = BEARER_TOKEN):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}

    url = "https://api.twitter.com/2/tweets/search/recent?query={}&{}".format(
        query, tweet_fields
    )
    response = requests.request("GET", url, headers=headers)

    print(response.status_code)

    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

#search term
query = "skateboarding dog"
#twitter fields to be returned by api call
tweet_fields = "tweet.fields=text,author_id,created_at"
search_twitter(query, tweet_fields)
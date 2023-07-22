__author__ = 'chance'
import json
import sys
from datetime import datetime
sys.path.append('../modules')
import sqldb
import push
import fantasy
from io import BytesIO
import certifi
import pycurl
import time
import requests

inst = push.Push()
bdb = sqldb.DB('Baseball.db')
fantasy = fantasy.Fantasy()

now = datetime.now()  # current date and time
date_time = now.strftime("%Y%m%d%H%M%S")
date8 = now.strftime("%Y%m%d")
statcast_date = now.strftime("%Y-%m-%d")
sleep_interval = 1
msg = ""
TIMEOUT = 10


def get_player_data_json_requests():
    # print_calling_function()
    leagueID = "6455"
    year = "2023"
    url_name = "http://fantasy.espn.com/apis/v3/games/flb/seasons/" + year + \
               "/segments/0/leagues/" + \
               str(leagueID) + "?view=kona_playercard"

    headers = {"authority": "fantasy.espn.com",
               "accept": "application/json",
               "x-fantasy-source": "kona",
               "x-fantasy-filter": '{"players":{"filterStatus":{"value":["FREEAGENT","WAIVERS","ONTEAM"]},"filterSlotIds":{"value":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]}}}'}

    print("sleeping ....")
    time.sleep(.5)

    r = requests.get(url_name, headers=headers, allow_redirects=True)
    json_data = json.loads(r.content)
    print(len(json_data['players']))
    #print(len(json.dumps(json_data,indent=2)))



def get_player_data_json():
    # print_calling_function()
    leagueID = "6455"
    year = "2023"
    url_name = "http://fantasy.espn.com/apis/v3/games/flb/seasons/" + year + \
               "/segments/0/leagues/" + \
               str(leagueID) + "?view=kona_playercard"
    headers = ['authority: fantasy.espn.com',
               'accept: application/json',
               'x-fantasy-source: kona',
               'x-fantasy-filter: {"players":{"filterStatus":{"value":["FREEAGENT","WAIVERS","ONTEAM"]},"filterSlotIds":{"value":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]}}}']
    # print("get_player_data_json: " + url_name)
    # self.logger_instance.debug(f'get_player_data_json: {url_name}')
    try:
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url_name)
        c.setopt(c.HTTPHEADER, headers)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.CONNECTTIMEOUT, 10)
        c.setopt(c.CAINFO, certifi.where())
        c.perform()
        c.close()
        data = buffer.getvalue()
        json_data = json.loads(data)
        print(len(json_data['players']))
    except Exception as ex:
        print(f'Exception in get_player_data_json')


def get_savant_gamefeed_page_curl(url_name):

    headers = ["authority: baseballsavant.mlb.com"
              ,  "user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
            ]

    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url_name)
    c.setopt(c.CONNECTTIMEOUT, TIMEOUT)
    c.setopt(c.HTTPHEADER, headers)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.CAINFO, certifi.where())
    c.perform()
    c.close()
    data = buffer.getvalue()
    return json.loads(data)


def main():
    # url = "https://baseballsavant.mlb.com/gf?game_pk=718666"
    # data = get_savant_gamefeed_page_curl(url)
    # print(data)

    get_player_data_json()
    get_player_data_json_requests()


if __name__ == "__main__":
    main()

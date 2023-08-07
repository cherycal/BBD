import sys

import requests

sys.path.append('./modules')

# https://slack.dev/python-slack-sdk/
import logging

logging.basicConfig(level=logging.DEBUG)

from io import BytesIO
import certifi
import pycurl


def get_savant_events_requests(url_name):
    headers = {"authority": "baseballsavant.mlb.com"
               # , "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
               # , "accept-language": "en-US,en;q=0.9"
               # , "cache-control": "max-age=0"
               # , "dnt": "1"
               # , "if-modified-since": "Sat, 08 Apr 2023 19:59:59 GMT"
               # , "sec-ch-ua-mobile": "?0"
               # , "sec-ch-ua-platform": "Windows"
               # , "sec-fetch-dest": "document"
               # , "sec-fetch-mode": "navigate"
               # , "sec-fetch-site": "none"
               # , "sec-fetch-user": "?1"
               # , "upgrade-insecure-requests": "1"
               # , "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
               }

    r = requests.get(url_name, headers=headers, allow_redirects=True)

    csvfile = "../../2023/python/data/statcast_events_daily.csv"
    print(csvfile)
    open(csvfile, 'wb').write(r.content)

def get_savant_events_2(url_name):
    headers = {"authority": "baseballsavant.mlb.com"
               # , "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
               # , "accept-language": "en-US,en;q=0.9"
               # , "cache-control": "max-age=0"
               # , "dnt": "1"
               # , "if-modified-since": "Sat, 08 Apr 2023 19:59:59 GMT"
               # , "sec-ch-ua-mobile": "?0"
               # , "sec-ch-ua-platform": "Windows"
               # , "sec-fetch-dest": "document"
               # , "sec-fetch-mode": "navigate"
               # , "sec-fetch-site": "none"
               # , "sec-fetch-user": "?1"
               # , "upgrade-insecure-requests": "1"
               # , "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
               }

    print(requests.get(url_name, headers=headers).text)


def get_savant_events_curl(url_name):
    TIMEOUT = 10
    headers = ["authority: baseballsavant.mlb.com"
        ,
               "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
        , "accept-language: en-US,en;q=0.9"
        , "cache-control: max-age=0"
        , "dnt: 1"
        , "if-modified-since: Sat, 08 Apr 2023 19:59:59 GMT"
        , "sec-ch-ua: \"Chromium\";v=\"112\", \"Google Chrome\";v=\"112\", \"Not:A-Brand\";v=\"99\""
        , "sec-ch-ua-mobile: ?0"
        , "sec-ch-ua-platform: \"Windows\""
        , "sec-fetch-dest: document"
        , "sec-fetch-mode: navigate"
        , "sec-fetch-site: none"
        , "sec-fetch-user: ?1"
        , "upgrade-insecure-requests: 1"
        ,
               "user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
               ]

    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url_name)
    c.setopt(c.CONNECTTIMEOUT, TIMEOUT)
    c.setopt(c.HTTPHEADER, headers)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.CAINFO, certifi.where())
    c.setopt(c.FOLLOWLOCATION, True)
    c.perform()
    c.close()

    data = buffer.getvalue()
    print(data)

    csvfile = "../../2023/python/data/statcast_events_daily.csv"
    print(csvfile)
    open(csvfile, 'wb').write(data)


def main():
    #url = "https://baseballsavant.mlb.com/statcast_search/csv?all=true&hfPT=&hfAB=single%7Cdouble%7Ctriple%7Chome%5C.%5C.run%7Cfield%5C.%5C.out%7Cstrikeout%7Cstrikeout%5C.%5C.double%5C.%5C.play%7Cwalk%7Cdouble%5C.%5C.play%7Cfield%5C.%5C.error%7Cgrounded%5C.%5C.into%5C.%5C.double%5C.%5C.play%7Cfielders%5C.%5C.choice%7Cfielders%5C.%5C.choice%5C.%5C.out%7Cforce%5C.%5C.out%7Chit%5C.%5C.by%5C.%5C.pitch%7Cintent%5C.%5C.walk%7Csac%5C.%5C.bunt%7Csac%5C.%5C.bunt%5C.%5C.double%5C.%5C.play%7Csac%5C.%5C.fly%7Csac%5C.%5C.fly%5C.%5C.double%5C.%5C.play%7Ctriple%5C.%5C.play%7C&hfGT=R%7C&hfPR=&hfZ=&stadium=&hfBBL=&hfNewZones=&hfPull=&hfC=&hfSea=2023%7C&hfSit=&player_type=pitcher&hfOuts=&opponent=&pitcher_throws=&batter_stands=&hfSA=&game_date_gt=2023-03-30&game_date_lt=2023-03-30&hfInfield=&team=&position=&hfOutfield=&hfRO=&home_road=&hfFlag=&hfBBT=&metric_1=&hfInn=&min_pitches=0&min_results=0&group_by=name-event&sort_col=xwoba&player_event_sort=lineup_cd&sort_order=desc&min_pas=0&chk_event_estimated_slg_using_speedangle=on&type=details&"
    #get_savant_events_requests(url)

    url = "https://baseballsavant.mlb.com/statcast_search?hfPT=&hfAB=single%7Cdouble%7Ctriple%7Chome%5C.%5C.run%7Cfield%5C.%5C.out%7Cstrikeout%7Cstrikeout%5C.%5C.double%5C.%5C.play%7Cwalk%7Cdouble%5C.%5C.play%7Cfield%5C.%5C.error%7Cgrounded%5C.%5C.into%5C.%5C.double%5C.%5C.play%7Cfielders%5C.%5C.choice%7Cfielders%5C.%5C.choice%5C.%5C.out%7Cforce%5C.%5C.out%7Chit%5C.%5C.by%5C.%5C.pitch%7Cintent%5C.%5C.walk%7Csac%5C.%5C.bunt%7Csac%5C.%5C.bunt%5C.%5C.double%5C.%5C.play%7Csac%5C.%5C.fly%7Csac%5C.%5C.fly%5C.%5C.double%5C.%5C.play%7Ctriple%5C.%5C.play%7C&hfGT=R%7C&hfPR=&hfZ=&stadium=&hfBBL=&hfNewZones=&hfPull=&hfC=&hfSea=2023%7C&hfSit=&player_type=batter&hfOuts=&opponent=&pitcher_throws=&batter_stands=&hfSA=&game_date_gt=2023-03-30&game_date_lt=2023-03-30&hfInfield=&team=&position=&hfOutfield=&hfRO=&home_road=&hfFlag=&hfBBT=&metric_1=&hfInn=&min_pitches=0&min_results=0&group_by=name-event&sort_col=xwoba&player_event_sort=lineup_cd&sort_order=desc&min_pas=0&chk_event_estimated_slg_using_speedangle=on#results"
    get_savant_events_2(url)


if __name__ == "__main__":
    main()

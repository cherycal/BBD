__author__ = 'chance'

import sys
import time

sys.path.append('./modules')
import os
import sqldb
import push
import pycurl
from io import BytesIO
import json
import certifi
from datetime import datetime
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd

inst = push.Push()

def get_rank(section, row):
    if ( section[0:1] == "P" and int(row) <= 12) or int(section) <= 106:
        rank = 1
    elif row <= 1 and int(section) <= 129:
        rank = 2
    elif int(section) == 121 and int(row) <= 15:
        rank = 3
    else:
        rank = row
        if row > 24:
            rank += (row - 25) * 2
        if row >= 25 and rank <= 27:
            rank -= 15
        section = int(section)
        sectionScore = section - 100
        if section % 2 == 0 and section >= 110:
            sectionScore *= 2
        if section % 2 == 0 and section >= 116:
            sectionScore *= 2
        if section >= 121:
            sectionScore *= 1.5
        if section >= 123:
            sectionScore *= 1.5
        if section >= 125:
            sectionScore *= 2.5
        rank += sectionScore + row

    return rank


def get_listings(count):
    bdb = sqldb.DB('Baseball.db')

    now = datetime.now()  # current date and time
    date_time = now.strftime("%Y%m%d_%H%M%S")

    eventId = '105060644'
    priceMin = 10
    priceMax = 46
    FEE = 14
    TIMEOUT = 10
    PRICE_FLOOR = 54
    SLEEP_PUSH = 2

    BEARER = os.environ['STUBHUB_BEARER']
    zones = ''
    withZones = True
    if withZones:
        zones = '&zoneIdList=46827,46828,46829,46830,46824,46826,78030,46825,46842,46841' #90029 46928 46823
        # "id":46823,First Base VIP Box 13"
        # id":46826, 113-120
        # id":46825, 107-114
        # "id":46824 101-110
        # "id":46828, 121-127
        # "id":78030 109-116
        # "id":46827, 117-127
        # id":46928, 7,9,11
        # "id":90029, 1-6
        # "id":94280 1-6
        # "id":46830, Premier
        # "id": 46850, Premier Suite
        # "id":46841, 129-137
        # "id":46927, 8,10


    url_name = f'https://api.stubhub.com/sellers/find/listings/v3/?eventId=' \
               f'{eventId}&quantity=2&start=0&rows=200&priceMin={priceMin}&priceMax={priceMax}{zones}'

    url_name = f'https://api.stubhub.net/catalog/events/{eventId}'

    print(f'{url_name}')

    headers = [f'Authorization: Bearer {BEARER}',
               'Accept: application/json']

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

    data_json = json.loads(data)

    if not data_json.get('listings'):
        print(f'No listings for eventId: {eventId}: {data_json}')
        exit(0)

    lol = list()

    for listing in data_json['listings']:
        # print(listing)
        section = listing['sellerSectionName']
        section = section.replace("Field Reserved ", "")
        price = round(listing['pricePerProduct']['amount'] + FEE, 2)

        row = listing.get('row', '0')
        row = int(row.replace(" ", ""))
        seatNumber = listing.get('seat', "")

        if listing.get('products'):
            products = listing['products']
            for seat in products:
                row = seat['row']
                row = row.replace("D","")
                row = int(row.replace(" ", ""))
                seatNumber = seat['seat']
                seatNumber = seatNumber.replace(" ", "")

        rank = get_rank(section, row)
        if rank <= 1:
            msg = f'S: {section} R: {row} ({price} Rk: {rank})'
            print(f'Tweeting: {msg}')
            inst.push(msg, '')
            inst.tweet(msg)
            time.sleep(SLEEP_PUSH)
        seatDetail = [date_time, eventId, section, price, row, seatNumber, rank]
        lol.append(seatDetail)

    # print(lol)
    col_headers = ['date_time', 'eventId', 'section', 'price', 'row', 'seatNumber', 'rank']
    df = pd.DataFrame(lol, columns=col_headers)

    table_name = "Tickets"
    # bdb.delete(f'delete FROM {table_name}')
    df.to_sql(table_name, bdb.conn, if_exists='append', index=False)

    if count % 4 == 0:
        cols, rows = bdb.select_w_cols(f'SELECT * FROM TicketsView WHERE price <= {PRICE_FLOOR} LIMIT 1')
        for row in rows:
            low_listing = dict(zip(cols, row))
            msg = f'Low Sec: {low_listing["section"]} Row: {low_listing["row"]} ({low_listing["price"]}) {low_listing["date_time"]}'
            print(f'Pushing: {msg}')
            inst.push(msg, '')
            time.sleep(SLEEP_PUSH)

        cols, rows = bdb.select_w_cols(f'SELECT * FROM TicketsView LIMIT 1')
        for row in rows:
            best_listing = dict(zip(cols, row))
            msg = f'Top Sec: {best_listing["section"]} Row: {best_listing["row"]} ({best_listing["price"]}) {best_listing["date_time"]}'
            print(f'Pushing: {msg}')
            inst.push(msg, '')
            time.sleep(SLEEP_PUSH)

    bdb.close()


def main():
    count = 0
    SLEEP_INTERVAL = 60 * 8
    while True:
        try:
            get_listings(count)
        except Exception as ex:
            print(f'Try failed with exception {ex}')
        time.sleep(SLEEP_INTERVAL)
        count += 1


if __name__ == "__main__":
    main()

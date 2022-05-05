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
import pandas as pd

inst = push.Push()

def get_rank(section, row):
    rank = 100
    if section[0:1] == "P":
        rank = 1
    elif row <= 2 and int(section) <= 129:
        rank = row + 1
    else:
        if row > 25:
            rank += (row - 25) * 2
        if row == 26:
            rank -= 5
        if section[0:1] != "P":
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
                sectionScore *= 1.5
            rank += sectionScore + row

    return rank


def get_listings(count):
    bdb = sqldb.DB('Baseball.db')

    now = datetime.now()  # current date and time
    date_time = now.strftime("%Y%m%d_%H%M%S")

    eventId = '105060685'
    priceMin = 10
    priceMax = 50
    FEE = 14
    TIMEOUT = 10
    PRICE_FLOOR = 60
    SLEEP_PUSH = 2

    BEARER = os.environ['STUBHUB_BEARER']
    zones = ''
    withZones = True
    if withZones:
        zones = '&zoneIdList=46827,46828,46829,46830,46824,46826,78030,46825,46842,46841'

    url_name = f'https://api.stubhub.com/sellers/find/listings/v3/?eventId=' \
               f'{eventId}&quantity=2&start=0&rows=200&priceMin={priceMin}&priceMax={priceMax}{zones}'

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

    # if not data_json.get('listings'):
    #     print(f'No listings for eventId: {eventId}')

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
                row = int(row.replace(" ", ""))
                seatNumber = seat['seat']
                seatNumber = seatNumber.replace(" ", "")

        rank = get_rank(section, row)
        if rank == 1:
            msg = f'Sec: {section} Row: {row} ({price})'
            print(f'Pushing: {msg}')
            inst.push(msg, '')
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
        cols, rows = bdb.select_w_cols(f'SELECT * FROM TicketsView WHERE price < {PRICE_FLOOR} LIMIT 1')
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
    SLEEP_INTERVAL = 60 * 10
    while True:
        try:
            get_listings(count)
        except Exception as ex:
            print(f'Try failed with exception {ex}')
        time.sleep(SLEEP_INTERVAL)
        count += 1


if __name__ == "__main__":
    main()

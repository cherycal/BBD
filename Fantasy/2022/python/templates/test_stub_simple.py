__author__ = 'chance'

import sys

sys.path.append('../modules')
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
bdb = sqldb.DB('Baseball.db')

now = datetime.now()  # current date and time
date_time = now.strftime("%Y%m%d_%H%M%S")
date8 = now.strftime("%Y%m%d")


def get_rank(section, row):
    rank = 1
    if row < 10:
        rank = row
    if section[0:1] != "P":
        section = int(section)
        sectionScore = section - 100
        if section % 2 == 0 and section >= 110:
            sectionScore *= 4
        if section >= 123:
            sectionScore *= 2
        rank = sectionScore + row

    return rank


def main():
    eventId = '105060685'
    priceMin = 25
    priceMax = 75
    BEARER = os.environ['STUBHUB_BEARER']

    zones = ''
    withZones = True
    if withZones:
        zones = '&zoneIdList=46827,46828,46829,46830,46824,46826,78030,46825,46842'

    url_name = f'https://api.stubhub.com/sellers/find/listings/v3/?eventId=' \
               f'{eventId}&quantity=2&start=0&rows=200&priceMin={priceMin}&priceMax={priceMax}{zones}'

    headers = [f'Authorization: Bearer {BEARER}',
               'Accept: application/json']

    TIMEOUT = 10
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
        price = listing['pricePerProduct']['amount']

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
        seatDetail = [date_time, eventId, section, price, row, seatNumber, rank]
        lol.append(seatDetail)

    # print(lol)
    col_headers = ['date_time', 'eventId', 'section', 'price', 'row', 'seatNumber', 'rank']
    df = pd.DataFrame(lol, columns=col_headers)

    table_name = "Tickets"
    # bdb.delete(f'delete FROM {table_name}')
    df.to_sql(table_name, bdb.conn, if_exists='append', index=False)

    bdb.close()


if __name__ == "__main__":
    main()

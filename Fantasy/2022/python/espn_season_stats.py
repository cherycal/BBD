import json
import sys

sys.path.append('./modules')
import sqldb
import pycurl
import certifi
from io import BytesIO
import pandas as pd

def get_stats(yr=2022):
    bdb = sqldb.DB('Baseball.db')

    # Columns for table
    dfheaders = ["Name", "id", "Year"]

    stat_id_list = list()
    stats_table = bdb.select_plus(f'SELECT * from ESPNStatIds')
    #cat_dict = dict()
    for d in stats_table['dicts']:
        dfheaders.append(d['statabbr'])
        stat_id_list.append(str(d['statid']))
        #cat_dict[d['statabbr']] = str(d['statid'])

    url_name = "https://fantasy.espn.com/apis/v3/games/flb/" \
               "seasons/" + str(yr) + "/segments/0/leaguedefaults/1?view=kona_player_info"

    headers = ['authority: fantasy.espn.com',
               'accept: application/json',
               'x-fantasy-source: kona',
               'x-fantasy-filter: {"players":{"filterStatus":{"value":["FREEAGENT","WAIVERS","ONTEAM"]},'
               '"filterSlotIds":{"value":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]}}}']

    #print("get_player_data_json: " + url_name)
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url_name)
    c.setopt(c.HTTPHEADER, headers)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.CAINFO, certifi.where())
    c.perform()
    c.close()

    data = buffer.getvalue()
    json_data = json.loads(data)

    stat_rows = []
    for player in json_data['players']:
        if player.get('player'):
            player_data = player['player']
            player_name = player_data.get('fullName', "NA")
            player_id = player_data.get('id', 0)
            if player_data.get('stats'):
                #print(f'Name: {player_name}')
                for stat_dict in player_data['stats']:
                    # 00: actual 10: projected
                    if stat_dict['id'] == '00' + str(yr):
                        stats = stat_dict['stats']
                        if len(stats):
                            #print(f'Length: {len(stats)}: {stats}')
                            stat_row = [player_name, player_id, yr]
                            for stat_id in stat_id_list:
                                stat_row.append(stats.get(stat_id, None))
                            #print(f'{stat_row}')
                            stat_rows.append(stat_row)

    df = pd.DataFrame(stat_rows, columns=dfheaders)
    table_name = "ESPNSeasonStats"
    del_cmd = f'delete from {table_name} where Year = {str(yr)}'
    bdb.delete(del_cmd)
    df.to_sql(table_name, bdb.conn, if_exists='append', index=False)

    bdb.close()
    return


def main():
    yr = 2022
    get_stats(yr)
    exit(0)


if __name__ == "__main__":
    main()

import sys

sys.path.append('./modules')
import sqldb
import pandas as pd

def espn_positions():
    bdb = sqldb.DB('Baseball.db')

    # Columns for table
    dfheaders = ["id", "Name", "Position"]

    poslist = list()
    epdc = bdb.select_plus(f'SELECT * from ESPNPlayerDataCurrent')
    #cat_dict = dict()
    for d in epdc['dicts']:
        #print(f"{d['eligiblePositions']} {d['espnid']} {d['name']}")
        positions = d['eligiblePositions'].split(",")
        #print(positions)
        for p in positions:
            p = p.strip()
            p = p.replace("'", "")
            #print(f"{d['espnid']} {d['name']} {p}")
            poslist.append([d['espnid'],d['name'],p])

    df = pd.DataFrame(poslist, columns=dfheaders)
    #print(df)
    table_name = "ESPNPlayerPositions"
    del_cmd = f'delete from {table_name}'
    bdb.delete(del_cmd)
    df.to_sql(table_name, bdb.conn, if_exists='append', index=False)

    bdb.close()
    return


def main():
    espn_positions()
    exit(0)


if __name__ == "__main__":
    main()

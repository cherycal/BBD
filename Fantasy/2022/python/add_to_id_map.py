import sys

sys.path.append('./modules')
import sqldb
import push
import fantasy

inst = push.Push()
bdb = sqldb.DB('Baseball.db')
fantasy = fantasy.Fantasy()


def create_id_map():
    idmapids = list()
    idmap_obj = bdb.select_plus("select * from IDMap")
    for d in idmap_obj['dicts']:
        idmapids.append(d['IDPLAYER'])
    return idmapids


def run_id_map_fixes():
    missing_obj = bdb.select_plus("select * from ACheck_IDMap_Found")
    for d in missing_obj['dicts']:
        idmapids = create_id_map()
        idmapidtype = ""
        idnametype = ""
        if d['mlbid'] in idmapids:
            # print(f"id {d['mlbid']} found")
            if d['otheridtype'] == "FG":
                idmapidtype = "IDFANGRAPHS"
                idnametype = "FANGRAPHSNAME"
            elif d['otheridtype'] == "ESPN":
                idmapidtype = "ESPNID"
                idnametype = 'ESPNNAME'
            else:
                pass
            cmd = f"UPDATE IDMap set TEAM = '{d['mlbTeam']}', POS = '{d['position']}', " \
                  f"{idmapidtype} = '{d['id']}', {idnametype} = '{d['name']}', " \
                  f"BATS = '{d['bats']}', THROWS = '{d['throws']}' WHERE IDPLAYER = {d['mlbid']}"
            print(f"{cmd}")
        else:
            # print(f"id {d['mlbid']} not found")
            insertcols = f"(IDPLAYER, PLAYERNAME, TEAM, POS, IDFANGRAPHS, FANGRAPHSNAME, ESPNID, ESPNNAME, MLBID, MLBNAME, BATS, THROWS)"
            idfangraphs = d.get('idfangraphs', 'NULL')
            fangraphsname = d.get('name', "")
            espnid = d.get('espnid', "NULL")
            espnname = d.get('name', "")
            insertvals = f"({d['mlbid']}, '{d['name']}', '{d['mlbTeam']}', '{d['position']}'," \
                         f" {idfangraphs}, '{fangraphsname}', {espnid}, '{espnname}', {d['mlbid']}, '{d['name']}', " \
                         f"'{d['bats']}', '{d['throws']}')"
            cmd = f"INSERT INTO IDMAP {insertcols} VALUES {insertvals}"
            print(f"{cmd}")

        bdb.cmd(cmd)

def main():
    run_id_map_fixes()


if __name__ == "__main__":
    main()

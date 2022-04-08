__author__ = 'chance'

import sys

sys.path.append('./modules')
import pandas as pd
import time
import push
from datetime import date
from datetime import timedelta

inst = push.Push()

import sqldb

bdb = sqldb.DB('Baseball.db')


def do_range(start_date, end_date, player_type, spring_training):

    year = start_date[6:10]
    start_date8 = year + start_date[0:2] + start_date[3:5]
    end_date8 = year + end_date[0:2] + end_date[3:5]
    bpdir = ""
    if player_type == "batter":
        bpdir = "Batting"
    elif player_type == "pitcher":
        bpdir = "Pitching"
    else:
        print("player_type is batter or pitcher")
        exit(-1)

    st_flag = ""
    if spring_training:
        st_flag = "S"
    else:
        st_flag = "R"


    csvfile = "C:\\Users\\chery\\Documents\\BBD\\Statcast\\" + bpdir + \
              "\\statcast_daily_" + start_date + "_" + end_date + ".csv"  # "statcast_daily_batting_20210401.csv"

    url_text = "https://baseballsavant.mlb.com/statcast_search?" \
               "hfPT=&hfAB=single%7Cdouble%7Ctriple%7Chome%5C.%5C.run%7Cfield%5C.%5C.out%" \
               "7Cstrikeout%7Cstrikeout%5C.%5C.double%5C.%5C.play%7Cwalk%7Cdouble%5C.%5C.play%" \
               "7Cfield%5C.%5C.error%7Cgrounded%5C.%5C.into%5C.%5C.double%5C.%5C.play%7C" \
               "fielders%5C.%5C.choice%7Cfielders%5C.%5C.choice%5C.%5C.out%7C" \
               "force%5C.%5C.out%7Chit%5C.%5C.by%5C.%5C.pitch%7Cintent%5C.%5C.walk%7C" \
               "sac%5C.%5C.bunt%7Csac%5C.%5C.bunt%5C.%5C.double%5C.%5C.play%7C" \
               "sac%5C.%5C.fly%7Csac%5C.%5C.fly%5C.%5C.double%5C.%5C.play%" \
               "7Ctriple%5C.%5C.play%7C" + "&hfPR=&hfZ=&stadium=&hfBBL=&hfNewZones=&hfGT=" + st_flag + "%7C" + \
               "&hfC=&hfSea=" + str(year) + "%7C&hfSit=&player_type=" + player_type + "&hfOuts=&opponent=&" \
                "pitcher_throws=&batter_stands=&hfSA=&game_date_gt=" + start_date + \
               "&game_date_lt=" + end_date + \
               "&hfInfield=&team=&position=&hfOutfield=&hfRO=&home_road=&hfFlag=&hfPull=&metric_1=&hfInn=&min_pitches=0&" \
               "min_results=0&group_by=name-date&sort_col=xwoba&player_event_sort=api_h_launch_speed&" \
               "sort_order=desc&min_pas=0" \
               "&chk_stats_date=on" \
               "&chk_stats_player_id=on" \
               "&chk_stats_game_pk=on" \
               "&chk_stats_pa=on" \
               "&chk_stats_abs=on" \
               "&chk_stats_bip=on" \
               "&chk_stats_hits=on" \
               "&chk_stats_singles=on" \
               "&chk_stats_dbls=on" \
               "&chk_stats_triples=on" \
               "&chk_stats_hrs=on" \
               "&chk_stats_so=on" \
               "&chk_stats_k_percent=on" \
               "&chk_stats_bb=on" \
               "&chk_stats_bb_percent=on" \
               "&chk_stats_babip=on" \
               "&chk_stats_iso=on" \
               "&chk_stats_ba=on" \
               "&chk_stats_xba=on" \
               "&chk_stats_xbadiff=on" \
               "&chk_stats_slg=on" \
               "&chk_stats_xslg=on" \
               "&chk_stats_xslgdiff=on" \
               "&chk_stats_obp=on" \
               "&chk_stats_xobp=on" \
               "&chk_stats_woba=on" \
               "&chk_stats_xwoba=on" \
               "&chk_stats_wobadiff=on" \
               "&chk_stats_velocity=on" \
               "&chk_stats_launch_speed=on" \
               "&chk_stats_launch_angle=on" \
               "&chk_stats_bbdist=on" \
               "&chk_stats_spin_rate=on" \
               "&chk_stats_plate_x=on" \
               "&chk_stats_plate_z=on" \
               "&chk_stats_release_pos_x=on" \
               "&chk_stats_release_pos_z=on" \
               "&chk_stats_pos3_int_start_distance=on" \
               "&chk_stats_pos4_int_start_distance=on" \
               "&chk_stats_pos6_int_start_distance=on" \
               "&chk_stats_pos5_int_start_distance=on" \
               "&chk_stats_pos7_int_start_distance=on" \
               "&chk_stats_pos8_int_start_distance=on" \
               "&chk_stats_pos9_int_start_distance=on" \
               "&chk_stats_release_extension=on" \
               "#results"

    # url_text = "https://baseballsavant.mlb.com/statcast_search?hfPT=&hfAB=single%7Cdouble%7Ctriple%7Chome%5C.%5C.run%7Cfield%5C.%5C.out%7Cstrikeout%7Cstrikeout%5C.%5C.double%5C.%5C.play%7Cwalk%7Cdouble%5C.%5C.play%7Cfield%5C.%5C.error%7Cgrounded%5C.%5C.into%5C.%5C.double%5C.%5C.play%7Cfielders%5C.%5C.choice%7Cfielders%5C.%5C.choice%5C.%5C.out%7Cforce%5C.%5C.out%7Chit%5C.%5C.by%5C.%5C.pitch%7Cintent%5C.%5C.walk%7Csac%5C.%5C.bunt%7Csac%5C.%5C.bunt%5C.%5C.double%5C.%5C.play%7Csac%5C.%5C.fly%7Csac%5C.%5C.fly%5C.%5C.double%5C.%5C.play%7Ctriple%5C.%5C.play%7C&hfBBT=&hfPR=&hfZ=&stadium=&hfBBL=&hfNewZones=&hfGT=R%7C&hfC=&hfSea=2021%7C&hfSit=&player_type=pitcher&hfOuts=&opponent=&pitcher_throws=&batter_stands=&hfSA=&game_date_gt="+\
    #            "2021-04-01"+\
    #            "&game_date_lt=" +\
    #            "2021-04-02"+\
    #            "&hfInfield=&team=&position=&hfOutfield=&hfRO=&home_road=&hfFlag=&hfPull=&metric_1=&hfInn=&min_pitches=0&min_results=0&group_by=name-date&sort_col=xwoba&player_event_sort=api_h_launch_speed&sort_order=desc&min_pas=0&chk_stats_date=on&chk_stats_player_id=on&chk_stats_pa=on&chk_stats_abs=on&chk_stats_bip=on&chk_stats_hits=on&chk_stats_singles=on&chk_stats_dbls=on&chk_stats_triples=on&chk_stats_hrs=on&chk_stats_so=on&chk_stats_k_percent=on&chk_stats_bb=on&chk_stats_bb_percent=on&chk_stats_babip=on&chk_stats_iso=on&chk_stats_ba=on&chk_stats_xba=on&chk_stats_xbadiff=on&chk_stats_slg=on&chk_stats_xslg=on&chk_stats_xslgdiff=on&chk_stats_obp=on&chk_stats_xobp=on&chk_stats_woba=on&chk_stats_xwoba=on&chk_stats_wobadiff=on&chk_stats_velocity=on&chk_stats_launch_speed=on&chk_stats_launch_angle=on&chk_stats_bbdist=on&chk_stats_spin_rate=on&chk_stats_plate_x=on&chk_stats_plate_z=on&chk_stats_release_pos_x=on&chk_stats_release_pos_z=on&chk_stats_pos3_int_start_distance=on&chk_stats_pos4_int_start_distance=on&chk_stats_pos6_int_start_distance=on&chk_stats_pos5_int_start_distance=on&chk_stats_pos7_int_start_distance=on&chk_stats_pos8_int_start_distance=on&chk_stats_pos9_int_start_distance=on&chk_stats_release_extension=on#results"

    print(url_text)

    df = pd.read_html(url_text)[0]

    print("sleeping ....")
    time.sleep(1)

    df.drop(df.columns[[1, 7, -1]], axis=1, inplace=True)
    df.columns.values[6] = "id"
    df.columns.values[7] = "gamepk"
    df['Date'] = pd.to_datetime(df['Date'])
    df['Date'] = df['Date'].dt.strftime('%Y%m%d')
    df['Season'] = pd.to_numeric(year)
    df.insert(loc=2, column='playerid', value=df['id'])
    df.drop(['id'], axis=1, inplace=True)

    df[['LastName', 'FirstName']] = df['Player'].str.split(',', expand=True)
    df['Player'] = df[['FirstName', 'LastName']].agg(' '.join, axis=1)
    df['Player'] = df['Player'].str.strip()
    df.drop(['LastName'], axis=1, inplace=True)
    df.drop(['FirstName'], axis=1, inplace=True)
    df['GameType'] = st_flag

    df.to_csv(csvfile, index=False, encoding='utf-8-sig')
    table_name = "Statcast" + bpdir + "Daily"

    # CONVERT Date to Date8
    del_cmd = 'DELETE from ' + table_name + ' WHERE Date >= ' + start_date8 + " AND Date <= " + end_date8
    bdb.delete(del_cmd)
    df.to_sql(table_name, bdb.conn, if_exists='append', index=False)

    print("done")


def main():

    today = date.today()
    yesterday = today - timedelta(days=1)
    date10 = yesterday.strftime("%m-%d-%Y")

    start_date = date10
    end_date = date10

    # start_date = "03-30-2021"
    # end_date = "04-30-2021"

    # player_type = "pitcher"  # "batter or pitcher
    spring_training = False

    #######################

    do_range(start_date, end_date, "pitcher", spring_training)
    do_range(start_date, end_date, "batter", spring_training)


if __name__ == "__main__":
    main()

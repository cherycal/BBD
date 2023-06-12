__author__ = 'chance'

import re
import sys
import time
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup
from pandasql import sqldf

sys.path.append('./modules')
import sqldb
cur_dir = Path.cwd()
data_dir = cur_dir / 'data'
data_dir.mkdir(mode=0o755, exist_ok=True)
bdb = sqldb.DB('Baseball.db')
import tools

def get_savant_page(year, player_type):
    #year = "2023"
    # Custom statcast stats
    #player_type = "batter"
    table_type = "Batting"

    if player_type == "pitcher":
        table_type = "Pitching"

    url = f"https://baseballsavant.mlb.com/leaderboard/custom?year=2023&type={player_type}&" \
          f"filter=&sort=1&sortDir=desc&min=25&selections=xba,xslg,xwoba,xobp,xiso," \
          f"exit_velocity_avg,launch_angle_avg,sweet_spot_percent,barrel_batted_rate," \
          f"&chart=false&x=xba&y=xba&r=no&chartType=beeswarm"

    print(url)

    headers = {"authority": "baseballsavant.mlb.com"}
    print("sleeping ....")
    time.sleep(.5)
    r = requests.get(url, headers=headers, allow_redirects=True)
    soup = BeautifulSoup(r.content, 'html.parser')
    scr = str(soup.find_all('script')[3])[10:].strip()
    pattern = re.compile('var data = (.*);')
    m = pattern.match(scr)
    jd = m.groups(0)[0]
    df = pd.read_json(jd)

    filename = f"statcast_{player_type}_events_season.csv"
    csvfile = data_dir / filename
    print(f"{csvfile}")
    df.to_csv(csvfile)

    columns = f"year,player_id,pitch_count,season_id,player_name,pid,player_age,p_k_percent,p_bb_percent," \
              f"ba,xba,bacon,obp,slg,xobp,xslg,iso,xiso,woba,xwoba,wobacon,xwobacon,team_id,pitcher,pitch_hand," \
              f"hit,single,double,triple,home_run,walk,strikeout," \
              f"p_opp_batting_avg,slg_percent,on_base_percent,on_base_plus_slg,p_blown_save,p_caught_stealing_2b," \
              f"p_double,p_gnd_into_dp,p_home_run,p_run,p_save,p_shutout,p_single,p_stolen_base_2b,p_stolen_base_3b," \
              f"p_stolen_base_home,p_strikeout,p_triple,p_unearned_run,p_walk,p_win,p_total_bases," \
              f"p_total_caught_stealing,p_total_hits,p_total_pa,p_total_stolen_base,p_quality_start," \
              f"p_run_support,p_gnd_into_dp_opp,p_grand_slam,p_relief_lost_lead," \
              f"hbp,k_percent,bb_percent,barrel_batted_rate,exit_velocity_avg,sweet_spot_percent,hard_hit_percent," \
              f"in_zone_percent,out_zone_percent,edge_percent,z_swing_percent," \
              f"oz_swing_percent,iz_contact_percent,oz_contact_percent,whiff_percent,meatball_percent," \
              f"z_swing_miss_percent,oz_swing_miss_percent,in_zone,out_zone,edge,barrel,popups_percent," \
              f"flyballs_percent,linedrives_percent,groundballs_percent,solidcontact_percent,hr_flyballs_percent," \
              f"in_zone_swing,out_zone_swing,in_zone_swing_miss,out_zone_swing_miss,pitch_count_fastball," \
              f"pitch_count_offspeed,pitch_count_breaking,pa," \
              f"ff_avg_speed,ff_avg_spin,ff_avg_break,sl_avg_speed,sl_avg_spin,sl_avg_break,ch_avg_speed," \
              f"ch_avg_spin,ch_avg_break,fs_avg_speed,fs_avg_spin,fs_avg_break,fastball_avg_speed," \
              f"fastball_avg_spin,fastball_avg_break,breaking_avg_speed,breaking_avg_spin,breaking_avg_break," \
              f"offspeed_avg_speed,offspeed_avg_spin,offspeed_avg_break,p_era,batting_avg"

    columns = ','.join(df.columns)

    if table_type == "Batting":
        columns = "*"

    df = sqldf(f"select {columns} from df")

    table_name = f"Statcast{table_type}Season"
    del_cmd = f"delete from {table_name} where Year = '{year}'"
    not_passed = True
    while not_passed:
        try:
            print(del_cmd)
            bdb.delete(del_cmd)
            not_passed = False
        except Exception as ex:
            print(f"DB Error: {str(ex)}")
            time.sleep(.5)

    try:
        df.to_sql(table_name, bdb.conn, if_exists='append', index=False)
    except Exception as ex:
        print(f"DB Error: {str(ex)}")

@tools.try_wrap
def main():
    year = "2023"
    get_savant_page(year, "batter")
    get_savant_page(year, "pitcher")


if __name__ == "__main__":
    main()

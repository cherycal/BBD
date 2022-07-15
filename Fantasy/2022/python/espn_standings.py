import os
import sys
import time

sys.path.append('./modules')

import warnings

warnings.simplefilter(action='ignore', category=UserWarning)
import pandas as pd
import fantasy
# import dataframe_image as dfi
from datetime import date, datetime
from datetime import timedelta
import matplotlib.pyplot as plt
from imgurpython import ImgurClient
import push

inst = push.Push()

mode = "PROD"
fantasy = fantasy.Fantasy(mode)
bdb = fantasy.get_db()
ts = datetime.now()  # current date and time
formatted_date_time = ts.strftime("%Y%m%d-%H%M%S")
formatted_date8 = ts.strftime("%Y%m%d")


def get_account_map():
    account_map = {
        '37863846': {
            'pts': f'AdjR + AdjH2B + AdjH3B + AdjHR + AdjRBI + AdjSB + AdjGIDP + AdjAVG +  AdjHRAGNST + AdjK + AdjW + AdjL + AdjSV + AdjHD + AdjERA + AdjWHIP',
            'cats': f'AdjR, AdjH2B, AdjH3B, AdjHR, AdjRBI, AdjSB, AdjGIDP, AdjAVG, AdjHRAGNST, AdjK, AdjW, AdjL, AdjSV, AdjHD, AdjERA, AdjWHIP',
            'table': "Standings_History_FRAN",
            'detail_table': 'SD_FRAN',
            'detail_table_current': 'SD_FRAN_CURRENT',
            'chg_table': 'CATS_CHG_FRAN',
            'view': "StandingsFRAN",
            'image': "UpperMidwest"
        },
        '6455': {
            'pts': f'AdjR + AdjHR + AdjRBI + AdjSB + AdjAVG + AdjK + AdjW +  AdjSV  + AdjERA + AdjWHIP',
            'cats': f'AdjR, AdjHR, AdjRBI, AdjSB, AdjAVG, AdjK, AdjW, AdjSV, AdjERA, AdjWHIP',
            'table': "Standings_History_wOBA",
            'detail_table': 'SD_WOBA',
            'detail_table_current': 'SD_WOBA_CURRENT',
            'view': "StandingsWOBA",
            'image': "RotoAuctionKeeper"
        },
        '1095816069': {
            'pts': f'AdjR + AdjHR + AdjRBI + AdjSB + AdjAVG + AdjK + AdjW +  AdjSV  + AdjERA + AdjWHIP',
            'cats': f'AdjR, AdjHR, AdjRBI, AdjSB, AdjAVG, AdjK, AdjW, AdjSV, AdjERA, AdjWHIP',
            'table': "Standings_History_FOMO",
            'view': "StandingsPitch",
            'image': "TexasPro"
        }
    }

    return account_map


def build_query(date8, league, account_map):
    query = f'with Summary as ( \
    with PitchStandings as \
    ( \
    with S as ( \
    with P as ( \
    select S.teamID,T.TeamName,sum(AB) as AB,sum(HITS) as H, sum(R) as R,sum(HR) as HR,sum(RBI) as RBI,sum(SB) as SB, round(sum(HITS)/sum(AB),6) as AVG, \
    sum(IP) as IP,sum(H) as HA,sum(BB) as BBA,sum(ER) as ER,sum(K) as K,sum(W) as W,sum(SV) as SV,round((27*sum(ER)/sum(IP)),6) as ERA,round((sum(H)+sum(BB))/(sum(IP)/3),6) as WHIP, \
    sum(H2B) as H2B, sum(H3B) as H3B, sum(GIDP) as GIDP, sum(HRAGNST) as HRAGNST, sum(L) as L, sum(HD) as HD \
    from ESPNDailyScoring S, ESPNTeamOwners T \
    where S.leagueId = T.LeagueID and S.teamId = T.TeamID \
    and S.LeagueID = {league} and Date >= 20220407 and Date <= {date8}\
    and lineupSlotID not like "B%" \
    and lineupSlotID not like "IL%" \
    group by S.teamID \
    order by S.teamID \
    ) \
    select TeamName, \
    rank() over ( order by R ) as Rrank, \
    rank() over ( order by H2B ) as H2Brank, \
    rank() over ( order by H3B ) as H3Brank, \
    rank() over ( order by HR ) as HRrank, \
    rank() over ( order by RBI ) as RBIrank, \
    rank() over ( order by SB ) as SBrank, \
    rank() over ( order by GIDP desc ) as GIDPrank, \
    rank() over ( order by AVG ) as AVGrank, \
    rank() over ( order by HRAGNST desc ) as HRAGNSTrank, \
    rank() over ( order by K ) as Krank, \
    rank() over ( order by W ) as Wrank, \
    rank() over ( order by L desc ) as Lrank, \
    rank() over ( order by SV ) as SVrank, \
    rank() over ( order by HD ) as HDrank, \
    rank() over ( order by ERA desc ) as ERArank, \
    rank() over ( order by WHIP desc ) as WHIPrank, \
    *  \
    from P \
    ) \
    select Rrank + H2Brank + H3Brank + HRrank + RBIrank + SBrank + GIDPrank + AVGrank + HRAGNSTrank + Krank + Wrank + Lrank + SVrank + HDrank + ERArank + WHIPrank  as Pts,  \
    S.* from S \
    ), \
    HRADJ as ( \
    select HRrank,  \
    (count(HRrank)-1)/2.0 as HRadj from PitchStandings group by HRrank \
    ), \
    H2BADJ as ( \
    select H2Brank,  \
    (count(H2Brank)-1)/2.0 as H2Badj from PitchStandings group by H2Brank \
    ), \
    H3BADJ as ( \
    select H3Brank,  \
    (count(H3Brank)-1)/2.0 as H3Badj from PitchStandings group by H3Brank \
    ), \
    RADJ as ( \
    select Rrank,  \
    (count(Rrank)-1)/2.0 as Radj from PitchStandings group by Rrank \
    ), \
    RBIADJ as ( \
    select RBIrank,  \
    (count(RBIrank)-1)/2.0 as RBIadj from PitchStandings group by RBIrank \
    ), \
    SBADJ as ( \
    select SBrank,  \
    (count(SBrank)-1)/2.0 as SBadj from PitchStandings group by SBrank \
    ), \
    GIDPADJ as ( \
    select GIDPrank,  \
    (count(GIDPrank)-1)/2.0 as GIDPadj from PitchStandings group by GIDPrank \
    ), \
    AVGADJ as ( \
    select AVGrank,  \
    (count(AVGrank)-1)/2.0 as AVGadj from PitchStandings group by AVGrank \
    ), \
    HRAGNSTADJ as ( \
    select HRAGNSTrank,  \
    (count(HRAGNSTrank)-1)/2.0 as HRAGNSTadj from PitchStandings group by HRAGNSTrank \
    ), \
    KADJ as ( \
    select Krank,  \
    (count(Krank)-1)/2.0 as Kadj from PitchStandings group by Krank \
    ), \
    WADJ as ( \
    select Wrank,  \
    (count(Wrank)-1)/2.0 as Wadj from PitchStandings group by Wrank \
    ), \
    LADJ as ( \
    select Lrank,  \
    (count(Lrank)-1)/2.0 as Ladj from PitchStandings group by Lrank \
    ), \
    SVADJ as ( \
    select SVrank,  \
    (count(SVrank)-1)/2.0 as SVadj from PitchStandings group by SVrank \
    ), \
    HDADJ as ( \
    select HDrank,  \
    (count(HDrank)-1)/2.0 as HDadj from PitchStandings group by HDrank \
    ), \
    ERAADJ as ( \
    select ERArank,  \
    (count(ERArank)-1)/2.0 as ERAadj from PitchStandings group by ERArank \
    ), \
    WHIPADJ as ( \
    select WHIPrank,  \
    (count(WHIPrank)-1)/2.0 as WHIPadj from PitchStandings group by WHIPrank \
    ) \
    Select  \
    P.RRank + Radj as AdjR,  \
    P.H2BRank + H2Badj as AdjH2B,  \
    P.H3BRank + H3Badj as AdjH3B,  \
    P.HRRank + HRadj as AdjHR, \
    P.RBIRank + RBIadj as AdjRBI, \
    P.SBRank + SBadj as AdjSB, \
    P.GIDPRank + GIDPadj as AdjGIDP, \
    P.AVGRank + AVGadj as AdjAVG, \
    P.HRAGNSTRank + HRAGNSTadj as AdjHRAGNST, \
    P.KRank + Kadj as AdjK, \
    P.WRank + Wadj as AdjW, \
    P.LRank + Ladj as AdjL, \
    P.SVRank + SVadj as AdjSV, \
    P.HDRank + HDadj as AdjHD, \
    P.ERARank + ERAadj as AdjERA, \
    P.WHIPRank + WHIPadj as AdjWHIP, \
    * from PitchStandings P \
    left outer join RADJ on P.RRank = RADJ.RRANK  \
    left outer join H2BADJ on P.H2BRank = H2BADJ.H2BRANK  \
    left outer join H3BADJ on P.H3BRank = H3BADJ.H3BRANK  \
    left outer join HRADJ on P.HRRank = HRADJ.HRRANK  \
    left outer join RBIADJ on P.RBIRank = RBIADJ.RBIRANK  \
    left outer join SBADJ on P.SBRank = SBADJ.SBRANK  \
    left outer join GIDPADJ on P.GIDPRank = GIDPADJ.GIDPRANK  \
    left outer join AVGADJ on P.AVGRank = AVGADJ.AVGRANK  \
    left outer join HRAGNSTADJ on P.HRAGNSTRank = HRAGNSTADJ.HRAGNSTRANK \
    left outer join KADJ on P.KRank = KADJ.KRANK  \
    left outer join WADJ on P.WRank = WADJ.WRANK  \
    left outer join LADJ on P.LRank = LADJ.LRANK  \
    left outer join SVADJ on P.SVRank = SVADJ.SVRANK  \
    left outer join HDADJ on P.HDRank = HDADJ.HDRANK  \
    left outer join ERAADJ on P.ERARank = ERAADJ.ERARANK  \
    left outer join WHIPADJ on P.WHIPRank = WHIPADJ.WHIPRANK  \
    ) \
    select {account_map[str(league)]["pts"]} as PTS, \
    TeamName, \
    AdjR, AdjH2B, AdjH3B, AdjHR, AdjRBI, AdjSB, AdjGIDP, AdjAVG, AdjHRAGNST, AdjK, AdjW, AdjL, AdjSV, AdjHD, AdjERA, AdjWHIP, \
    R,H2B,H3B,HR,RBI,SB,GIDP,AVG,HRAGNST,K,W,L,SV,HD,ERA,WHIP \
    from Summary order by TeamName'
    return query


def run_single_day(date8, date10, league, account_map):
    query = build_query(date8, league, account_map)
    table_data = bdb.select_plus(query)
    print(f'Date: {date8} League: {league}')
    daily_points = list()
    daily_points.append(date8)
    daily_points.append(date10)
    daily_detail = list()
    column_names = list()
    column_names.append('Date8')
    column_names.append('Date10')
    column_names.append('leagueID')
    for column_name in table_data['column_names']:
        column_names.append(column_name)
    for row in table_data['rows']:
        team_detail = list()
        team_detail.append(date8)
        team_detail.append(date10)
        team_detail.append(league)
        for item in row:
            team_detail.append(item)
        daily_detail.append(team_detail)
    for d in table_data['dicts']:
        daily_points.append(d['PTS'])
    table_name = "ESPNStandingsDetail"
    df_daily_detail = pd.DataFrame(daily_detail, columns=column_names)
    bdb.delete(f'delete FROM {table_name} where Date8 = {date8} and leagueID = {league}')
    df_daily_detail.to_sql(table_name, bdb.conn, if_exists='append', index=False)
    return daily_points


def get_team_names(league):
    table_data = bdb.select_plus(f'select TeamName from ESPNTeamOwners where LeagueID = {league} order by TeamName')
    return_list = list()
    for row in table_data['rows']:
        return_list.append(row[0])
    return return_list


def get_team_rank(view):
    table_data = bdb.select_plus(f'select TeamName from {view}')
    return_list = list()
    for row in table_data['rows']:
        return_list.append(row[0])
    return return_list


def run_all():
    client = ImgurClient(os.environ['IMGURID'], os.environ['IMGURSECRET'])
    client.set_user_auth(os.environ['IMGURACCESS'], os.environ['IMGURREFRESH'])

    account_map = get_account_map()

    for league in account_map:

        config = {
            'album': None,
            'name': f'{account_map[str(league)]["image"]}_{formatted_date8}',
            'title': f'{account_map[str(league)]["image"]}_{formatted_date8}',
            'description': f'{account_map[str(league)]["image"]}_{formatted_date8}'
        }

        # order by best team, preserve order for legend ( https://www.statology.org/matplotlib-legend-order/ )
        team_rank = get_team_rank(account_map[str(league)]['view'])

        today = date.today()
        yesterday = today - timedelta(days=5)
        start_date = yesterday  # date(2022, 4, 7)  # start: date(2022, 4, 7)
        print(league)
        team_names = get_team_names(league)

        column_names = ["Date", "Date10"]
        for team in team_names:
            column_names.append(team)

        legend_order = list()
        for team in team_rank:
            legend_order.append(column_names[2:].index(team))

        step = timedelta(days=1)
        table_name = account_map[str(league)]['table']

        while start_date < today:
            day_lol = []
            date8 = start_date.strftime("%Y%m%d")
            date10 = start_date.strftime("%Y-%m-%d")
            print(date8)
            daily_data = run_single_day(int(date8), date10, league, account_map)
            day_lol.append(daily_data)
            start_date += step
            time.sleep(.4)
            df_day = pd.DataFrame(day_lol, columns=column_names)
            bdb.delete(f'delete FROM {table_name} where Date = {date8}')
            df_day.to_sql(table_name, bdb.conn, if_exists='append', index=False)

        ######### PLOTTING ############
        lol = []
        history = bdb.select_plus(f'SELECT * FROM {table_name}')
        date10_list = []
        for d in history['dicts']:
            date10_list.append(d['Date10'])
        for row in history['rows']:
            lol.append(row)
        pd.set_option("display.max.columns", None)
        pd_dates = pd.to_datetime(date10_list)
        df = pd.DataFrame(lol, columns=history['column_names'])
        df = df.set_index(pd_dates)

        # csv file
        csv_file = f'./data/{table_name}.csv'
        df.to_csv(csv_file)

        # detail file
        detail_lol = []
        detail_table_name = account_map[str(league)].get('detail_table',None)
        if detail_table_name:
            detail_history = bdb.select_plus(f'SELECT * FROM {detail_table_name}')
            for row in detail_history['rows']:
                detail_lol.append(row)
            detail_df = pd.DataFrame(detail_lol, columns=detail_history['column_names'])
            detail_csv_file = f'./data/{detail_table_name}.csv'
            detail_df.to_csv(detail_csv_file)
            print(f'Created: {detail_csv_file}')

            # detail file current
            detail_current_lol = []
            detail_current_table_name = account_map[str(league)].get('detail_table_current', None)
            if detail_current_table_name:
                detail_current_history = bdb.select_plus(f'SELECT * FROM {detail_current_table_name}')
                for row in detail_current_history['rows']:
                    detail_current_lol.append(row)
                detail_current_df = pd.DataFrame(detail_current_lol, columns=detail_current_history['column_names'])
                detail_current_csv_file = f'./data/{detail_current_table_name}.csv'
                detail_current_df.to_csv(detail_current_csv_file)
                print(f'Created: {detail_current_csv_file}')

        chg_table = account_map[str(league)].get('chg_table', None)
        if chg_table:
            chg_file = f'./data/{chg_table}.csv'
            chg_lol = []
            chg_data = bdb.select_plus(f'SELECT * FROM {chg_table}')
            for row in chg_data['rows']:
                chg_lol.append(row)
            chg_df = pd.DataFrame(chg_lol, columns=chg_data['column_names'])
            chg_df.to_csv(chg_file)
            print(f'Created: {chg_file}')


        pd.set_option("display.max.columns", None)
        df.plot(y=column_names[2:])
        # plt.show()
        png_file = f'./data/{table_name}.png'
        handles, labels = plt.gca().get_legend_handles_labels()
        # plt.legend(loc='upper left', prop={'size': 6})
        plt.legend([handles[idx] for idx in legend_order], [labels[idx] for idx in legend_order], loc='upper left',
                   prop={'size': 6})
        # plt.show()
        print(f'{png_file}')
        plt.savefig(png_file)
        image = client.upload_from_path(png_file, config=config, anon=False)
        print(f'Image link: {image["link"]}')
        inst.tweet(f'{account_map[str(league)]["image"]}\n\n{image["link"]}\n\nvia @imgur')
        ######################################

    bdb.close()


def main():
    run_all()


if __name__ == "__main__":
    main()

# df = pd.DataFrame(lol, columns=col_headers, index=index)

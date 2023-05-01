import sys

sys.path.append('./modules')
import push
import espn_standings
import espn_daily_scoring_to_db
import statcast_event_level
import statcast_season_level
import espn_season_stats
import savant_boxscores
import team_splits

inst = push.Push()


def main():
    # scripts = ['espn_season_stats.py',
    #            'espn_daily_scoring_to_db.py', 'espn_standings.py', 'odds.py', 'statcast_event_level.py',
    #            'statcast_daily_level.py', 'savant_boxscores.py', 'team_splits.py', 'tables_to_files.py']

    # scripts = ['./espn_daily_scoring_to_db.py', 'espn_standings.py', 'statcast_event_level.py',
    #            'statcast_season_level.py', 'espn_season_stats.py', 'savant_boxscores.py', 'team_splits.py']
    #
    # for script in scripts:
    #     try:
    #         #exec(open(script).read())
    #         #print(f'Script {script} succeeded')
    #     except Exception as ex:
    #         print(f'Script {script} failed with error {ex}')
    #         inst.push("Morning suite process error:", f'Error: {ex}\nFunction: {script}')
    #     time.sleep(1)

    espn_daily_scoring_to_db.main()
    espn_standings.main()
    statcast_event_level.main()
    statcast_season_level.main()
    espn_season_stats.main()
    savant_boxscores.main()
    team_splits.main()


if __name__ == "__main__":
    main()

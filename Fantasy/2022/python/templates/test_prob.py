import random
import sys

sys.path.append('../')
sys.path.append('../modules')

run_count = 0
walk_count = 0
out_count = 0
inning_count = 1
season_game_count = 1
game_walk_count = 0
game_out_count = 0
game_play_count = 0
game_run_count = 0
season_run_count = 0
season_walk_count = 0
season_out_count = 0
season_play_count = 0
season_count = 0
total_run_count = 0
total_game_count = 0
total_walk_count = 0
total_play_count = 0
SEASONS = 1
OB_PCT = 40
RUN_MULT = 1
PRINTFLAG = True

while season_count < SEASONS:
    while season_game_count < 162:
        num1 = random.randint(0, 100)
        game_play_count += 1
        #print(num1)
        if num1 > 100 - OB_PCT:
            game_walk_count += 1
            if PRINTFLAG:
                print("On Base")
            walk_count += 1
            if walk_count >= RUN_MULT:
                run_count += 1
                game_run_count += 1
                if PRINTFLAG:
                    print(f"\tRun scored. {game_run_count} runs scored. {out_count} outs. Inning {inning_count} ")

        else:
            if PRINTFLAG:
                print("Out")
            game_out_count += 1
            out_count += 1
            if out_count == 3:
                if PRINTFLAG:
                    print(f"\t\t{out_count} outs. Inning {inning_count} over. {run_count} runs scored")
                inning_count += 1
                walk_count = 0
                out_count = 0
                run_count = 0
                if inning_count == 10:
                    if PRINTFLAG:
                        print(f"\t\t\tGame {season_game_count} over. {game_run_count} runs scored. {game_walk_count} walks. "
                              f"{game_out_count} outs. {game_play_count} plays. "
                              f"{100 * game_walk_count/game_play_count} percent walks")
                    season_walk_count += game_walk_count
                    season_play_count += game_play_count
                    season_out_count += game_out_count
                    season_run_count += game_run_count
                    game_play_count = 0
                    game_walk_count = 0
                    game_out_count = 0
                    game_run_count = 0
                    inning_count = 1
                    season_game_count += 1

    if PRINTFLAG:
        print(f"Season over. {season_game_count} games. {season_run_count} runs. "
              f"{round(season_run_count/season_game_count,2)} runs per game. {season_walk_count} walks. "
              f"{season_out_count} outs. {season_play_count} plays. "
              f"{round(100 * season_walk_count/season_play_count,2)} percent walks")
    total_run_count += season_run_count
    total_game_count += season_game_count
    total_walk_count += season_walk_count
    total_play_count += season_play_count
    season_game_count = 0
    season_walk_count = 0
    season_run_count = 0
    season_play_count = 0
    season_out_count = 0
    season_count += 1

print(f"{SEASONS} seasons. {total_game_count} games. {round(total_run_count/total_game_count,2)} runs per game. "
      f"{round(100 * total_walk_count/total_play_count,2)} percent walks")

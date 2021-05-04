options(buildtools.check=NULL)
require(devtools)
require(magrittr)
library(tidyverse)
library(dplyr) 
library(sys)
library(DBI)
library(RSQLite)
library(stringr)
library(vroom)

year <- 2021

# custom_stats_url <- paste0("https://baseballsavant.mlb.com/leaderboard/custom?year=",
#       year,"&type=batter&filter=&sort=1&sortDir=desc&min=1&selections=",
#       "player_id,player_age,b_ab,b_total_pa,b_single,b_double,b_triple,b_home_run,",
#       "b_strikeout,b_walk,batting_avg,slg_percent,on_base_percent,b_rbi,r_total_stolen_base,",
#       "xba,xslg,xwoba,xobp,exit_velocity_avg,launch_angle_avg,sweet_spot_percent,",
#       "barrel_batted_rate,oz_swing_percent,oz_contact_percent,iz_contact_percent,",
#       "&chart=false&x=player_age&y=player_age&r=no&chartType=beeswarm&csv=true")

custom_stats_url <- paste0("https://baseballsavant.mlb.com/leaderboard/custom?year=",
                           year,"&type=batter&filter=&sort=1&sortDir=desc&min=1&selections=",
                           "player_age,b_ab,b_total_pa,b_total_hits,b_single,",
                           "b_double,b_triple,b_home_run,b_strikeout,b_walk,b_k_percent,",
                           "b_bb_percent,batting_avg,slg_percent,on_base_percent,",
                           "on_base_plus_slg,isolated_power,b_rbi,b_lob,b_total_bases,",
                           "r_total_caught_stealing,r_total_stolen_base,b_ab_scoring,",
                           "b_ball,b_called_strike,b_foul,b_foul_tip,b_game,b_gnd_into_dp,",
                           "b_hit_ground,b_hit_fly,b_hit_into_play,b_hit_line_drive,",
                           "b_intent_walk,b_sac_bunt,b_sac_fly,b_swinging_strike,",
                           "r_run,r_stolen_base_2b,r_stolen_base_3b,r_stolen_base_home,",
                           "b_total_ball,b_total_sacrifices,b_total_strike,",
                           "b_total_swinging_strike,b_total_pitches,r_stolen_base_pct,",
                           "xba,xslg,woba,xwoba,xobp,xiso,wobacon,xwobacon,",
                           "exit_velocity_avg,launch_angle_avg,sweet_spot_percent,",
                           "barrels,barrel_batted_rate,solidcontact_percent,",
                           "poorlyweak_percent,hard_hit_percent,z_swing_percent,",
                           "z_swing_miss_percent,oz_swing_percent,oz_swing_miss_percent,",
                           "oz_contact_percent,out_zone_swing_miss,out_zone_swing,",
                           "out_zone_percent,out_zone,meatball_swing_percent,",
                           "meatball_percent,pitch_count_offspeed,pitch_count_fastball,",
                           "pitch_count_breaking,pitch_count,iz_contact_percent,",
                           "in_zone_swing_miss,in_zone_swing,in_zone_percent,",
                           "in_zone,edge_percent,edge,whiff_percent,swing_percent,",
                           "pull_percent,straightaway_percent,opposite_percent,",
                           "batted_ball,f_strike_percent,groundballs_percent,",
                           "groundballs,flyballs_percent,flyballs,linedrives_percent,",
                           "linedrives,popups_percent,popups,n_bolts,hp_to_1b,",
                           "sprint_speed,&chart=false&x=player_age&y=player_age&",
                           "r=no&chartType=beeswarm&csv=true")  


custom_stats_df <- vroom::vroom(custom_stats_url, delim = ",")

expected_stats_url <- paste0("https://baseballsavant.mlb.com/leaderboard/",
              "expected_statistics?type=batter&year=",
              year,
              "&position=&team=&min=1&csv=true")

expected_stats_df <- vroom::vroom(expected_stats_url, delim = ",")

exit_velo_url <- paste0("https://baseballsavant.mlb.com/leaderboard/",
                             "statcast?type=batter&year=",
                             year,
                             "&position=&team=&min=1&csv=true")

exit_velo_df <- vroom::vroom(exit_velo_url, delim = ",")

my_temp_db <- dbConnect(RSQLite::SQLite(), ":memory:")

expected_stats_table <- "ExpectedStats"

dbWriteTable(my_temp_db, expected_stats_table, expected_stats_df, append = TRUE )

exit_velo_stats_table <- "ExitVeloStats"

dbWriteTable(my_temp_db, exit_velo_stats_table, exit_velo_df, append = TRUE )

custom_stats_table <- "CustomStats"

dbWriteTable(my_temp_db, custom_stats_table, custom_stats_df, append = TRUE )

#excess_exp <- dbGetQuery(my_temp_db, 'SELECT * FROM ExpectedStats where player_id not in ( select player_id from ExitVeloStats)')
#excess_exit <- dbGetQuery(my_temp_db, 'SELECT * FROM ExitVeloStats where player_id not in ( select player_id from ExpectedStats)')

combined_df <- dbGetQuery(my_temp_db, 
                          'select * FROM ExitVeloStats V, ExpectedStats X, CustomStats C 
                          where C.player_id = V.player_id and V.player_id = X.player_id')

names(combined_df)

idx = which(duplicated(names(combined_df)))
combined_df = combined_df[,-idx]

file_name <- paste("C:/Users/chery/Documents/BBD/Statcast/Batting/custom_2021.csv",sep="")

write.csv( combined_df, file_name, row.names = FALSE)

dbDisconnect(my_temp_db)

conn <- dbConnect(RSQLite::SQLite(), "C:/Ubuntu/Shared/data/Baseball.db")

delcmd <- paste0("DELETE FROM StatcastBattingSeason WHERE year = ", year )

if (length(combined_df) ) {
  dbExecute(conn, delcmd)
}

dbWriteTable(conn, "StatcastBattingSeason", combined_df, append = TRUE )

dbDisconnect(conn)


#https://baseballsavant.mlb.com/leaderboard/statcast?type=batter&year=2020&position=&team=&min=q&csv=true

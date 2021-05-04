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
#       year,"&type=pitcher&filter=&sort=1&sortDir=desc&min=1&selections=",
#       "player_id,player_age,b_ab,b_total_pa,b_single,b_double,b_triple,b_home_run,",
#       "b_strikeout,b_walk,batting_avg,slg_percent,on_base_percent,b_rbi,r_total_stolen_base,",
#       "xba,xslg,xwoba,xobp,exit_velocity_avg,launch_angle_avg,sweet_spot_percent,",
#       "barrel_batted_rate,oz_swing_percent,oz_contact_percent,iz_contact_percent,",
#       "&chart=false&x=player_age&y=player_age&r=no&chartType=beeswarm&csv=true")

custom_stats_url <- paste0("https://baseballsavant.mlb.com/leaderboard/custom?year=",
                           year,"&type=pitcher&filter=&sort=1&sortDir=desc&min=1&selections=",
                           "player_age,p_game,p_formatted_ip,p_total_pa,p_ab,p_total_hits,",
                           "p_single,p_double,p_triple,p_home_run,p_strikeout,p_walk,p_k_percent,",
                           "p_bb_percent,batting_avg,slg_percent,on_base_percent,on_base_plus_slg,",
                           "isolated_power,p_earned_run,p_out,p_win,p_loss,p_era,p_opp_batting_avg,",
                           "p_opp_on_base_avg,p_quality_start,p_starting_p,p_inh_runner,",
                           "p_inh_runner_scored,p_beq_runner,p_beq_runner_scored,xba,xslg,",
                           "woba,xwoba,xobp,xiso,wobacon,xwobacon,exit_velocity_avg,",
                           "launch_angle_avg,sweet_spot_percent,barrels,barrel_batted_rate,",
                           "solidcontact_percent,z_swing_percent,z_swing_miss_percent,",
                           "oz_swing_percent,oz_swing_miss_percent,oz_contact_percent,",
                           "pitch_count,iz_contact_percent,edge_percent,whiff_percent,",
                           "f_strike_percent,groundballs_percent,flyballs_percent,",
                           "linedrives_percent,fastball_avg_speed,fastball_avg_spin,",
                           "fastball_avg_break_x,fastball_avg_break_z,fastball_avg_break,",
                           "n_breaking_formatted,breaking_avg_speed,breaking_avg_spin,",
                           "breaking_avg_break_x,breaking_avg_break_z,n_offspeed_formatted,",
                           "offspeed_avg_speed,offspeed_avg_spin,offspeed_avg_break_x,",
                           "offspeed_avg_break_z,&chart=false&x=player_age&y=player_age",
                           "&r=no&chartType=beeswarm&csv=true")

custom_stats_df <- vroom::vroom(custom_stats_url, delim = ",")
Sys.sleep(1)

expected_stats_url <- paste0("https://baseballsavant.mlb.com/leaderboard/",
              "expected_statistics?type=pitcher&year=",
              year,
              "&position=&team=&min=1&csv=true")

expected_stats_df <- vroom::vroom(expected_stats_url, delim = ",")
Sys.sleep(1)

exit_velo_url <- paste0("https://baseballsavant.mlb.com/leaderboard/",
                             "statcast?type=pitcher&year=",
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

dbGetQuery(my_temp_db, 'select * FROM CustomStats')

combined_df <- dbGetQuery(my_temp_db, 
                          'select * FROM ExitVeloStats V, ExpectedStats X, CustomStats C 
                          where C.player_id = V.player_id and V.player_id = X.player_id')

names(combined_df)

idx = which(duplicated(names(combined_df)))
combined_df = combined_df[,-idx]

file_name <- paste("C:/Users/chery/Documents/BBD/Statcast/Pitching/custom_2021.csv",sep="")

write.csv( combined_df, file_name, row.names = FALSE)

dbDisconnect(my_temp_db)

conn <- dbConnect(RSQLite::SQLite(), "C:/Ubuntu/Shared/data/Baseball.db")

delcmd <- paste0("DELETE FROM StatcastPitchingSeason WHERE year = ", year )

if (length(combined_df) ) {
  dbExecute(conn, delcmd)
}

dbWriteTable(conn, "StatcastPitchingSeason", combined_df, append = TRUE )

dbDisconnect(conn)


#https://baseballsavant.mlb.com/leaderboard/statcast?type=batter&year=2020&position=&team=&min=q&csv=true

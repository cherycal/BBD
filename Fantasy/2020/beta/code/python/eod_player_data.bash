#!/bin/bash

CURRENTEPOCTIME=`date +"%Y%m%d-%H%M%S"`

echo $CURRENTEPOCTIME
cd /media/sf_Shared/BBD/Fantasy/2020/beta/code/python/
/usr/bin/python3 /media/sf_Shared/BBD/Fantasy/2020/beta/code/python/end_of_day_player_data_process.py > /media/sf_Shared/BBD/Fantasy/2020/beta/data/logs/eod_player_data_$CURRENTEPOCTIME.txt 2>&1

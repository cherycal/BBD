#!/bin/bash

CURRENTEPOCTIME=`date +'%Y%m%d-%H%M%S'`

echo $CURRENTEPOCTIME
cd /media/sf_Shared/BBD/Fantasy/2021/beta/code/pythonProject/
/usr/bin/python3 /media/sf_Shared/BBD/Fantasy/2021/beta/code/pythonProject/espn_player_info.py > /media/sf_Shared/BBD/Fantasy/2021/beta/data/logs/espn_player_info_$CURRENTEPOCTIME.txt 2>&1

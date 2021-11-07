#!/bin/bash

CURRENTEPOCTIME=`date +'%Y%m%d-%H%M%S'`

echo $CURRENTEPOCTIME
cd /media/sf_Shared/BBD/Fantasy/2021/prod/code/python/
/usr/bin/python3 /media/sf_Shared/BBD/Fantasy/2021/prod/code/python/statcast_event_level.py > /media/sf_Shared/BBD/Fantasy/2021/prod/data/logs/statcast_event_level_$CURRENTEPOCTIME.txt 2>&1

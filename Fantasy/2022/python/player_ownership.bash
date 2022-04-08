#!/bin/bash

CURRENTEPOCTIME=`date +"%Y%m%d-%H%M%S"`

echo $CURRENTEPOCTIME
cd /media/sf_Shared/BBD/Fantasy/2020/beta/code/python/
/usr/bin/python3 /media/sf_Shared/BBD/Fantasy/2020/beta/code/python/player_ownership.py > /media/sf_Shared/BBD/Fantasy/2020/beta/data/logs/player_ownership_$CURRENTEPOCTIME.txt 2>&1

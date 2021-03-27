#!/bin/bash

CURRENTEPOCTIME=`date +"%Y%m%d-%H%M%S"`

echo $CURRENTEPOCTIME
cd /media/sf_Shared/BBD/Fantasy/2020/beta/code/python/
/usr/bin/python3 /media/sf_Shared/BBD/Fantasy/2020/beta/code/python/roster_changes.py > /media/sf_Shared/BBD/Fantasy/2020/beta/data/logs/roster_changes_log_$CURRENTEPOCTIME.txt 2>&1

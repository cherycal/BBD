#!/bin/bash

CURRENTEPOCTIME=`date +"%Y%m%d-%H%M%S"`

echo $CURRENTEPOCTIME
cd /media/sf_Shared/first/site/push_notification
/usr/bin/python3 /media/sf_Shared/first/site/push_notification/rosters_w_changes.py > /media/sf_Shared/first/site/push_notification/logs/roster_changes_log_$CURRENTEPOCTIME.txt 2>&1

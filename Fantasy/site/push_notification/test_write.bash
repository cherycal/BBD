#!/bin/bash

CURRENTEPOCTIME=`date +"%Y%m%d-%H%M%S"`

echo $CURRENTEPOCTIME
/usr/bin/python3 /media/sf_Shared/pyt/scripts/push_notification/rosters_w_changes.py > /media/sf_Shared/pyt/scripts/push_notification/logs/log_file_$CURRENTEPOCTIME 2>&1

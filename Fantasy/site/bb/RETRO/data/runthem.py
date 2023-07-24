# -*- coding: utf-8 -*-
"""
Created on Sun Nov  1 20:57:41 2015

@author: cheryll
"""
# NOTE: This runs a Windows executable, MUST be run on Windows !!!
#
# http://www.retrosheet.org/game.htm
# Click on the proper year under
# Regular Season Event Files
# unzip to C:\Users\cheryll\Documents\bevent\ directory
# Run this script
# It will make a file called 2015ALL.CSV ( the year will be different )
# Copy that file to C:\Users\cheryll\Documents\Columbia\COMS3101LNX\ubuntu
# which is the linux share
# /home/cws2136/share/pyt in linux

# This does event files, do the .ROS files in linux
# Copy the .ROS files from C:\Users\cheryll\Documents\bevent\ to
# /home/cws2136/share/pyt/ROS/ directory
# C:\Users\cheryll\Documents\Columbia\COMS3101LNX\ubuntu\pyt\ROS in windows
# back up ROSMULTI.CSV
# in this directory, in Linux, run
# for i in *.ROS; do; cat $i >> ROSMULTI.CSV; done;
# copy this file to /home/cws2136/share/pyt/
# that's it
# Retrosheet disclaimer:
# The information used here was obtained free of
#     charge from and is copyrighted by Retrosheet.  Interested
#     parties may contact Retrosheet at "www.retrosheet.org".


import os

strgsn = ["ARI","ATL","CHN",'CIN','COL','LAN','MIA','MIL', \
            'NYN','PHI','PIT','SDN','SFN','SLN','WAS']
            
strgsa = ["ANA","BAL",'BOS',"CHA",'CLE','DET','HOU','KCA','MIN', \
             'NYA','OAK','SEA','TBA','TEX','TOR']
  
count = 0

years = [2014,2015,2013]

runcmd = 1


for y in years:

    for strg in strgsn:
        cmd = "BEVENT -y " + str(y) + " -f 0-6,8-9,12-13,16-17,26-40," + \
        "43-45,51,58-61,66-71,75-79 " + str(y) +  \
            strg + ".EVN >> " + str(y) + "ALL.CSV"
        print(cmd)
        if runcmd:
            os.system( cmd )
        count += 1
    
    for strg in strgsa:
        cmd = "BEVENT -y " + str(y) + " -f 0-6,8-9,12-13,16-17,26-40," + \
        "43-45,51,58-61,66-71,75-79 " + str(y) +  \
            strg + ".EVA >> " + str(y) + "ALL.CSV"
        print(cmd)
        if runcmd:
            os.system( cmd )
        count += 1
        
print(count)

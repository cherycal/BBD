__author__ = 'chance'

import os
import time
from datetime import datetime

from bs4 import BeautifulSoup

import push
import sqldb
import tools

inst = push.Push()
bdb = sqldb.DB('Baseball.db')

league_dict = {}
team_dict = {}
old_rosters = {}
new_rosters = {}
insert_list = []
now = datetime.now() # current date and time
date_time = now.strftime("%m/%d/%Y-%H:%M:%S")
out_date = now.strftime("%m%d%Y-%H%M%S")

platform = tools.get_platform()
current_dir = os.getcwd()
if (platform == "Windows"):
    outfile = current_dir + "\\logs\\log." + str(out_date)
elif (platform == "Linux" or platform == "linux"):
    outfile = current_dir + "/logs/log." + str(out_date)
else:
    print("OS platform " + platform + " isn't Windows or Linux. Exit.")
    exit(1)

print(outfile)
msg = ""


f = open(outfile, "w")

c = bdb.select("SELECT LeagueID, Name FROM Leagues where Active = 'True'")
for t in c:
    league_dict[t[0]] = t[1]


c = bdb.select("SELECT * FROM Rosters where LeagueID  in (SELECT LeagueID FROM Leagues where Active = 'True')")
for t in c:
    old_rosters[t[0]+':'+t[1]] = t[1]
    team_dict[t[1]] = t[2]


c = bdb.select("SELECT * FROM Leagues where Active = 'True'")

driver = tools.get_driver("headless")

for t in c:
    url = "http://fantasy.espn.com/baseball/league/rosters?leagueId=" + str(t[0])
    print (url)
    driver.get(url)
    time.sleep(20)

    html = driver.page_source
    soup = BeautifulSoup(html, "lxml")

    sections = soup.find_all("section")
    for section in sections:
        section_row = section.find_all('span')
        names = section.find_all('span', {'class': 'teamName truncate'})
        for name in names:
            pass

        tables = section.find_all("table", {'class': 'Table2__table'})

        for table in tables:
            table_rows = table.find_all('tr')
            for tr in table_rows:
                title = tr.find('span')
                a = tr.find_all('a')
                row = [i.text for i in a]
                print("Row: " + row )
                if (len(row)):
                    command = "INSERT INTO Rosters(Player, Team, LeagueID) VALUES ( \"" + row[0] + \
                              "\" ,\"" \
                                                                                       + \
                              name.text + "\"," + str(t[0]) + ")"
                    new_rosters[row[0]+':'+name.text] = name.text
                    insert_list.append(command)

players = len(insert_list)

minimum = 200
    
if ( players < minimum ):
    print("Not enough players in Rosters: " + str(players))
    msg += "Not enough players in Rosters"
    inst.push("Roster error: "+str(date_time), msg)
    time.sleep(2)
    inst.push("Roster error: "+str(date_time), msg)
else:
    print("Rosters appear to be full: " + str(players))
    print("Updating Rosters table")
    c = bdb.delete("DELETE FROM Rosters where LeagueID  in (SELECT LeagueID FROM Leagues where Active = 'True')")
    for command in insert_list:
        #print(command)
        bdb.insert(command)


for p in old_rosters:
    if new_rosters.get(p):
        if ( old_rosters[p] == new_rosters[p] ):
            #print(p, old_rosters[p], new_rosters[p] )
            pass
        else:
            #print("In old not in new: " + p, old_rosters[p], new_rosters[p] )
            msg += "DROPPED: " + p + ": " + old_rosters[p] + ", " + new_rosters[p]
            msg += "\n"
    else:
        #print("In old not in new: " + p)
        msg += "DROPPED: " + p
        msg += "\n"

for p in new_rosters:
    if ( old_rosters.get(p) ):
        pass
    else:
        #print("In new not in old: " + p, new_rosters[p])
        msg += "ADDED: " + p
        msg += "\n"

if (msg != ""):
    print("Msg: " + msg)
    inst.push("Roster changes: "+str(date_time), msg)
else:
    msg = "No changes"
    inst.push("Roster changes: " + str(date_time), msg)
    print("Msg: " + msg)

f.write(msg)

f.close()
driver.quit()
bdb.close()


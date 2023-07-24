# -*- coding: utf-8 -*-
"""
Created on Sat Oct 31 00:54:44 2015
# MLB data package
@author: Chance Steinberg, cws2136
"""
import csv
import getopt
import pickle
import sys

import requests
from bs4 import BeautifulSoup


class StatPack:
    def __init__(self):
        self.players = {}
        self.batters = {}
        self.pitchers = {}
        self.names = {}
        self.player_count = 0

    def roster(self, filename):
        with open(filename, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                id = row[0]
                self.name = str(row[2] + " " + row[1])
                if self.players.get(id) is None:
                    b = Batter(id, self.name)
                    p = Pitcher(id, self.name)
                    self.players[id] = id
                    self.names[self.name] = id
                    self.batters[id] = b
                    self.pitchers[id] = p
                    self.player_count += 1

    def new_player(self, id):
        self.players[id] = id
        print("New player: ", id, "Unknown")

    def get_player(self, id):
        return self.players[id]

    def get_batter(self, id):
        return self.batters[id]

    def get_pitcher(self, id):
        return self.pitchers[id]

    def get_players(self):
        return self.players

    def get_id(self, n):
        if self.names.get(n):
            return self.names[n]
        return 0

    def get_batter_by_name(self, n):
        if self.names.get(n):
            return self.get_batter(self.names[n])
        return 0

    def get_pitcher_by_name(self, n):
        if self.names.get(n):
            return self.get_batter(self.names[n])
        return 0


class Player:
    def __init__(self, id, n):
        self.id = id
        self.n = n
        self.pa = 0
        self.ab = 0
        self.r = 0
        self.h = 0
        self.h2 = 0
        self.h3 = 0
        self.hr = 0
        self.rbi = 0
        self.sb = 0
        self.cs = 0
        self.bb = 0
        self.ba = 0
        self.obp = 0
        self.slg = 0
        self.ops = 0
        self.tb = 0
        self.gdp = 0
        self.hbp = 0
        self.sh = 0
        self.sf = 0
        self.ibb = 0
        self.so = 0
        self.er = 0
        self.ur = 0
        self.ip = 0

    def name(self):
        return self.n

    def get_id(self):
        return self.id


class Batter(Player):
    def set_r(self, n):
        self.r += n

    def set_h(self, n):
        if n >= 1:
            self.h += 1
        if n == 2:
            self.h2 += 1
        elif n == 3:
            self.h3 += 1
        elif n == 4:
            self.hr += 1
        self.tb += n

    def bref_h(self, n):
        self.h += int(n[0])
        self.h2 += int(n[1])
        self.h3 += int(n[2])
        self.hr += int(n[3])
        self.tb += int(n[4])

    def set_ab(self, n):
        self.ab += n

    def set_pa(self, n):
        self.pa += n

    def set_rbi(self, n):
        self.rbi += n

    def set_bb(self, n):
        self.bb += 1
        self.ibb += n

    def bref_bb(self, n):
        self.bb += int(n[0])
        self.ibb += int(n[1])

    def set_hbp(self, n):
        self.hbp += n

    def set_sh(self, n):
        self.sh += n

    def set_sf(self, n):
        self.sf += n

    def set_sb(self, n):
        self.sb += n

    def set_cs(self, n):
        self.cs += n

    def set_so(self, n):
        self.so += n

    def stats(self):
        if self.pa > 0:
            return [self.id, self.name(), self.pa, self.ab, self.r, self.h, self.h2, self.h3, self.hr, self.rbi,
                    self.sb, self.cs, self.bb, self.so, self.tb]

    def bref_stats(self, stats):
        [pa, ab, r, h, h2, h3, hr, rbi, sb, cs, bb, so] = stats[3:15]
        [tb, gdp, sh, sf, ibb] = stats[20:25]
        if int(pa) > 0:
            self.set_pa(int(pa))
            self.set_ab(int(ab))
            self.bref_h([h, h2, h3, hr, tb])
            self.set_r(int(r))
            self.set_rbi(int(rbi))
            self.set_sb(int(sb))
            self.set_cs(int(cs))
            self.set_so(int(so))
            self.bref_bb([bb, ibb])
            self.set_sh(int(sh))
            self.set_sf(int(sf))

            return [self.id, self.name(), self.pa, self.ab, self.r, self.h, \
                    self.h2, self.h3, self.hr, \
                    self.rbi, self.sb, self.cs, self.bb, self.so, self.tb]


class Pitcher(Player):
    def set_r(self, n):
        self.r += int(n)

    def set_ur(self, n):
        self.ur += int(n)

    def set_er(self, n):
        self.er += int(n)

    def set_h(self, n):
        if n >= 1:
            self.h += 1
        if n == 2:
            self.h2 += 1
        elif n == 3:
            self.h3 += 1
        elif n == 4:
            self.hr += 1
        self.tb += n

    def bref_h(self, n):
        self.h += n

    def set_hr(self, n):
        self.hr += n

    def set_so(self, n):
        self.so += n

    def set_ip(self, n):
        self.ip += int(n) / 3.0

    def bref_ip(self, n):
        [i, t] = n.split('.')
        ip = float(i) + float(t) / 3

        self.ip += ip

    def set_bb(self, n):
        self.bb += 1
        self.ibb += int(n)

    def bref_bb(self, n):
        self.bb += int(n[0])
        self.ibb += int(n[1])

    def stats(self):
        if self.ip > 0:
            return [self.id, self.name(), str(int(self.ip)) + "." + str(int((self.ip - int(self.ip)) * 3)), self.h,
                    self.r, self.r - self.ur, self.hr,
                    self.bb, self.ibb, self.so]

    def bref_stats(self, stats):
        [ip, h, r, er, hr, bb, ibb, so] = stats[12:20]
        if float(ip) > 0:
            self.bref_ip(ip)
            self.bref_h(int(h))
            self.set_r(int(r))
            self.set_er(int(er))
            self.set_hr(int(hr))
            self.bref_bb([int(bb), int(ibb)])
            self.set_so(int(so))
            ip = int((self.ip - int(self.ip)) * 3.5)
            ip = str(int(self.ip)) + "." + str(ip)

        return [self.id, self.name(), '%5s' % ip, self.h, self.r, self.er, self.hr, self.bb, self.ibb, self.so]


def get_bref(url, pick, path, stat_pack, bp):
    player_dict = {}
    # Load from web is slow
    if pick and path:
        pkl_file = open(path, 'rb')
        r = pickle.load(pkl_file)
    else:
        print("Retrieving: " + url)
        # get data and convert to string
        r = requests.get(url)
        output1 = open(path, 'wb')
        pickle.dump(r, output1)

    soup = BeautifulSoup(r.content)
    trlist = soup.find_all("tr")

    for tritem in trlist:
        tdlist = tritem.find_all("td")
        stats = []
        i = 0
        if len(tdlist) > 0 and tdlist[0].get_text() != "":
            name = tdlist[1].get_text().encode('ascii', 'replace')
            if len(str(name)) > 5:
                lg = tdlist[3].get_text()
                name = name.replace("?", " ")
                name = str(name)
                name = name.replace("*", "")
                name = name.replace("#", "")
                if stat_pack.get_id(name):
                    id = stat_pack.get_id(name)
                    b = stat_pack.get_batter(id)
                    p = stat_pack.get_pitcher(id)
                    stats.append(name)
                    if lg == "TOT":
                        continue
                    stats.append(lg)
                    for tditem in tdlist:
                        if 5 <= i <= 28:
                            stats.append(tditem.get_text())
                        i += 1
                    if bp == "Bat":
                        bs = b.bref_stats(stats)
                        if bs is not None:
                            player_dict[bs[0]] = bs
                    else:
                        ps = p.bref_stats(stats)
                        if ps is not None:
                            player_dict[ps[0]] = ps
                else:
                    print(name + " not found")
    return player_dict


def rf(path):
    # lc is linecount
    lc = 0
    with open(path, 'r') as f:
        while True:
            lc += 1
            ln = f.readline()
            if ln == '':
                break
            print(ln)


def events(filename, StatPack):
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            id = row[9]
            b = StatPack.get_batter(id)
            pitch_id = row[11]
            p = StatPack.get_pitcher(pitch_id)
            playid = row[21]
            # Total bases
            tb = int(row[24])
            # RBI
            rb = int(row[28])
            outs = int(row[27])
            if row[22] == 'T':
                b.set_pa(1)
            if row[23] == 'T':
                b.set_ab(1)
            if row[25] == 'T':
                b.set_sh(1)
            if row[26] == 'F':
                b.set_sf(1)
            if rb:
                b.set_rbi(rb)
            if outs:
                p.set_ip(outs)
            if playid == '14':
                # walk
                b.set_bb(0)
                p.set_bb(0)
            # Intentional walk
            elif (playid == '15'):
                b.set_bb(1)
                p.set_bb(1)
            elif (playid == '3'):
                # Strikeout
                b.set_so(1)
                p.set_so(1)
            else:
                # Hit for tb bases
                b.set_h(tb)
                p.set_h(tb)

            # Stolen bases
            i = 36
            while i < 39:
                if ((row[i]) == 'T'):
                    StatPack.get_batter(row[i - 23]).set_sb(1)
                i += 1
            i = 39
            while i < 42:
                if ((row[i]) == 'T'):
                    StatPack.get_batter(row[i - 26]).set_cs(1)
                i += 1

            # Run scoring
            if tb >= 4:
                b.set_r(1)
                StatPack.get_pitcher(row[11]).set_r(1)
                if tb >= 5:
                    StatPack.get_pitcher(row[11]).set_ur(1)
            i = 33
            while i < 36:
                if int(row[i]) >= 4:
                    StatPack.get_batter(row[i - 20]).set_r(1)
                    StatPack.get_pitcher(row[i + 9]).set_r(1)
                    if int(row[i]) > 4:
                        StatPack.get_pitcher(row[i + 9]).set_ur(1)
                i += 1

            if StatPack.players.get(id) is None:
                print("Unknown player: " + id)
                StatPack.new_player(id)


def load_events(StatPack, event_file):
    events(event_file, StatPack)


def load_event_codes(filename):
    code = {}
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            code[row[0]] = row[1]
    return code


def load_retrosheet_data(StatPack):
    code = load_event_codes("event_codes.csv")


def build_rosters(StatPack, roster_file):
    StatPack.roster(roster_file)


def load_retrosheet_events(stat_pack, event_file):
    pitcher_dict = {}
    batter_dict = {}

    load_events(stat_pack, event_file)

    players = stat_pack.get_players()
    for p in players:
        b = stat_pack.get_batter(p)
        if b.stats() != None:
            batter_dict[b.get_id()] = b.stats()

        t = stat_pack.get_pitcher(p)
        if t.stats() != None:
            pitcher_dict[t.get_id()] = t.stats()

    return [batter_dict, pitcher_dict]


def load_web_data(stat_pack, year, use_pickle):
    pitcher_dict = {}
    batter_dict = {}

    bat_url = 'http://www.baseball-reference.com/leagues/MLB/' + str(year) + \
              '-standard-batting.shtml'

    pitch_url = 'http://www.baseball-reference.com/leagues/MLB/' + str(year) + \
                '-standard-pitching.shtml'

    batter_dict = get_bref(bat_url, use_pickle, 'key.pickle.' + str(year), stat_pack, "Bat")

    pitcher_dict = get_bref(pitch_url, use_pickle, 'key.pickle.' + str(year), stat_pack, "Pitch")

    return [batter_dict, pitcher_dict]


def show_all(source):
    [bat, pitch] = source
    print()
    print('%-22s %5s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s' % \
          ("Player name", "PA", "AB", "R", "H", "2B", "3B", "HR", "RBI", "SB", "CS", "BB", "SO", "TB"))
    print("")
    for i in bat.keys():
        if bat.get(i) != None:
            print('%-22s %5s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s' % \
                  tuple(bat[i][1:]))
    print("")
    print("")
    print('%-22s %5s %4s %4s %4s %4s %4s %4s %4s' % \
          ("Name", "IP", "H", "R", "ER", "HR", "BB", "IBB", "SO"))
    for i in pitch.keys():
        if pitch.get(i) != None:
            print('%-22s %5s %4s %4s %4s %4s %4s %4s %4s' % \
                  tuple(pitch[i][1:]))


def reconcile(r, b, tolerance):
    [r_bat, r_pitch] = r
    [b_bat, b_pitch] = b

    total_batters = 0
    mismatch = 0
    missing = 0
    missed = {}
    print("Summary of mismatches with total tolerance of " + \
          str(tolerance) + ":")
    print()
    print('Source  %-22s %5s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s' % \
          ("Player name", "PA", "AB", "R", "H", "2B", "3B", "HR", "RBI", "SB", "CS", "BB", "SO", "TB"))
    print("")
    for i in b_bat.keys():
        total_batters += 1
        if r_bat.get(i) is not None:
            if abs(sum(b_bat[i][3:]) - sum(r_bat[i][3:])) > tolerance:
                print('BRef:   %-22s %5s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s' % \
                      tuple(b_bat[i][1:]))
                print('Retro:  %-22s %5s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s' % \
                      tuple(r_bat[i][1:]))
                print()
                mismatch += 1
        else:
            missed[b_bat[i][1]] = 1
            missing += 1

    for i in r_bat.keys():
        if b_bat.get(i) is None:
            missed[r_bat[i][1]] = 1
            missing += 1

    print("Total batters: " + str(total_batters))
    print("Mismatches: " + str(mismatch))
    print()

    total_pitchers = 0
    mismatch = 0
    print('Source  %-22s %5s %4s %4s %4s %4s %4s %4s %4s' % \
          ("Name", "IP", "H", "R", "ER", "HR", "BB", "IBB", "SO"))
    for i in b_pitch.keys():
        total_pitchers += 1
        if r_pitch.get(i) is not None:
            if abs(sum(b_pitch[i][4:]) - sum(r_pitch[i][4:])) > tolerance:
                print('BRef:   %-22s %5s %4s %4s %4s %4s %4s %4s %4s' % \
                      tuple(b_pitch[i][1:]))
                print('Retro:  %-22s %5s %4s %4s %4s %4s %4s %4s %4s' % \
                      tuple(r_pitch[i][1:]))
                print()
                mismatch += 1
        else:
            missed[b_pitch[i][1]] = 1
            missing += 1

    for i in r_pitch.keys():
        if b_pitch.get(i) is None:
            missed[r_pitch[i][1]] = 1
            missing += 1

    print("Total pitchers: " + str(total_pitchers))
    print("Mismatches: " + str(mismatch))
    print()
    print("Missed players:")
    print()
    for i in missed.keys():
        print(i)


def run(args, opts):
    use_pickle = 1
    tolerance = 1
    roster_file = "ROSMULTI.CSV"
    year = "2012"

    for a in opts:
        if a[0] == '-t':
            tolerance = int(a[1])
            if (tolerance == 99999):
                tolerance = -1
        if a[0] == '-y':
            year = str(a[1])
        if a[0] == '-l':
            use_pickle = 0
        if a[0] == '-h':
            usage()
            return

    print("Year: " + year)

    event_file = year + "ALL.CSV"
    pickle_suffix = ".pickle." + year

    pickleroot = '../data/'

    if use_pickle:

        picklepath = pickleroot + 'retro' + pickle_suffix
        pkl_file = open(picklepath, 'rb')
        r = pickle.load(pkl_file)

        picklepath = pickleroot + 'bref' + pickle_suffix
        pkl_file = open(picklepath, 'rb')
        b = pickle.load(pkl_file)

    else:

        picklepath = pickleroot + 'retro' + pickle_suffix

        bref = StatPack()
        retro = StatPack()

        build_rosters(retro, roster_file)
        build_rosters(bref, roster_file)

        r = load_retrosheet_events(retro, event_file)
        output1 = open(picklepath, 'wb')
        pickle.dump(r, output1)

        picklepath = pickleroot + 'bref' + pickle_suffix
        b = load_web_data(bref, year, use_pickle)
        output1 = open(picklepath, 'wb')
        pickle.dump(b, output1)

    for a in opts:
        if (a[0] == '-b'):
            show_all(b)
            return
        elif (a[0] == '-r'):
            show_all(r)

    reconcile(r, b, tolerance)


def usage():
    print("proj.py [ -h -b -r -l -t tolerance -y year]")
    print("")
    print("Notes: -t tolerance: is the minimum total difference in statistics")
    print("       allowed before it is reported. The default is 1 ")
    print("")
    print("       examples:")
    print("       -t 1 means that data is considered a match if there is")
    print("        a difference of 1 when all stats are added together")
    print("       -t 99999 shows all comparisons")
    print("       -t 0 prints all differences ")
    print("")
    print("       -l forgoes using pickled data, which runs faster")
    print("       running with -l gets data from flat files")
    print("       and the internet.")
    print("")
    print("       -b show all baseball-reference data")
    print("")
    print("       -r show all retrosheet data")
    print("")
    print("       -y year")


# C:\Users\cheryll\Documents\bevent/runthem.py creates the event files
# 1) Load event files from retrosheet
# 2) Reformat them with runthem.py
# 3) Move them to this directory
# 4) Do .ROS files in linux ( see runthem for details )

def main(argv):
    opts, args = getopt.getopt(argv, "hlbrt:y:", [])
    # print(os.name) # posix (LINUX) or nt (windows) 
    # return
    run(args, opts)


if __name__ == "__main__":
    main(sys.argv[1:])

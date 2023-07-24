__author__ = 'chance'

import csv

file_name = 'player_map.csv'

with open(file_name, 'r') as csv_file:
    csv_reader = csv.reader(csv_file)

    line_count = 0

    for row in csv_reader:
        if line_count == 0:
            print(f'Column names are {", ".join(row)}')
            line_count += 1
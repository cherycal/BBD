from pybaseball import statcast

data = statcast(start_dt='2020-08-10', end_dt='2020-08-11')

print(data.head(10).values)

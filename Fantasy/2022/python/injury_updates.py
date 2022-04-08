import sys

sys.path.append('./modules')
import push
import fantasy
from datetime import datetime

mode = "PROD"
fantasy = fantasy.Fantasy(mode)
bdb = fantasy.get_db()
ts = datetime.now()  # current date and time
#formatted_date_time = ts.strftime("%Y%m%d-%I%M%S.f")
date8 = ts.strftime("%Y%m%d")

inst = push.Push()

def main():
	fantasy.run_injury_updates()

if __name__ == "__main__":
	main()

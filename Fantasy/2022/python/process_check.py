import logging
import sys
from pathlib import Path

p = Path.cwd()
log_dir = p / 'logs'
log_dir.mkdir(mode=0o755, exist_ok=True)
log_file = log_dir / 'process_check_log.txt'
log_filename = str(log_file)

sys.path.append('./modules')
import sqldb
import push
import time
from datetime import datetime

inst = push.Push()
bdb = sqldb.DB('Baseball.db')


class Check:
	def __init__(self):
		self._is_ok = bool
		self._msg = ""

	def set_is_ok(self, b):
		self._is_ok = b

	def set_msg(self, m):
		self._msg = m

	def is_ok(self):
		return self._is_ok

	def msg(self):
		return self._msg


def do_check():
	# return_string = ""
	check = Check()
	# return_obj = dict()
	# return_obj['is_ok'] = bool
	# return_obj['msg'] = ""

	current_time = datetime.now()  # current date and time
	# current_time_str = current_time.strftime("%Y%m%d%H%M%S")

	cmd = "SELECT * FROM ProcessUpdateTimes where Active = 1"
	rows = list()
	try:
		names, rows = bdb.select_w_cols(cmd)
	except Exception as ex:
		print(str(ex))
		inst.push("DB error in process_check", str(ex))
		inst.tweet("DB error in process_check\n" + cmd + ":\n" + str(ex))

	check_str = ""
	maxdiff = 0

	if len(rows) == 0:
		print("There are no processes to check. Exiting.")
		exit(0)

	for row in rows:
		process_name = row[0]
		update_int = str(row[1])
		update_time = datetime.strptime(update_int, "%Y%m%d%H%M%S")
		diff = (current_time - update_time).total_seconds()
		maxdiff = max(maxdiff, diff)
		check_str += f'{process_name} was last updated at {update_time.strftime("%I:%M %p")}, {diff:.2f} seconds ago'
		check_str += "\n"
		logging.info(check_str)

	check_str += "\n"
	#return_obj['msg'] = check_str
	check.set_msg(check_str)
	if maxdiff > 100:
		#return_obj['is_ok'] = False
		check.set_is_ok(False)
	else:
		#return_obj['is_ok'] = True
		check.set_is_ok(True)

	return check


def main():

	logging.basicConfig(filename=log_filename,
	                    level=logging.DEBUG,
	                    filemode='w',
	                    format='%(asctime)s:%(levelname)s:%(message)s:\n%(pathname)s:%(funcName)s')
	ts = datetime.now()  # current date and time
	time_of_day = int(ts.strftime("%H%M%S"))
	end_time = 235500
	count = 0

	while time_of_day < end_time:
		ts = datetime.now()  # current date and time
		time_of_day = int(ts.strftime("%H%M%S"))
		check = do_check()
		check_str = check.msg()

		if check.is_ok():
			pass
		else:
			inst.push("PROCESS ALERT", check_str)
			inst.tweet("PROCESS ALERT:\n*****************\n*****************\n{}".format(check_str))

		count_check = count % 1
		print(check_str)
		if count_check == 0:
			inst.tweet(check_str)
		count += 1
		time.sleep(480)


if __name__ == "__main__":
	main()

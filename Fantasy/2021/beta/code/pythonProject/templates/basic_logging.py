__author__ = 'chance'

import sys
from pathlib import Path

sys.path.append('../modules')
import tools
import colorlog


p = Path.cwd()
log_dir = p / 'logs'
log_dir.mkdir(mode=0o755, exist_ok=True)
log_file = log_dir / 'log.txt'
log_filename = str(log_file)

print("Log file is {} ".format(log_file))

# DEBUG: Detailed information, typically of interest only when diagnosing problems.

# INFO: Confirmation that things are working as expected.

# WARNING: An indication that something unexpected happened,
# or indicative of some problem in the near future (e.g. ‘disk space low’).
# The software is still working as expected.

# ERROR: Due to a more serious problem, the software has not been able
# to perform some function.

# CRITICAL: A serious error, indicating that the program itself may be
# unable to continue running.

def main():
	logger_instance = tools.get_logger()
	logger_instance.debug("Hello, debug")

	logformat = '%(log_color)s%(asctime)s:%(levelname)s:%(funcName)s:%(lineno)d:%(message)s:%(pathname)s\n'
	logger = colorlog.getLogger()
	logger.setLevel(colorlog.colorlog.logging.DEBUG)

	handler = colorlog.StreamHandler()
	handler.setFormatter(colorlog.ColoredFormatter(logformat))
	logger.addHandler(handler)

	logger.debug("Debug message")
	logger.info("Information message")
	logger.warning("Warning message")
	logger.error("Error message")
	logger.critical("Critical message")

	# log = logging.getLogger("my-logger")
	# logging.basicConfig(filename=log_filename,
	#                     level=logging.INFO,
	#                     filemode='w',
	#                     format='%(asctime)s:%(levelname)s::%(name)s:%(message)s:\n%(pathname)s:%(funcName)s')
	# logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
	# logging.debug("Hello, debug")
	# logging.info("Hello, info")
	# logging.warning("Hello, warning")

	# logger_instance = logging.getLogger("my-logger")

	# logger_instance.setLevel(logging.DEBUG)
	#
	# formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
	# file_handler = logging.FileHandler('sample.log')
	# stream_handler = logging.StreamHandler()
	#
	# file_handler.setLevel(logging.ERROR)
	# file_handler.setFormatter(formatter)
	#
	# stream_handler.setFormatter(formatter)
	#
	# logger_instance.addHandler(file_handler)
	# logger_instance.addHandler(stream_handler)


# try:
#         result = x / y
#     except ZeroDivisionError:
#         logger.exception('Tried to divide by zero')
#     else:
#         return result

# print("Hello {}".format(0))


if __name__ == "__main__":
	main()

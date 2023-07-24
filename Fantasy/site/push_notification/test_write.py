__author__ = 'chance'

from datetime import datetime

now = datetime.now() # current date and time
date_time = now.strftime("%m/%d/%Y-%H:%M:%S")
out_date = now.strftime("%m%d%Y-%H%M%S")
outfile = "log." + str(out_date)
print(outfile)
msg = "Hello"

f = open(outfile, "w")

f.write(msg)

f.close()

exit(0)
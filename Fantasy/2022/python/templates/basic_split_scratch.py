import re
import sys

sys.path.append('../modules')

def process_oddsline(text):
	splittext = re.split('(SF)|(Giants)| +|\xa0|-|\+',text)
	print(text)
	print(splittext)
	res = [i for i in splittext if i]
	return res


text = " 8:07PMSF GiantsKevin Gausman  -1.5+116     O 8-112     -125.0"
print(process_oddsline(text))
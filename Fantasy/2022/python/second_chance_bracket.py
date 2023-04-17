__author__ = 'chance'
import json
import sys
import time
import urllib.request
from datetime import datetime

sys.path.append('./modules')
import sqldb
import push
import fantasy
from io import BytesIO
import pycurl
import certifi

inst = push.Push()
bdb = sqldb.DB('Baseball.db')
fantasy = fantasy.Fantasy()

now = datetime.now()  # current date and time
date_time = now.strftime("%Y%m%d%H%M%S")
date8 = now.strftime("%Y%m%d")
statcast_date = now.strftime("%Y-%m-%d")

sleep_interval = 1
# Selenium
#driver = tools.get_driver("headless")

msg = ""

# https://fantasy.espn.com/games/mens-tournament-challenge-second-chance-bracket-2023/group?id=9b1350bd-973e-49d9-8d95-d94659d2d3c0

def get_brackets():
	bracket_list = dict()
	url_name = f"https://fantasy.espn.com/apis/v1/challenges/mens-tournament-challenge-second-chance-bracket-2023/groups/9b1350bd-973e-49d9-8d95-d94659d2d3c0?view=chui_default_group&platform=chui"

	headers = ['authority: fantasy.espn.com',
	           'accept: application/json',
	           'referrer: https://fantasy.espn.com/games/mens-tournament-challenge-second-chance-bracket-2023/bracket?id=7cd43a30-c8e6-11ed-a2cf-af959a23db0d',
	           'referrerPolicy: strict-origin-when-cross-origin',
	           'cookie: CHUI_themeScheme=light; region=ccpa; _dcf=1; country=us; userZip=92103; country=us; hashedIp=36aac583dad4af9a45f4d49bc0fa3739e35e481c13a74ee0a82adbc02b3d91b3; _cb=BUPLU1CQkH0OinzKD; _cb_svref=https%3A%2F%2Ffantasy.espn.com%2Ftournament-challenge-bracket%2F2023%2Fen%2Fentry%3FentryID%3D86180707; s_ensCDS=0; s_ensRegion=ccpa; s_ensNSL=0; s_ecid=MCMID%7C64395968896969124333073655265355968658; AMCVS_EE0201AC512D2BE80A490D4C%40AdobeOrg=1; AMCV_EE0201AC512D2BE80A490D4C%40AdobeOrg=-330454231%7CMCIDTS%7C19440%7CMCMID%7C64395968896969124333073655265355968658%7CMCAID%7CNONE%7CMCOPTOUT-1679545761s%7CNONE%7CMCAAMLH-1680143362%7C9%7CMCAAMB-1680143362%7Cj8Odv6LonN4r3an7LhD3WZrU1bUpAkFkkiY1ncBR96t2PTI%7CvVersion%7C3.1.2; usprivacy=1YNY; s_c24_s=First%20Visit; s_cc=true; s_gpv_pn=fantasy%3Abasketball%3Abracket%3AOpponent%20Entry; s_c6=1679538563654-New; IR_gbd=espn.com; IR_9070=1679538563784%7C0%7C1679538563784%7C%7C; s_c24=1679538575705; s_sq=wdgespcom%252Cwdgespge%3D%2526pid%253Dfantasy%25253Abasketball%25253Abracket%25253AOpponent%252520Entry%2526pidt%253D1%2526oid%253Dfunctionli%252528%252529%25257B%25257D%2526oidt%253D2%2526ot%253DSUBMIT; ESPN-ONESITE.WEB-PROD.api=fciey6SN4HeLWHO0EG+thCnmSJ7OuD1uTqh8iq7W6xCJqov1wWnfD437mrLo7ptVzAqNqZskw32nRoUVHF7JdQFp6p1o; device_9de3f653=4a03f1b8-50b1-44dc-b454-990fb466c9bb; ESPN-ONESITE.WEB-PROD.ts=2023-03-23T02:59:52.652Z; ESPN-ONESITE.WEB-PROD.token=5=eyJhY2Nlc3NfdG9rZW4iOiJlY2Y4NDcxN2JlZjU0OTc3YmNiZGI4MTUyZGVlMWVhMSIsInJlZnJlc2hfdG9rZW4iOiJkNjQ2NTUzNTVjMzg0ZTQ1YmEyOTc1ZDQyMzk1NmVkMSIsInN3aWQiOiJ7NDI2RUNCNzQtOTQ5MC00MzNFLTkwMTgtQTVGNDA3Qjc1QzhCfSIsInR0bCI6ODY0MDAsInJlZnJlc2hfdHRsIjoxNTU1MjAwMCwiaGlnaF90cnVzdF9leHBpcmVzX2luIjoxNzk5LCJpbml0aWFsX2dyYW50X2luX2NoYWluX3RpbWUiOjE2Nzk1Mzg1OTIwNDIsImlhdCI6MTY3OTUzODU5MjAwMCwiZXhwIjoxNjc5NjI0OTkyMDAwLCJyZWZyZXNoX2V4cCI6MTY5NTA5MDU5MjAwMCwiaGlnaF90cnVzdF9leHAiOjE2Nzk1NDAzOTEwMDAsInNzbyI6bnVsbCwiYXV0aGVudGljYXRvciI6ImRpc25leWlkIiwibG9naW5WYWx1ZSI6bnVsbCwiY2xpY2tiYWNrVHlwZSI6bnVsbCwic2Vzc2lvblRyYW5zZmVyS2V5IjoiM1JWNzBfWWpGSjJiQkpiN2RZbWpENXBqM2dNZk14R2Yza1RHdTZjU2pzM0cwNDBoNkJHM2RzZ00wZ2hTNlBLYlZ0TDZTcXY2T25vTmUxZ1JIaDZoRUt1N1BDZHRGaU51eW1fR1JXc1J0UjdxcFlJd1MtYyIsImNyZWF0ZWQiOiIyMDIzLTAzLTIzVDAyOjI5OjUyLjY0OVoiLCJsYXN0Q2hlY2tlZCI6IjIwMjMtMDMtMjNUMDI6Mjk6NTIuNjQ5WiIsImV4cGlyZXMiOiIyMDIzLTAzLTI0VDAyOjI5OjUyLjY0OVoiLCJyZWZyZXNoX2V4cGlyZXMiOiIyMDIzLTA5LTE5VDAyOjI5OjUyLjY0OVoiLCJibHVlX2Nvb2tpZSI6bnVsbH0=|eyJraWQiOiJxUEhmditOL0tONE1zYnVwSE1PWWxBc0pLcWVaS1U2Mi9DZjNpSm1uOEJ6dzlwSW5xbTVzUnc9PSIsImFsZyI6IlJTMjU2In0.eyJpc3MiOiJodHRwczovL2F1dGhvcml6YXRpb24uZ28uY29tIiwic3ViIjoiezQyNkVDQjc0LTk0OTAtNDMzRS05MDE4LUE1RjQwN0I3NUM4Qn0iLCJhdWQiOiJFU1BOLU9ORVNJVEUuV0VCLVBST0QiLCJleHAiOjE2Nzk2MjQ5OTIsImlhdCI6MTY3OTUzODU5MiwianRpIjoiMzR6aHo0WlRJR0VqbllXck0yUTRGQSIsIm5iZiI6MTY3OTUzODUzMiwiYV90eXAiOiJPTkVJRF9UUlVTVEVEIiwiYV9jYXQiOiJHVUVTVCIsImF0ciI6ImRpc25leWlkIiwic2NvcGVzIjpbImR0c3MtZW50aXRsZW1lbnQtdXNlci1hZG1pbiIsIkFVVEhaX0dVRVNUX1NFQ1VSRURfU0VTU0lPTiJdLCJjX3RpZCI6IjEzMjQiLCJpZ2ljIjoxNjc5NTM4NTkyMDQyLCJodGF2IjoyLCJodGQiOjE4MDAsInJ0dGwiOjE1NTUyMDAwLCJlbWFpbCI6ImNoYW5jZV9zdEB5YWhvby5jb20ifQ.ElQv40QcRrdTJNoIUXxhh74efmvUIFkjp7mPlCHe7lXy4AGFMjhXXIGMJsakoSV-QPLQdK12PfXSCu2m63EptxNl2DOmPFB6pj_U8q9iurx8iQyh4J5AjwMz7Q26kH4KxPxsWjqxpx3W5vu4sYZLwqXs4dP4Xk9yVNTc99d0eiL71JJTgnc2133MCB_Smnxj0YvRXTjwGGOYjO-8yZPnev8ZpH1poRfzSJKZHvuze4TzWbhCnm3sMNXbkDgYWTMunV77tjrn5m9n_MlA4bVZbtOkHQrsUS9-ny-dJtKH5_B-83nTEB0Xo3bi52ZmFWvnpfO2309A13-du_8Jt_50aA; ESPN-ONESITE.WEB-PROD-ac=XUS; SWID={426ECB74-9490-433E-9018-A5F407B75C8B}; SWID_NT=0; _chartbeat2=.1679538561274.1679538596054.1.Bkna8YBfLhV-DCscTICsXYCuCTqQY.3; OptanonConsent=isGpcEnabled=0&datestamp=Wed+Mar+22+2023+19%3A29%3A56+GMT-0700+(Pacific+Daylight+Time)&version=202212.1.0&isIABGlobal=false&hosts=&consentId=06492cfc-a530-44e5-8b2e-74866d5a5fd9&interactionCount=1&landingPath=https%3A%2F%2Ffantasy.espn.com%2Fgames%2Fmens-tournament-challenge-second-chance-bracket-2023%2Fbracket%3Fid%3D7cd43a30-c8e6-11ed-a2cf-af959a23db0d&groups=C0001%3A1%2CC0003%3A1%2CSSPD_BG%3A1%2CC0002%3A1%2CC0004%3A1%2CC0005%3A1; espn_s2=AEA8qRTgMkj3wdtSuDSHzWT6Gsb5KNxO2MaKja5trgFWIQ4SotRbtUFA7yzTQcmU3DSchg7TNe7ucN9pWX0ifsEaQEhd2Syj%2Fyhhd6ultT9GoutLgYU8ie3oHnHHat%2BZSf14B%2F4hq7buffk1kqAKwImmc8AxJ1v6WHdC1T3Q8gepmNCNy7p63mENfIKLXLoztnk2gKfTOr%2Ft7uHh9C29ykv9xsM4yLIEXZPZ7bawyp9TGZBY9d2fC2qVoFVY7V6Gyp7Ejt7I6c6z14HGziLNYj%2FefP%2Fld1%2BXsPIYN1OSjFNODw%3D%3D; ESPN-ONESITE.WEB-PROD.idn=009d66d834'
	           'credentials: include']

	print(f"get_brackets with {url_name}")

	try:
		buffer = BytesIO()
		c = pycurl.Curl()
		c.setopt(c.URL, url_name)
		c.setopt(c.HTTPHEADER, headers)
		c.setopt(c.WRITEDATA, buffer)
		c.setopt(c.CONNECTTIMEOUT, 1000)
		c.setopt(c.CAINFO, certifi.where())
		c.perform()
		c.close()
		data = buffer.getvalue()
		json_data = json.loads(data)
		#print(json_data)
		brackets = json_data['entries']
		for bracket in brackets:
			bracket_id = bracket['id']
			bracket_name = bracket['name']
			bracket_list[bracket_id] = bracket_name
			print(bracket_id)
			print('')

	except Exception as ex:
		print(f'Exception in get_brackets {ex}')

	return bracket_list



def get_picks(idmap, bracket_id, bracket_name):

	pick_names = list()
	url_name = f"https://fantasy.espn.com/apis/v1/challenges/225/entries/{bracket_id}"
	headers = ['authority: fantasy.espn.com',
	           'accept: application/json',
	           'referrer: https://fantasy.espn.com/games/mens-tournament-challenge-second-chance-bracket-2023/bracket?id=7cd43a30-c8e6-11ed-a2cf-af959a23db0d',
	           'referrerPolicy: strict-origin-when-cross-origin',
	           'cookie: CHUI_themeScheme=light; region=ccpa; _dcf=1; country=us; userZip=92103; country=us; hashedIp=36aac583dad4af9a45f4d49bc0fa3739e35e481c13a74ee0a82adbc02b3d91b3; _cb=BUPLU1CQkH0OinzKD; _cb_svref=https%3A%2F%2Ffantasy.espn.com%2Ftournament-challenge-bracket%2F2023%2Fen%2Fentry%3FentryID%3D86180707; s_ensCDS=0; s_ensRegion=ccpa; s_ensNSL=0; s_ecid=MCMID%7C64395968896969124333073655265355968658; AMCVS_EE0201AC512D2BE80A490D4C%40AdobeOrg=1; AMCV_EE0201AC512D2BE80A490D4C%40AdobeOrg=-330454231%7CMCIDTS%7C19440%7CMCMID%7C64395968896969124333073655265355968658%7CMCAID%7CNONE%7CMCOPTOUT-1679545761s%7CNONE%7CMCAAMLH-1680143362%7C9%7CMCAAMB-1680143362%7Cj8Odv6LonN4r3an7LhD3WZrU1bUpAkFkkiY1ncBR96t2PTI%7CvVersion%7C3.1.2; usprivacy=1YNY; s_c24_s=First%20Visit; s_cc=true; s_gpv_pn=fantasy%3Abasketball%3Abracket%3AOpponent%20Entry; s_c6=1679538563654-New; IR_gbd=espn.com; IR_9070=1679538563784%7C0%7C1679538563784%7C%7C; s_c24=1679538575705; s_sq=wdgespcom%252Cwdgespge%3D%2526pid%253Dfantasy%25253Abasketball%25253Abracket%25253AOpponent%252520Entry%2526pidt%253D1%2526oid%253Dfunctionli%252528%252529%25257B%25257D%2526oidt%253D2%2526ot%253DSUBMIT; ESPN-ONESITE.WEB-PROD.api=fciey6SN4HeLWHO0EG+thCnmSJ7OuD1uTqh8iq7W6xCJqov1wWnfD437mrLo7ptVzAqNqZskw32nRoUVHF7JdQFp6p1o; device_9de3f653=4a03f1b8-50b1-44dc-b454-990fb466c9bb; ESPN-ONESITE.WEB-PROD.ts=2023-03-23T02:59:52.652Z; ESPN-ONESITE.WEB-PROD.token=5=eyJhY2Nlc3NfdG9rZW4iOiJlY2Y4NDcxN2JlZjU0OTc3YmNiZGI4MTUyZGVlMWVhMSIsInJlZnJlc2hfdG9rZW4iOiJkNjQ2NTUzNTVjMzg0ZTQ1YmEyOTc1ZDQyMzk1NmVkMSIsInN3aWQiOiJ7NDI2RUNCNzQtOTQ5MC00MzNFLTkwMTgtQTVGNDA3Qjc1QzhCfSIsInR0bCI6ODY0MDAsInJlZnJlc2hfdHRsIjoxNTU1MjAwMCwiaGlnaF90cnVzdF9leHBpcmVzX2luIjoxNzk5LCJpbml0aWFsX2dyYW50X2luX2NoYWluX3RpbWUiOjE2Nzk1Mzg1OTIwNDIsImlhdCI6MTY3OTUzODU5MjAwMCwiZXhwIjoxNjc5NjI0OTkyMDAwLCJyZWZyZXNoX2V4cCI6MTY5NTA5MDU5MjAwMCwiaGlnaF90cnVzdF9leHAiOjE2Nzk1NDAzOTEwMDAsInNzbyI6bnVsbCwiYXV0aGVudGljYXRvciI6ImRpc25leWlkIiwibG9naW5WYWx1ZSI6bnVsbCwiY2xpY2tiYWNrVHlwZSI6bnVsbCwic2Vzc2lvblRyYW5zZmVyS2V5IjoiM1JWNzBfWWpGSjJiQkpiN2RZbWpENXBqM2dNZk14R2Yza1RHdTZjU2pzM0cwNDBoNkJHM2RzZ00wZ2hTNlBLYlZ0TDZTcXY2T25vTmUxZ1JIaDZoRUt1N1BDZHRGaU51eW1fR1JXc1J0UjdxcFlJd1MtYyIsImNyZWF0ZWQiOiIyMDIzLTAzLTIzVDAyOjI5OjUyLjY0OVoiLCJsYXN0Q2hlY2tlZCI6IjIwMjMtMDMtMjNUMDI6Mjk6NTIuNjQ5WiIsImV4cGlyZXMiOiIyMDIzLTAzLTI0VDAyOjI5OjUyLjY0OVoiLCJyZWZyZXNoX2V4cGlyZXMiOiIyMDIzLTA5LTE5VDAyOjI5OjUyLjY0OVoiLCJibHVlX2Nvb2tpZSI6bnVsbH0=|eyJraWQiOiJxUEhmditOL0tONE1zYnVwSE1PWWxBc0pLcWVaS1U2Mi9DZjNpSm1uOEJ6dzlwSW5xbTVzUnc9PSIsImFsZyI6IlJTMjU2In0.eyJpc3MiOiJodHRwczovL2F1dGhvcml6YXRpb24uZ28uY29tIiwic3ViIjoiezQyNkVDQjc0LTk0OTAtNDMzRS05MDE4LUE1RjQwN0I3NUM4Qn0iLCJhdWQiOiJFU1BOLU9ORVNJVEUuV0VCLVBST0QiLCJleHAiOjE2Nzk2MjQ5OTIsImlhdCI6MTY3OTUzODU5MiwianRpIjoiMzR6aHo0WlRJR0VqbllXck0yUTRGQSIsIm5iZiI6MTY3OTUzODUzMiwiYV90eXAiOiJPTkVJRF9UUlVTVEVEIiwiYV9jYXQiOiJHVUVTVCIsImF0ciI6ImRpc25leWlkIiwic2NvcGVzIjpbImR0c3MtZW50aXRsZW1lbnQtdXNlci1hZG1pbiIsIkFVVEhaX0dVRVNUX1NFQ1VSRURfU0VTU0lPTiJdLCJjX3RpZCI6IjEzMjQiLCJpZ2ljIjoxNjc5NTM4NTkyMDQyLCJodGF2IjoyLCJodGQiOjE4MDAsInJ0dGwiOjE1NTUyMDAwLCJlbWFpbCI6ImNoYW5jZV9zdEB5YWhvby5jb20ifQ.ElQv40QcRrdTJNoIUXxhh74efmvUIFkjp7mPlCHe7lXy4AGFMjhXXIGMJsakoSV-QPLQdK12PfXSCu2m63EptxNl2DOmPFB6pj_U8q9iurx8iQyh4J5AjwMz7Q26kH4KxPxsWjqxpx3W5vu4sYZLwqXs4dP4Xk9yVNTc99d0eiL71JJTgnc2133MCB_Smnxj0YvRXTjwGGOYjO-8yZPnev8ZpH1poRfzSJKZHvuze4TzWbhCnm3sMNXbkDgYWTMunV77tjrn5m9n_MlA4bVZbtOkHQrsUS9-ny-dJtKH5_B-83nTEB0Xo3bi52ZmFWvnpfO2309A13-du_8Jt_50aA; ESPN-ONESITE.WEB-PROD-ac=XUS; SWID={426ECB74-9490-433E-9018-A5F407B75C8B}; SWID_NT=0; _chartbeat2=.1679538561274.1679538596054.1.Bkna8YBfLhV-DCscTICsXYCuCTqQY.3; OptanonConsent=isGpcEnabled=0&datestamp=Wed+Mar+22+2023+19%3A29%3A56+GMT-0700+(Pacific+Daylight+Time)&version=202212.1.0&isIABGlobal=false&hosts=&consentId=06492cfc-a530-44e5-8b2e-74866d5a5fd9&interactionCount=1&landingPath=https%3A%2F%2Ffantasy.espn.com%2Fgames%2Fmens-tournament-challenge-second-chance-bracket-2023%2Fbracket%3Fid%3D7cd43a30-c8e6-11ed-a2cf-af959a23db0d&groups=C0001%3A1%2CC0003%3A1%2CSSPD_BG%3A1%2CC0002%3A1%2CC0004%3A1%2CC0005%3A1; espn_s2=AEA8qRTgMkj3wdtSuDSHzWT6Gsb5KNxO2MaKja5trgFWIQ4SotRbtUFA7yzTQcmU3DSchg7TNe7ucN9pWX0ifsEaQEhd2Syj%2Fyhhd6ultT9GoutLgYU8ie3oHnHHat%2BZSf14B%2F4hq7buffk1kqAKwImmc8AxJ1v6WHdC1T3Q8gepmNCNy7p63mENfIKLXLoztnk2gKfTOr%2Ft7uHh9C29ykv9xsM4yLIEXZPZ7bawyp9TGZBY9d2fC2qVoFVY7V6Gyp7Ejt7I6c6z14HGziLNYj%2FefP%2Fld1%2BXsPIYN1OSjFNODw%3D%3D; ESPN-ONESITE.WEB-PROD.idn=009d66d834'
	           'credentials: include']
	#print(f"get_picks for bracket {bracket_name} ({bracket_id})")
	# self.logger_instance.debug(f'get_player_data_json: {url_name}')
	try:
		buffer = BytesIO()
		c = pycurl.Curl()
		c.setopt(c.URL, url_name)
		c.setopt(c.HTTPHEADER, headers)
		c.setopt(c.WRITEDATA, buffer)
		c.setopt(c.CONNECTTIMEOUT, 1000)
		c.setopt(c.CAINFO, certifi.where())
		c.perform()
		c.close()
		data = buffer.getvalue()
		json_data = json.loads(data)
		picks = json_data['picks']
		for pick in picks:
			pick_id = pick['outcomesPicked'][0]['outcomeId']
			pick_name = idmap.get(pick_id)
			pick_names.append(pick_name)

		print(f'{bracket_name}: {pick_names}')

	except Exception as ex:
		print(f'Exception in get_picks {ex}')


	# print("url is: " + url_name)
	# time.sleep(1)
	# with urllib.request.urlopen(url_name) as url:
	# 	time.sleep(1)
	# 	data = json.loads(url.read().decode())
	# 	print(data)


def get_map():
	idmap = dict()
	url_name = "https://fantasy.espn.com/apis/v1/propositions?challengeId=225&platform=chui&view=chui_default"
	print("url is: " + url_name)
	with urllib.request.urlopen(url_name) as url:
		data = json.loads(url.read().decode())
		for i in data:
			for j in i['possibleOutcomes']:
				idmap[j['id']] = j['abbrev']

	return idmap


def main():
	idmap = get_map()
	bracket_list = get_brackets()
	for bracket_id in bracket_list:
		bracket_name = bracket_list[bracket_id]
		get_picks(idmap, bracket_id, bracket_name)
		time.sleep(.25)

#	driver.close()


if __name__ == "__main__":
	main()

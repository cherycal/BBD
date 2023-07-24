__author__ = 'chance'

import json
import time


filename = 'file_text.json'

url = "http://fantasy.espn.com/apis/v3/games/flb/seasons/2019/segments/0/leagues/162788?view" \
      "=recentActivity"

#page = urllib.request.urlopen(url)
#html_content = page.read()
#rendered_content = html2text.html2text(str(html_content, encoding = "utf-8"))
#file = open(filename, 'w')
#file.write(rendered_content)
#file.close()
#print("File done")

f = open(filename, 'r')
text = f.read()
text = text.replace('\n', '')
array = json.loads(text)
f.close()

print("Array: ")

unix_ts = array["communication"]["topics"][1000]["date"]/1000

dt = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(unix_ts))

print(dt)


print (array["communication"]["topics"][0]["date"])
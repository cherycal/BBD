__author__ = 'chance'

import json
import urllib.request


addr = "https://www.fangraphs.com/api/menu/menu-standings"
print(addr)

with urllib.request.urlopen(addr) as url:
    data = json.loads(url.read().decode())
    j = data
    print(data)


__author__ = 'chance'

import requests
from bs4 import BeautifulSoup

request = requests.get("http://games.espn.com/flb/standings?leagueId=87301&view=live")
content = request.content
soup = BeautifulSoup(content, "html.parser")
element = soup.find("td", {"class": "sortableStat5", "id": "tmTotalStatPts_6_5"})
print(element.text)
element = soup.find("td", {"class": "sortableStat5", "id": "tmTotalStatPts_9_5"})
print(element)

# <td class="sortableStat5" id="tmTotalStatPts_6_5">5.5</td>
# <td class="sortableStat5" id="tmTotalStatPts_9_5">2.5</td>


print(request.content)

from processes.retrieve import Retrieve
from selenium import webdriver

__author__ = 'chance'
data = Retrieve()
print(data.title + " by " + __author__)

browser = webdriver.Chrome("C:\Windows\chromedriver.exe") #replace with .Firefox(), or with the browser of your choice
url = "http://www.espn.com/fantasy/baseball/"
browser.get(url) #navigate to the page



# with requests.Session() as s:
#     url = "http://fantasy.espn.com/baseball/team?leagueId=162788&teamId=4&seasonId=2019"
#     r = s.get(url)
#     print (r.content)
#     soup = BeautifulSoup(r.content, 'html.parser')


#s.auth = ('francis_soyer', 'Becton69!')
#s.headers.update({'x-test': 'true'})

#page = requests.get("https://www.fangraphs.com/statss.aspx?playerid=11579")

#page = s.get("http://fantasy.espn.com/baseball/team?leagueId=162788&teamId=4&seasonId=2019")

#print(page.text)

#soup = BeautifulSoup(page.content, 'html.parser')
#html = list(soup.children)[1]


#all_div = soup.find('table', class_='Table2__table__wrapper')

#print(soup.prettify())


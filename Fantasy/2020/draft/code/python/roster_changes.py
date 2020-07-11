import urllib.request, json

print("Load start")

with urllib.request.urlopen("http://fantasy.espn.com/apis/v3/games/flb/seasons/2020/segments/0/leagues/37863846?view=roster") as url:
    data = json.loads(url.read().decode())

print(type(data))

with urllib.request.urlopen("http://fantasy.espn.com/apis/v3/games/flb/seasons/2020/segments/0/leagues/87301?view=roster") as url:
    data = json.loads(url.read().decode())

print(type(data))
    
print("Done loading")

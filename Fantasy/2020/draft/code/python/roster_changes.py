import urllib.request, json

print("Hello")
with urllib.request.urlopen("http://fantasy.espn.com/apis/v3/games/flb/seasons/2020/segments/0/leagues/37863846?view=roster") as url:
    data = json.loads(url.read().decode())
    print(data)

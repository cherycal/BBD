__author__ = 'chance'

import os
import sys

sys.path.append('../modules')

from imgurpython import ImgurClient

album = "ESPNFantasyStandings"
image_path = "Standings_History_wOBA.png"

def main():
    client = ImgurClient(os.environ['IMGURID'], os.environ['IMGURSECRET'])
    #credentials = client.authorize('57e9b32de5', 'pin')
    client.set_user_auth(os.environ['IMGURACCESS'], os.environ['IMGURREFRESH'])

    config = {
        'album': album,
        'name': "rotoauctionkeeperleaguestandings",
        'title': "rotoauctionkeeperleaguestandings",
        'description': "rotoauctionkeeperleaguestandings"
    }

    print("Auth success")
    image = client.upload_from_path(image_path, config=config, anon=False)

    print(f'Image link: {image["link"]}')


if __name__ == "__main__":
    main()

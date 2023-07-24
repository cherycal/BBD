__author__ = 'chance'


class MLBData(object):

    message_body: str

    def __init__(self):
        self.api_root = "http://statsapi.mlb.com/api/v1"
        self.leagues = {}
        self.teams = {}
        self.players = {}


    def load(self):
        pass






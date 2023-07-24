__author__ = 'chance'

class Player:

    def __init__(self, first, last, id):
        self.first = first
        self.last = last
        self.id = id


    def fullname(self):
        return '{} {}'.format(self.first, self.last)


players = {}

players[32517] = Player("Josh", "Bell", 32517)

print( players[32517].fullname())

""" Game picker: chooses boardgame from your collection on boardgamgeek.com
    based on given filters """

from random import shuffle
from boardgamegeek import BGGClient

GOOD_THRESH = 0.2
BAD_THRESH = 0.2
MIN_VOTES = 20

def suggest_playernum(votes_dict):
    """ function to determine, if the game is really playable with the given
        number of players """
    total_votes = int(next(iter(votes_dict.values())))
    max_players = len(votes_dict["results"].items())
    if total_votes < MIN_VOTES:
        result = [list(range(1, max_players)), list(range(1, max_players))]
        return result
    best = []
    not_recommended = []
    for val in votes_dict['results'].values():
        best.append(val['best']/total_votes)
        not_recommended.append(val['not_recommended']/total_votes)
    good_num = [i for i, x in enumerate(best, 1) if x > GOOD_THRESH]
    bad_num = [i for i, x in enumerate(not_recommended, 1) if x > BAD_THRESH]
    return [good_num, bad_num]

def search_match(col):
    """ Generator for finding games that match filter criteria """
    for i, game in enumerate(col, 1):
        numfit = suggest_playernum(game.suggested_numplayers)
        if (game.max_players >= num_player and
                game.min_players <= num_player and
                game.max_playing_time <= playtime and
                num_player in numfit[0] and
                num_player not in numfit[1] and
                round(game.rating_average_weight) == weight):
            yield i, game.name

bgg = BGGClient()
USERNAME = eval(input("BGG Username: "))

collection = bgg.collection(USERNAME, exclude_subtype='boardgameexpansion', own=True, wishlist=None)
shuffle(collection.items)
ids = [x.id for x in collection.items]

print('Hello ' + USERNAME + ', you have ' + str(len(collection)) + ' games in your collection '
      '(expansions not counting)')

# get games from BGG
try:
    print('Collecting games.. ')
    game_list = bgg.game_list(ids)
except:
    print('Error!')
else:
    print('Done.\n')

num_player = eval(input("How many players: "))
playtime = eval(input("Maximum playtime in minutes: "))
weight = eval(input("Weight (1 = light, 5 = heavy): "))

match = search_match(game_list)
for num in range(5):
    print('Match: Game No. %d: %s' % (next(match)))

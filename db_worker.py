from picker_app import db
from picker_app import Game
from boardgamegeek import BGGClient
""" Worker script to get a collection and all game data from a collection
Should run once a day, preferably in the morning
TODO: Unit tests!!! """

def get_games(username):
    """ Get games and game collection using bgg API2 
    returns: list of games and collection object """

    bgg = BGGClient(timeout=120, requests_per_minute=20)
    print("Getting collection from BGG..")
    collection = bgg.collection(username, exclude_subtype='boardgameexpansion', own=True, wishlist=None)
    ids = [x.id for x in collection.items]
    game_list = []

    # get games from BGG
    try:
        print("Getting games from BGG..")
        game_list = bgg.game_list(ids)
        if not game_list:
            print("Error: empy list returned.")
    except:
        print("An Error occured..")
        raise TimeoutError
    else:
        print("Done.")
    return game_list, collection

def _suggest_playernum(votes_dict):
    """ private function to determine, if the game is really playable with the given
    number of players. Should only be executed from inside db_update
    returns a 2-dimensional list with 2 entries: list of bestplaynums and list of
    not recommended playnums
    TODO: Improve return!"""
    # Constants
    GOOD_THRESH = 0.2
    BAD_THRESH = 0.2
    MIN_VOTES = 20

    total_votes = int(votes_dict['total_votes'])
    max_players = len(votes_dict['results'].items()) - 1
    if total_votes < MIN_VOTES:
        result = [list(range(1, max_players + 1)), []]
        return result
    good_num = []
    bad_num = []
    for num, key in enumerate(votes_dict['results'], 1):
        if key[-1:] == '+':
            continue
        if int(votes_dict['results'][key]['not_recommended'])/total_votes > 0.2:
            bad_num.append(int(key))
        if int(votes_dict['results'][key]['best'])/total_votes > 0.2:
            good_num.append(int(key))
    return [good_num, bad_num]

def db_update(db, game_list, collection):
    """ Updates db data """
    for g, c in list(zip(game_list, list(collection))):
        numfit = _suggest_playernum(g.suggested_numplayers)
        game = Game(gid=g.id, name_col=c.name, name_en=g.name, authors=g.designers,
                    maxplayers=g.max_players, minplayers=g.min_players, max_playing_time=g.max_playing_time,
                    min_playing_time=g.min_playing_time, best_playnum=numfit[0], not_recom_playnum=numfit[1],
                    description=g.description, imageurl=g.image, mechanics=g.mechanics,
                    average_weight=g.rating_average_weight, bgg_rank=g.stats['ranks'][0]['value'])
        db.session.add(game)
        db.session.commit()

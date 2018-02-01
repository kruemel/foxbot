from random import shuffle
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import or_

app = Flask(__name__)

# on linux:
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://kathrin@localhost/gamepicker'

# on windows:
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://kathrin:password@localhost:5433/gamepicker'
db = SQLAlchemy(app)

# db Models
class Game(db.Model):
    gid = db.Column(db.Integer, primary_key=True)
    name_col = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    authors = db.Column(ARRAY(db.String(40)))
    maxplayers = db.Column(db.Integer)
    minplayers = db.Column(db.Integer)
    max_playing_time = db.Column(db.Integer)
    min_playing_time = db.Column(db.Integer)
    best_playnum = db.Column(ARRAY(db.Integer))
    not_recom_playnum = db.Column(ARRAY(db.Integer))
    description = db.Column(db.Text)
    imageurl = db.Column(db.String(200))
    mechanics = db.Column(ARRAY(db.String(60)))
    average_weight = db.Column(db.Float)
    bgg_rank = db.Column(db.Integer)

class GameQuery(db.Model):
    qid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    playnum = db.Column(db.Integer)
    max_playtime = db.Column(db.Integer)
    weight = db.Column(db.Integer)

def map_mechanic(arg):
    mapper = {
        'coop': 'Co-operative Play',
        'cardDraft': 'Card Drafting',
        'tilePlace': 'Tile Placement',
        'areaControl': 'Area Control / Area Influence',
        'deckBuild': 'Deck / Pool Building',
        'workerPlace': 'Worker Placement',
    }
    return mapper.get(arg, None)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/test')
def testroute():
    return render_template('test.html')

@app.route('/process', methods=['GET', 'POST'])
def process():
    playnum = request.form['playnum']
    playtime = request.form['playtime']
    weight = int(request.form['rating'])
    mechanics = request.form.getlist('mechCheck')
    if (playnum and playtime):
        gamequery = Game.query.filter(Game.maxplayers >= playnum, playnum == Game.best_playnum.any_(),
                                        Game.max_playing_time <= playtime)
        if weight:
            clamp = lambda n: max(min(5, n), 0)
            min_weight = clamp(weight - 0.5)
            max_weight = clamp(weight + 0.5)
            gamequery = gamequery.filter(Game.average_weight.between(min_weight, max_weight))

        mlist = []
        for m in mechanics:
            mlist.append(map_mechanic(m))
        
        if mlist:
            gamequery = gamequery.filter(or_(Game.mechanics.any_() == m for m in mlist))
        
        gamequery = gamequery.order_by(Game.bgg_rank)
        games = gamequery.all()

        return render_template('showgames.html', games=games, n=range(len(games)))
    return("Ooops.. you didn't fill out all the questions..")

# @app.route('/foundgames/<playnum>/<playtime>/<weight>/<mech>')
# def showgames(playnum, playtime, weight, mech):
#     clamp = lambda n: max(min(5, n), 0)
#     min_weight = clamp(int(weight) - 0.5)
#     max_weight = clamp(int(weight) + 0.5)
#     games = Game.query.filter(Game.maxplayers > playnum, playnum == Game.best_playnum.any_(),
#                               Game.max_playing_time <= playtime,
#                               Game.average_weight.between(min_weight, max_weight)).all()
#     shuffle(games)
#     mlist = []
#     for num, m in enumerate(mech):
#         mlist.append(map_mechanic(m))
#         print(num)

#     print(mech)
#     print(mlist)
    
#     return render_template('showgames.html', games=games, n=range(len(games)))
    # return "Found games: {}".format(found)
    # return('Playnum: {}<br><br>Playtime: {} <br><br>Weight: {}'
        #    '<br><br>Mechanics: {}'.format(playnum, playtime, weight, mech)

if __name__ == '__main__':
    app.run(debug=True)

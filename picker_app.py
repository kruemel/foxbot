from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY
from flask_wtf import Form 

app = Flask(__name__)

# on linux:
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://kathrin@dlocalhost/gamepicker'

# on windows:
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://kathrin:password@localhost:5433/gamepicker'
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

# class GameQueryForm(Form):

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/showgames')
def displaygames():
    return render_template('showgames.html')

@app.route('/process', methods=['GET', 'POST'])
def process():
    playnum = request.form['playnum']
    playtime = request.form['playtime']
    weight = request.form['rating']
    mechanics = request.form.getlist('mechCheck')
    if (playnum and playtime and weight):
        return redirect(url_for('showgames', playnum=playnum, 
            playtime=playtime, weight=weight, mech=mechanics))
    return("Ooops.. you didn't fill out all the questions..")

@app.route('/foundgames/<playnum>/<playtime>/<weight>/<mech>')
def showgames(playnum, playtime, weight, mech):
    clamp = lambda n: max(min(5, n), 0)
    min_weight = clamp(int(weight) - 0.5)
    max_weight = clamp(int(weight) + 0.5)
    gamelist = Game.query.filter(Game.maxplayers > playnum, playnum == Game.best_playnum.any_(),
                                    Game.max_playing_time <= playtime,
                                    Game.average_weight.between(min_weight, max_weight)).all()
    found = []
    for g in gamelist:
        found.append(g.name_col)

    return "Found games: {}".format(found)
    # return('Playnum: {}<br><br>Playtime: {} <br><br>Weight: {}'
        #    '<br><br>Mechanics: {}'.format(playnum, playtime, weight, mech)

if __name__ == '__main__':
    app.run(debug=True)

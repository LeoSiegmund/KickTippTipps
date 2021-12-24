from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import desc
import os
import math
import numpy as np

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db
db = SQLAlchemy(app)
# init ma
ma = Marshmallow(app)


class Verein(db.Model):
    name = db.Column(db.String, primary_key=True)
    s = db.Column(db.Integer)
    p = db.Column(db.Integer)
    t = db.Column(db.Integer)
    gt = db.Column(db.Integer)

    def __init__(self, name):
        self.name = name
        self.s = 0
        self.p = 0
        self.t = 0
        self.gt = 0

class vereinSchema(ma.Schema):
    class Meta:
        fields = ('name', 's', 'p', 't', 'gt')


# Init Schema
verein_schema = vereinSchema()
vereine_schema = vereinSchema(many=True)


@app.route('/')
def home():
    return render_template('index.html')


# Create Verein
@app.route('/add_verein', methods=['POST'])
def add_data():
    name = request.json['Name']
    if(name != ""):
        new_data = Verein(name)

        db.session.add(new_data)
        db.session.commit()

        return verein_schema.jsonify(new_data)
    else:
        return "Name can not be empty"


@app.route('/new_spieltag', methods=['POST'])
def add_spieltag():
    ergebnisse = request.json['Spiele']
    for spiel in ergebnisse:
        verein1 = spiel['Teilnehmer'][0]
        verein2 = spiel['Teilnehmer'][1]
        tore1 = spiel['Ergebnis'][0]
        tore2 = spiel['Ergebnis'][1]

        if(tore1 > tore2):          #handling win for team 1
            #print(verein1, "hat gewonnen")
            data = Verein.query.get(verein1)
            data.s = data.s + 1
            data.p = data.p + 3
            data.t = data.t + tore1
            data.gt = data.gt + tore2
            db.session.commit()

            data = Verein.query.get(verein2)
            data.s = data.s + 1
            data.t = data.t + tore2
            data.gt = data.gt + tore1
            db.session.commit()

        if(tore2 > tore1):          #handling win for team 2
            #print(verein2, "hat gewonnen")
            data = Verein.query.get(verein2)
            data.s = data.s + 1
            data.p = data.p + 3
            data.t = data.t + tore2
            data.gt = data.gt + tore1
            db.session.commit()

            data = Verein.query.get(verein1)
            data.s = data.s + 1
            data.t = data.t + tore1
            data.gt = data.gt + tore2
            db.session.commit()

        if(tore1 == tore2):         #handling draw game
            #print("Unentschieden")
            data = Verein.query.get(verein1)
            data.s = data.s + 1
            data.p = data.p + 1
            data.t = data.t + tore1
            data.gt = data.gt + tore2
            db.session.commit()

            data = Verein.query.get(verein2)
            data.s = data.s + 1
            data.p = data.p + 1
            data.t = data.t + tore2
            data.gt = data.gt + tore1
            db.session.commit()

    return str(ergebnisse)


@app.route('/new_tipp', methods=['POST'])
def generate_tipp():
    spiel = request.json['Teilnehmer']
    var = 1
    sigma = math.sqrt(var)

    verein1 = spiel[0]
    verein2 = spiel[1]

    data1 = Verein.query.get(verein1)
    mu = data1.t / data1.s
    tore1 = np.random.normal(mu, sigma)
    if(tore1 < 1):
        tore1 = 0
    if(tore1 >= 1 and tore1 < 2):
        tore1 = 1
    elif(tore1 >= 2 and tore1 < 3):
        tore1 = 2
    elif(tore1 >= 3 and tore1 < 4):
        tore1 = 3
    elif(tore1 >= 4 and tore1 < 5):
        tore1 = 4
    elif(tore1 >= 5 and tore1 < 6):
        tore1 = 5
    elif(tore1 >= 6 and tore1 < 7):
        tore1 = 6
    elif(tore1 >= 7 and tore1 < 8):
        tore1 == 7
    elif(tore1 >= 8):
        tore1 = 8

    data2 = Verein.query.get(verein2)
    mu = data2.t / data2.s
    tore2 = np.random.normal(mu, sigma)
    if(tore2 < 1):
        tore2 = 0
    if(tore2 >= 1 and tore2 < 2):
        tore2 = 1
    elif(tore2 >= 2 and tore2 < 3):
        tore2 = 2
    elif(tore2 >= 3 and tore2 < 4):
        tore2 = 3
    elif(tore2 >= 4 and tore2 < 5):
        tore2 = 4
    elif(tore2 >= 5 and tore2 < 6):
        tore2 = 5
    elif(tore2 >= 6 and tore2 < 7):
        tore2 = 6
    elif(tore2 >= 7 and tore2 < 8):
        tore2 == 7
    elif(tore2 >= 8):
        tore2 = 8

    ergebnis = jsonify({"Ergebnis": [tore1, tore2]})

    return ergebnis    



@app.route('/tabelle', methods=['GET'])
def get_tabelle():
    all_data = Verein.query.order_by(desc(Verein.p)).all()
    result = jsonify(vereine_schema.dump(all_data))
    result.headers.add("Access-Control-Allow-Origin", "*")
    return result


@app.route('/reset', methods=['GET'])
def reset_tabelle():
    all_data = Verein.query.order_by(desc(Verein.p)).all()
    vereine = []
    for data in all_data:
        vereine.append(data.name)
    for verein in vereine:
        data = Verein.query.get(verein)
        data.s = 0
        data.p = 0
        data.t = 0
        data.gt = 0
        db.session.commit()
    return "Table was reset"


@app.route('/delete/<verein>', methods=['DELETE'])
def delete_verein(verein):
    Verein.query.filter_by(name=verein).delete()
    db.session.commit()
    return "deleted " + verein


# Run App
if __name__ == '__main__':
    app.run(port=9000, debug=True)

from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import desc
import os

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


# Verein Class
class Data(db.Model):
    name = db.Column(db.String, primary_key=True)
    p = db.Column(db.Integer)
    t = db.Column(db.Integer)
    gt = db.Column(db.Integer)

    def __init__(self, name):
        self.name = name
        self.p = 0
        self.t = 0
        self.gt = 0


# Data Schema
class vereinSchema(ma.Schema):
    class Meta:
        fields = ('name', 'p', 't', 'gt')


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
    new_data = Data(name)

    db.session.add(new_data)
    db.session.commit()

    return verein_schema.jsonify(new_data)


@app.route('/new_spieltag', methods=['POST'])
def add_spieltag():
    ergebnisse = request.json['Spiele']
    for spiel in ergebnisse:
        verein1 = spiel['Teilnehmer'][0]
        verein2 = spiel['Teilnehmer'][1]
        tore1 = spiel['Ergebnis'][0]
        tore2 = spiel['Ergebnis'][1]

        if(tore1 > tore2):
            print(verein1, "hat gewonnen")
            data = Data.query.get(verein1)
            data.p = data.p + 3
            data.t = data.t + tore1
            data.gt = data.gt + tore2
            db.session.commit()

            data = Data.query.get(verein2)
            data.t = data.t + tore2
            data.gt = data.gt + tore1
            db.session.commit()

        if(tore2 > tore1):
            print(verein2, "hat gewonnen")
            data = Data.query.get(verein2)
            data.p = data.p + 3
            data.t = data.t + tore2
            data.gt = data.gt + tore1
            db.session.commit()

            data = Data.query.get(verein1)
            data.t = data.t + tore1
            data.gt = data.gt + tore2
            db.session.commit()

        if(tore1 == tore2):
            print("Unentschieden")
            data = Data.query.get(verein1)
            data.p = data.p + 1
            data.t = data.t + tore1
            data.gt = data.gt + tore2
            db.session.commit()

            data = Data.query.get(verein2)
            data.p = data.p + 1
            data.t = data.t + tore2
            data.gt = data.gt + tore1
            db.session.commit()

    return str(ergebnisse)


@app.route('/tabelle', methods=['GET'])
def get_tabelle():
    all_data = Data.query.order_by(desc(Data.p)).all()
    result = jsonify(vereine_schema.dump(all_data))
    result.headers.add("Access-Control-Allow-Origin", "*")
    return result


@app.route('/delete/<verein>', methods=['DELETE'])
def delete_verein(verein):
    Data.query.filter_by(name=verein).delete()
    db.session.commit()
    return "deleted" + verein


# Run App
if __name__ == '__main__':
    app.run(port=9000, debug=True)

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data-dev.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    __talblename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(20), unique=True, nullable = False)
    idade = db.Column(db.Integer, default=0)

    def json(self):
        user_json = {'id': self.id,
                     'name': self.name,
                     'email':self.email,
                     'idade': self.idade
                    }
        return user_json

if __name__ == "__main__":
    app.run(debug = True)

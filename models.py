from flask_sqlalchemy import SQLAlchemy
from datetime import datetime #them thoi gian
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'),nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    transactions = db.relationship('Transaction', backref='category', lazy=True) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    monthly_budget = db.Column(db.Float, nullable=True, default=0)

    transactions = db.relationship('Transaction', backref='author', lazy='dynamic')
    categories = db.relationship('Category', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

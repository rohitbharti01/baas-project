from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    first = db.Column(db.String(20), nullable=False)
    last = db.Column(db.String(20), nullable=False)
    phone_no = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(320), nullable=False)
    aadhar = db.Column(db.String(12), nullable=False)
    addr = db.Column(db.String(42), nullable=False)
    keystorehash = db.Column(db.String(20), nullable=False)
    lastlogin = db.Column(db.Date(), nullable=True)

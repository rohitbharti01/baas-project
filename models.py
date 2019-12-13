from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


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
    infurakey = db.Column(db.String, nullable=False)
    passwdhash= db.Column(db.String, nullable=False)


class scheduled(db.Model):
    __tablename__ = "scheduled"
    id = db.Column(db.Integer, primary_key=True)
    payerid= db.Column(db.Integer, db.ForeignKey(User.id))
    recipientid= db.Column(db.Integer, db.ForeignKey(User.id))
    amount= db.Column(db.Float, nullable=False)
    scheduled_time= db.Column(db.DateTime, nullable=False)

class payHistory(db.Model):
    __tablename__="payhistory"
    id=db.Column(db.Integer, primary_key=True)
    payerid= db.Column(db.Integer, db.ForeignKey(User.id))
    recipientid= db.Column(db.Integer, db.ForeignKey(User.id))
    amount= db.Column(db.Float, nullable=False)
    payment_datetime= db.Column(db.DateTime, nullable=False)
    txnhash= db.Column(db.String, nullable=False)

class threads(db.Model):
    __tablename__="threads"
    id=db.Column(db.Integer, primary_key=True)
    sch_id= db.Column(db.String, nullable=False)
    thread_id= db.Column(db.String, nullable=False)

# class PayHistory(db.Model):
#     __tablename__ = "paymenthistory"
#     id = db.Column(db.Integer, primary_key=True)
#     payerid=db.Column(db.Integer, foreign_key(User))

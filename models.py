from flask_sqlalchemy import SQLAlchemy
import onetimepass
import base64
import os

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
    lastlogin = db.Column(db.Date(), nullable=True)
    infurakey = db.Column(db.String, nullable=False)
    passwdhash= db.Column(db.String, nullable=False)
    balance=db.Column(db.Float, nullable=True)
    otp_secret = db.Column(db.String(16))

    def __init__(self,first, last, phone_no, email, aadhar, addr, lastlogin, infurakey, passwdhash, balance):
        
        self.first = first
        self.last = last
        self.phone_no = phone_no
        self.email = email
        self.aadhar = aadhar
        self.addr = addr
        self.infurakey = infurakey
        self.passwdhash = passwdhash
        self.balance = balance

        if self.otp_secret is None:
            self.otp_secret = base64.b32encode(os.urandom(10)).decode('utf-8')

    def get_totp_uri(self):
        return f'otpauth://totp/2FA-Demo:{self.id}?secret={self.otp_secret}&issuer=2FA-Demo'
    
    def verify_totp(self, token):
        return onetimepass.valid_totp(token, self.otp_secret)


class scheduled(db.Model):
    __tablename__ = "scheduled"
    id = db.Column(db.Integer, primary_key=True)
    payerid= db.Column(db.Integer, db.ForeignKey(User.id))
    recipientid= db.Column(db.Integer, db.ForeignKey(User.id))
    amount= db.Column(db.Float, nullable=False)
    scheduled_time= db.Column(db.DateTime, nullable=False)
    # link=db.Column(db.)

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
    sch_id= db.Column(db.String, db.ForeignKey(scheduled.id))
    thread_id= db.Column(db.String, nullable=False)

class keyDict(db.Model):
    __tablename__="keydict"
    id=db.Column(db.Integer, primary_key=True)
    userid=db.Column(db.String,db.ForeignKey(User.id) )
    address= db.Column(db.String, nullable=False)
    cipher= db.Column(db.String, nullable=False)
    ciphertext= db.Column(db.String, nullable=False)
    kdf= db.Column(db.String, nullable=False)
    iv= db.Column(db.String, nullable=False)
    dklen= db.Column(db.String, nullable=False)
    n= db.Column(db.String, nullable=False)
    r= db.Column(db.String, nullable=False)
    p= db.Column(db.String, nullable=False)
    salt= db.Column(db.String, nullable=False)
    mac= db.Column(db.String, nullable=False)
    id_= db.Column(db.String, nullable=False)
    version= db.Column(db.String, nullable=False)

class Requested(db.Model):
    __tablename__ = "requested"
    id = db.Column(db.Integer, primary_key=True)
    requesterid= db.Column(db.Integer, db.ForeignKey(User.id))
    payerid= db.Column(db.Integer, db.ForeignKey(User.id))
    sellerid=db.Column(db.Integer, db.ForeignKey(User.id))
    amount= db.Column(db.Float, nullable=False)
    scheduled_time= db.Column(db.DateTime, nullable=False)
    reason=db.Column(db.String, nullable=True)

class Delegated(db.Model):
    __tablename__ = "delegated"
    id = db.Column(db.Integer, primary_key=True)
    buyerid= db.Column(db.Integer, db.ForeignKey(User.id))
    fromid=db.Column(db.Integer, db.ForeignKey(User.id))
    recipientid= db.Column(db.Integer, db.ForeignKey(User.id))
    amount= db.Column(db.Float, nullable=False)
    scheduled_time= db.Column(db.DateTime, nullable=False)

# class PayHistory(db.Model):
#     __tablename__ = "paymenthistory"
#     id = db.Column(db.Integer, primary_key=True)
#     payerid=db.Column(db.Integer, foreign_key(User))

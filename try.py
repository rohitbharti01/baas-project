#!/usr/bin/env python


from flask import Flask, render_template, request
from web3 import Web3
import hashlib
from models import *
import os

app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]=os.getenv("SQLALCHEMY_DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
db.init_app(app) 

def main():
    db.create_all()
    users=db.query.all()
    for u in users:
        print({u.first})
        # print(f"{u.first} {u.second} has public address {u.addr}")

if __name__ == "__main__":
    with app.app_context():
        main()

def count(num):
    lst=[]
    for i in range(num):
        lst.append("")
    return lst

def loginfn(infura_url, passwd, keystore):
    acc={}
    val=1
    web3=Web3(Web3.HTTPProvider(infura_url))
    try:
        acc=web3.eth.account.decrypt(keystore, passwd)
    except ValueError:
        print("Wrong password")
        val=-1
    finally:
        return acc,val

@app.route('/signup')
def signup():
    return render_template("createaccount.html")

@app.route('/checksignup', methods=["POST"])
def checksignup():
    global selfaddress
    if request.method=="GET":
        return "Please fill the form"
    else:
        first=request.form.get("first")
        last=request.form.get("last")
        phone_no=request.form.get("phone_no")
        aadhar=request.form.get("aadhar")
        infura_key=request.form.get("infura_key")
        email=request.form.get("email")
        passwd=request.form.get("passwd")

        infura_url='https://mainnet.infura.io/v3/'+infura_key
        web3=Web3(Web3.HTTPProvider(infura_url))
        account = web3.eth.account.create()
        keystore=account.encrypt(passwd)
        keystore=str(keystore)
        keystorehash = hashlib.md5(keystore.encode())
        keystorehash=keystorehash.hexdigest()
        
        u=User(first=first, last=last, phone_no=phone_no, email=email, aadhar=aadhar, addr=account.address,keystorehash=keystorehash)
        db.session.add(u)
        db.session.commit()
        
        return render_template("home.html", first=first)

@app.route('/login', methods=["GET", "POST"])
def login():
    infura_key=request.form.get("infura_key")
    passwd=request.form.get("passwd")
    if request.method=="POST":
        passwd=""
        return render_template("login.html", val=-1)
    else :
        return render_template("login.html", val=1)

@app.route('/checklogin', methods=["POST"])
def checklogin():
    if request.method=="GET":
        return "Please fill the form"
    else:
        infura_key=request.form.get("infura_key")
        passwd=request.form.get("passwd")

        infura_url='https://mainnet.infura.io/v3/'+infura_key
        keystore={'address': '04e456c06f272c8f4059d372b4fefff4e1f97cf7', 'crypto': {'cipher': 'aes-128-ctr', 'cipherparams': {'iv': 'f3ecd6cd858c9e0d032c0c9d3c6cc391'}, 'ciphertext': '28e9d1e251937fcb47f475ef0017cdb7fd38fd9ceedbf9c8506a0f27b905f603', 'kdf': 'scrypt', 'kdfparams': {'dklen': 32, 'n': 262144, 'r': 1, 'p': 8, 'salt': 'e76355d14b439939ca191fba2052aa04'}, 'mac': '54de12270c230840d04feb6bae5fb644e33bbc231877fd56a76f96b34feeee3f'}, 'id': 'ad1b96cc-4ae6-468e-9008-5042229ca907', 'version': 3}
        


        x,flag=loginfn(infura_url, passwd, keystore)
        if flag is 1:
            return render_template("home.html", first=first)
        else:
            return render_template("login.html", val=-1)

@app.route('/home',methods=["POST"])
def home():
    global first
    global last
    if request.method=="GET":
        return "Please login first"
    else:
        return render_template("home.html", first=first)

@app.route('/paynow', methods=["POST"])
def paynow():
    numtxn=request.form.get("numtxn")
    numtxn=int(numtxn)
    lst=count(numtxn)
    return render_template("paynow.html", numtxn=numtxn)

@app.route('/payscheduler', methods=["POST"])
def payscheduler():
    numtxn=request.form.get("numtxn")
    numtxn=int(numtxn)
    return render_template("payscheduler.html", numtxn=numtxn)

@app.route('/paymentvalid_now',methods=["POST"])
def paymentvalid_now():

    global selfaddress

    infuraaddr=request.form.getlist("infuraaddr")
    amt=request.form.getlist("amt")
    x=0
    l=len(infuraaddr)
    for i in range(l):
        x+=amt[i]
    # hex_str = selfaddress
    # # console.log(selfaddress)
    # hex_int = int(hex_str, 16)
    # new_int = hex_int + 0x200
    sa=selfaddress.encode('utf-8')
    sa=sa.hex()
    return "wer"

    # bal=app.web3.eth.getBalance(selfaddress)
    # if(bal<x):
    #     return render_template('insufficientfunds.html')
    # else:
    #     return render_template("confirmpayment.html")

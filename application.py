from flask import Flask, render_template, request, send_file, abort
from web3 import Web3, EthereumTesterProvider
import hashlib
from models import *
import os
from datetime import date, datetime, timedelta
import time
import threading

app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]=os.getenv("SQLALCHEMY_DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
db.init_app(app) 
UPLOAD_FOLDER='./uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
global passwd
global keystore
global infura_url
global threaddict

def main():
    db.create_all()

if __name__ == "__main__":
    with app.app_context():
        main()

def wait(fromid, toid, val,hrs, sch_id):
    global threaddict
    threaddict[sch_id]=threading.get_ident()
    time.sleep(hrs*3600)
    flag=1
    try:
        txnhash=w3.eth.sendTransaction({'from':str(w3.eth.accounts[0]),'to':str(toid),'value': str(val)}) 
        txnhash=str(txnhash.hex())
        scheduledpayment=scheduled.query.get(sch_id)
        paid=payHistory(payerid=fromid, recipientid=toid, amount=val, payment_datetime=datetime.datetime.now(), txnhash=txnhash)
        tid=paid.id
    except:
        flag=-1

    if flag==1:
        return str(txnhash)
    else:
        return "Sorry, that didn't work."

def quotechange(str_):
    str_=str(str_)
    strnew=""
    for i in range(0, len(str_)):
        if str_[i] is '\'':
            strnew+='\"'
        else:
            strnew+=str_[i]
    return strnew

def count(num):
    lst=[]
    for i in range(0,num):
        lst.append([])
    return lst

def loginfn(infura_url, passwd, keystore):
    acc={}
    val=1
    w3=Web3(Web3.HTTPProvider(infura_url))
    try:
        acc=w3.eth.account.decrypt(keystore, passwd)
    except ValueError:
        print("Wrong password")
        val=-1
    finally:
        return acc,val

@app.route('/')
@app.route('/signup')
def signup():
    return render_template("createaccount.html", retry =False)

@app.route('/checksignup', methods=["GET", "POST"])
def checksignup():  

    if request.method=="GET":
        return "Please fill the form"
    else:
        flag=1
        first=request.form.get("first")
        last=request.form.get("last")
        phone_no=request.form.get("phone_no")
        aadhar=request.form.get("aadhar")
        infura_key=request.form.get("infura_key")
        email=request.form.get("email")
        passwd=str(request.form.get("passwd"))
        passwdhash=hashlib.md5(passwd.encode()).hexdigest()

        if first is "" or last is "" or phone_no is "" or aadhar is "" or infura_key is "" or email is "" or passwd is "":
            flag=-1

        if flag is 1:
            infura_url='https://mainnet.infura.io/v3/'+infura_key
            w3=Web3(Web3.HTTPProvider(infura_url))
            account = w3.eth.account.create()
            keystore=account.encrypt(passwd)
            keystore=str(keystore)
            keystorehash = hashlib.md5(keystore.encode())
            keystorehash=keystorehash.hexdigest()
            
            u=User(first=first, last=last, phone_no=phone_no, email=email, aadhar=aadhar, addr=account.address,keystorehash=keystorehash, lastlogin=date.today(), infurakey=infura_key, passwdhash=str(passwdhash))
            fromid=u.id
            db.session.add(u)
            db.session.commit()
        
        if flag is -1:
            return render_template("createaccount.html", retry =True)
        else:
            return render_template("accountcreated.html",fromid=fromid , first=first, keystore=keystore)

@app.route('/deleteall')
def deleteall():
    User.query.delete()
    db.session.commit()
    # db.create_all()
    return "hey"

@app.route('/ll')
def ll():
    u=User.query.all()[0]
    # db.create_all()
    return str(u.lastlogin)

@app.route('/login')
def login():
    if request.method is "GET":
        val=-1
    else:
        val=1
    return render_template("login.html", retry=val)

@app.route('/checklogin', methods=["POST"])
def checklogin():
    id_=request.form.get("id_")
    passwd=str(request.form.get("passwd"))
    passhash=(hashlib.md5(passwd.encode())).hexdigest()

    user=User.query.filter_by(id=id_).first()
    if user is None:
        return "User was none"
        # return render_template("login.html", retry=-1)
    elif user.passwdhash==passhash:
            return render_template("home.html",fromid=id_, first=user.first)
    else:
        return passwd+" "+user.passwdhash+' '+passhash
        # return render_template("login.html", retry=-1)

    # else:
    #     first_=user.first
    #     diff=0
    #     d2=user.lastlogin
    #     d1=date.today()
    #     delta=d2-d1
    #     diff=delta.days

    #     if diff>=2:
    #         return render_template("setupaccount.html", val=1)
    #     else:
    #         return render_template("home.html", fromid=id_)

@app.route('/showall')
def showall():
    lst=""
    us=User.query.all()
    for u in us:
        lst+=(f"{u.first} {u.last} {u.id } {u.passwdhash} ")
    return lst

@app.route('/setupaccount', methods=["GET", "POST"])
def setupaccount():
    global passwd
    global keystore

    infura_key=request.form.get("infura_key")
    passwd=request.form.get("passwd")
    keystore=request.form.get("keystore")
    infura_url='https://mainnet.infura.io/v3/'+infura_key

    if request.method=="POST":          #reset password and file fields if it is a retry
        passwd=""
        keystore={}
        return render_template("setupaccount.html", val=-1)
    else :
        return render_template("setupaccount.html", val=1)

@app.route('/checksetupreq', methods=["POST"])
def checksetupreq():
    if request.method=="GET":
        return "Please fill the form"
    else:
        flag=1       #authentication check
        acc={'address': "ad"}

        id_=request.form.get("id_")
        infura_key=request.form.get("infura_key")
        passwd=str(request.form.get("passwd"))
        k=request.form['file']
        # keystore.save(secure_filename(k.filename))
        f=open(os.path.join(app.config['UPLOAD_FOLDER'], str(k)),'r')
        keystore=quotechange(str(f.read()))
        # keystore=json.loads(quotechange(str(f.read())))

        if infura_key is "" or passwd is "" or str(keystore) is "":            #if user leaves a field blank
            flag=-1

        if not(flag is -1):

            infura_url='https://mainnet.infura.io/v3/'+infura_key
            w3=Web3(Web3.HTTPProvider(infura_url))
            keystore=str(keystore)
            ks_hash = hashlib.md5(keystore.encode())
            ks_hash=ks_hash.hexdigest()
 
            try:
                acc=w3.eth.account.decrypt(keystore, 'foobar')
                acc=str(acc.hex())
            except ValueError:
                flag=-2
                    # flag=-2

            # finally:
            if flag is 1:
                user_=User.query.filter_by(id=id_).first()
                if user_ is None:
                    flag=0
                else:
                    if not(user_.keystorehash != '') :          #change to include the necessary authentication
                        flag=-3  

        if flag is 1:
            return render_template("home.html", first=user_.first, fromid=user_.id)
        else:
            return str(flag)
            # return str(ks_hash)+'\n'+str(kk)
            # return render_template("setupaccount.html", val=flag)

@app.route('/home',methods=["GET", "POST"])
def home():
    if request.method=="GET":
        return "Please login first"
    else:
        first=request.form.get("first")
        fromid=request.form.get("fromid")
        if first is None or fromid is None:
            return abort(404)
        else:
            return render_template("home.html", first=first, fromid=fromid)

@app.route('/paynow', methods=["POST", "GET"])
def paynow():
    if request.method=="GET":               #if directly via address bar
        idnum=request.args.get('abc')
        if idnum is None:
            return "No such field."
        else:
            user=User.query.filter_by(id=id_).first()
            if user is None:                    #id passed in address bar doesn't match
                return "No such user."
            else:
                d2=user.lastlogin
                d1=date.today()
                delta=d2-d1
                diff=delta.days
                if diff>=2:
                    return render_template("setupaccount.html", val=1)  #time to setup wallet again
                else:
                    return render_template("paynow.html", numtxn=1)     #by default, pay to one account only
    else:
        fromid=request.form.get("fromid")
        # numtxn=request.form.get("numtxn")
        numtxn=1
        numtxn=int(numtxn)
        return render_template("paynow.html",numtxn=numtxn, fromid=fromid) #numtxn transactions allowed, via post method request

@app.route('/payscheduler', methods=["POST"])
def payscheduler():
    fromid=request.form.get("fromid")
    numtxn=request.form.get("numtxn")
    numtxn=1
    numtxn=int(numtxn)
    return render_template("payscheduler.html",numtxn=numtxn, fromid=fromid) #numtxn transactions allowed, via post method request

@app.route('/paymentvalid_now',methods=["POST"])
def paymentvalid_now():

    global passwd
    global keystore
    # addresses=request.form.get("addresses")
    txhash="hash"
    toid=request.form.get("toid")
    amount=request.form.get("second")
    fromid=request.form.get("fromid")
    u=User.query.get(fromid)
    if u is None:
        return "user is none"
    # paytime=request.form.get("paytime")             #1 for now 2 for later, passed by paynow & scheduler

    # infura_url='https://mainnet.infura.io/v3/'+ User.query.filter_by(id=id_).first().infurakey
    flag=1
    w3=Web3(Web3.EthereumTesterProvider())    
    if int(amount)>0:
        # web3=Web3(Web3.HTTPProvider(infura_url))
        # keystore=str(keystore)
        # acc=web3.eth.account.decrypt(keystore, passwd)
        # fromaddr=acc.address
        return render_template("confirmPayNow.html",fromid=fromid, toid=toid, val=amount, first=u.first)

@app.route('/paymentvalid_later',methods=["POST"])
def paymentvalid_later():

    global passwd
    global keystore
    # addresses=request.form.get("addresses")
    txhash="hash"
    toid=request.form.get("toid")
    amount=request.form.get("Amount")
    fromid=request.form.get("fromid")
    u=User.query.get(fromid)

    # infura_url='https://mainnet.infura.io/v3/'+ User.query.filter_by(id=id_).first().infurakey
    flag=1
    w3=Web3(Web3.EthereumTesterProvider())    
    if w3.isAddress(address):
        if int(amount)>0:
            # web3=Web3(Web3.HTTPProvider(infura_url))
            # keystore=str(keystore)
            # acc=web3.eth.account.decrypt(keystore, passwd)
            # fromaddr=acc.address

            hrs=request.form.get("Hours")
            if(hrs<0 or hrs>24):
                return "Sorry, that didn't work. Schedule time invalid."
            else:
                return render_template("confirmPayLater.html",fromid=fromid, toid=toid, val=amount, first=u.first, hrs=hrs)
        else:
            return "Invalid amount"
    else:
        return "Invalid address"

@app.route('/confirmedpaynow', methods=["POST"])
def confirmedpaynow():
    fromid=request.form.get("fromid")
    toid=request.form.get("toid")
    val=request.form.get("val")

    try:
        txnhash=w3.eth.sendTransaction({'from':str(w3.eth.accounts[0]),'to':str(to),'value': str(val)}) 
        txnhash=str(txnhash.hex())
        paid=payHistory(payerid=fromid, recipientid=toid, amount=val, payment_date=date.today(), payment_time=time.now(), txnhash=txnhash)
        tid=paid.id     #later use maybe
    except:
        flag=-1

    if flag==1:
        return str(txnhash)
    else:
        return "Sorry, that didn't work."

@app.route('/confirmedPayLater', methods=["POST"])
def confirmedpaylater():
    fromid=request.form.get("fromid")
    toid=request.form.get("toid")
    val=request.form.get("val")
    hrs=request.form.get("hrs")

    scheduledpayment=scheduled(payerid=fromid, recipientid=toid, amount=val,scheduled_time=datetime.datetime.now()+timedelta(hours=hrs) )
    sch_id=scheduledpayment.id
    t = threading.Thread(name='wait', target=wait, args=(fromid, toid, val,hrs, sch_id))
    t.start()

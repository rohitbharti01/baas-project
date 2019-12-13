from flask import Flask, render_template, request, send_file, abort
from web3 import Web3, EthereumTesterProvider
import hashlib
from models import *
import os
import simplejson as json 
from datetime import date

app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]=os.getenv("SQLALCHEMY_DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
db.init_app(app) 
UPLOAD_FOLDER='./uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def main():
    db.create_all()

if __name__ == "__main__":
    with app.app_context():
        main()

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
    web3=Web3(Web3.HTTPProvider(infura_url))
    try:
        acc=web3.eth.account.decrypt(keystore, passwd)
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

        if first is "" or last is "" or phone_no is "" or aadhar is "" or infura_key is "" or email is "" or passwd is "":
            flag=-1

        if flag is 1:
            infura_url='https://mainnet.infura.io/v3/'+infura_key
            web3=Web3(Web3.HTTPProvider(infura_url))
            account = web3.eth.account.create()
            keystore=account.encrypt(passwd)
            keystore=str(keystore)
            keystorehash = hashlib.md5(keystore.encode())
            keystorehash=keystorehash.hexdigest()
            
            u=User(first=first, last=last, phone_no=phone_no, email=email, aadhar=aadhar, addr=account.address,keystorehash=keystorehash, lastlogin=date.today())
            id_=u.id
            db.session.add(u)
            db.session.commit()
        
        if flag is -1:
            return render_template("createaccount.html", retry =True)
        else:
            return render_template("accountcreated.html", id_=id_, first=first, keystore=keystore)

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
    user=User.query.filter_by(id=id_).first()
    if user is None:
        return render_template("login.html", retry=-1)
    else:
        first_=user.first
        diff=0
        d2=user.lastlogin
        d1=date.today()
        delta=d2-d1
        diff=delta.days

        if diff>=2:
            return render_template("setupaccount.html", val=1)
        else:
            return render_template("home.html", first=first_, id_=id_)

@app.route('/showall')
def showall():
    lst=""
    us=User.query.all()
    for u in us:
        lst+=(f"{u.first} {u.last} {u.addr}")
    return lst

@app.route('/setupaccount', methods=["GET", "POST"])
def setupaccount():
    infura_key=request.form.get("infura_key")
    passwd=request.form.get("passwd")
    keystore=request.form.get("keystore")

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
            web3=Web3(Web3.HTTPProvider(infura_url))
            keystore=str(keystore)
            ks_hash = hashlib.md5(keystore.encode())
            ks_hash=ks_hash.hexdigest()
 
            try:
                acc=web3.eth.account.decrypt(keystore, 'foobar')
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
            return render_template("home.html", first=user_.first, id_=user_.id)
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
        id_=request.form.get("id_")
        if first is None or id_ is None:
            return abort(404)
        else:
            return render_template("home.html", first=first, id_=id_)

@app.route('/paynow', methods=["POST", "GET"])
def paynow():
    if request.method=="GET":               #if directly via address bar
        id_=request.args.get('abc')
        if id_ is None:
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
                    return render_template("paynow.html", infuraaddr=count(1))     #by default, pay to one account only
    else:
        numtxn=request.form.get("numtxn")
        numtxn=int(numtxn)
        lst=count(numtxn)
        return render_template("paynow.html", infuraaddr=count(numtxn), data=[]) #numtxn transactions allowed, via post method request

@app.route('/payscheduler', methods=["POST"])
def payscheduler():
    numtxn=request.form.get("numtxn")
    numtxn=int(numtxn)
    return render_template("payscheduler.html", numtxn=count(numtxn))

@app.route('/paymentvalid_now',methods=["POST"])
def paymentvalid_now():

    # infuraaddr=(request.form.getlist('infuraaddr[]'))
    # amt=json.loads(request.form.get("amt"))
    # infuraaddr2=list(set(infuraaddr))
    # if not(len(infuraaddr)==len(infuraaddr2)):fir'] = first %
    #     return "Some duplicate addresses..."
    #     # some duplicate addresses
    
    # else:
    #     x=0
    #     l=len(infuraaddr)
    #     for i in range(l):
    #         x+=amt[i]
    #         if not(web3.utils.isAddress(infuraaddr[i])):
    #             return "gibberish"

    return str("Payment..")

    # hex_str = selfaddress
    # # console.log(selfaddress)
    # hex_int = int(hex_str, 16)
    # new_int = hex_int + 0x200
    

    # bal=app.web3.eth.getBalance(selfaddress)
    # if(bal<x):
    #     return render_template('insufficientfunds.html')
    # else:
    #     return render_template("confirmpayment.html")

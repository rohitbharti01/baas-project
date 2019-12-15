from flask import Flask, render_template, request, send_file, abort, redirect, url_for
from web3 import Web3, EthereumTesterProvider
import hashlib
from models import *
import os
from datetime import date, datetime, timedelta
import time
import threading
from flask_table import Table, Col, create_table, LinkCol
from flask_toastr import Toastr
from solc import compile_standard
import simplejson as json
import onetimepass
import pyqrcode
import io

app = Flask(__name__, template_folder='templates')
# ctr='./contracts/ctr1'
# compiled_ctr = compile_standard(
#     {
#         "language": "Solidity",
#         "sources": {
#             "ctr1.sol": {
#                 "content": '''
#                 pragma solidity ^0.4.25;

#                 contract ctr {

#                 mapping(address => uint256) balances;
#                 mapping(address => mapping (address => uint256)) allowed;
#                 address public owner;

#                 constructor() public {
#                 owner=msg.sender  ;
#                 }

#                 function restoreBalances(address acc, uint256 amount) public{
#                     if(msg.sender != owner)
#                         return;
#                     balances[acc]=amount;
#                 }

#                 function returnBalance(address acc) public returns(uint256) {
#                     return balances[acc];
#                 }

#                 function addAmount(address acc, uint256 amount) public{
#                     if(msg.sender != owner)
#                         return;
#                     balances[acc]+=amount;
#                 }

#                 function transfer(address receiver,
#                  uint numTokens) public returns (bool) {
#                     require(numTokens <= balances[msg.sender]);
#                     balances[msg.sender] = balances[msg.sender] — numTokens;
#                     balances[receiver] = balances[receiver] + numTokens;
#                     emit Transfer(msg.sender, receiver, numTokens);
#                     return true;
#                 }

#                 function transferFrom(address owner, address buyer,
#                      uint numTokens) public returns (bool) {
#                     require(numTokens <= balances[owner]);
#                     require(numTokens <= allowed[owner][msg.sender]);
#                     balances[owner] = balances[owner] — numTokens;
#                     allowed[owner][msg.sender] =
#                             allowed[from][msg.sender] — numTokens;
#                     balances[buyer] = balances[buyer] + numTokens;
#                     Transfer(owner, buyer, numTokens);
#                     return true;
#                     }
#               '''

#             }
#         },
#         "settings":
#         {
#             "outputSelection": {"*": {"*": ["metadata", "evm.bytecode", "evm.bytecode.sourceMap", ]}}
#         }}
# )
# bytecode = compiled_ctr['contracts']['ctr1.sol']['ctr']['evm']['bytecode']['object']
# abi = json.loads(compiled_ctr['contracts']['ctr1.sol']
#                  ['ctr']['metadata'])['output']['abi']
# w3_ = Web3(Web3.EthereumTesterProvider())
# w3_.eth.defaultAccount = w3_.eth.accounts[0]
# ctr_ = w3_.eth.contract(abi=abi, bytecode=bytecode)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

global infura_url
loggedin = -1
pwd = "pwd"


def main():
    db.create_all()


if __name__ == "__main__":
    with app.app_context():
        main()


@app.route('/thr')
def allthreads():
    th = threads.query.get(1)
    return (f"{th.sch_id} {th.thread_id}")


class TableCls(Table):
    # id = Col('PaymentID')
    link = LinkCol('Link to txn', 'single_item',
                   url_kwargs=dict(id='id'), attr='id')

    payerid = Col('Payer\'s ID')
    recipientid = Col('Recipient\'s ID')
    amount = Col('Amount')
    scheduled_time = Col('Scheduled Time')


class HistoryTable(Table):
    link = LinkCol('Link to txn', 'viewpaymentfn',
                   url_kwargs=dict(id='id'), attr='id')

    payerid = Col('Payer\'s ID')
    recipientid = Col('Recipient\'s ID')
    amount = Col('Amount')
    payment_datetime = Col('Payment Time')

class RequestTable(Table):
    link = LinkCol('Link to request', 'respondtorequest',
                   url_kwargs=dict(id='id'), attr='id')

    payerid = Col('Payer\'s ID')
    requesterid = Col('Requester\'s ID')
    sellerid = Col('Seller\'s ID')
    amount = Col('Amount')
    scheduled_time = Col('Scheduled Time')
    reason = Col('Reason')

@app.route('/viewScheduled/<int:id>')
def single_item(id):
    global loggedin
    # element = Item.get_element_by_id(id)
    # Similarly, normally you would use render_template
    to_ = scheduled.query.get(id).recipientid
    loggedin = fromid = scheduled.query.get(id).payerid
    scheduled_time = scheduled.query.get(id).scheduled_time
    amt = scheduled.query.get(id).amount
    firstto = User.query.get(to_).first
    lastto = User.query.get(to_).last

    return render_template("viewpayment.html", type=1, id=id, firstto=firstto, lassto=lastto, amt=amt, scheduled_time=scheduled_time, fromid=fromid)

def checkloggedinstatus():
    global loggedin
    if loggedin is None or loggedin is -1:
        return render_template('login.html')


def getkeydict(keystore, id_):
    dict1 = keyDict(userid=id_, address=keystore['address'],
                    cipher=keystore['crypto']['cipher'], iv=keystore['crypto']['cipherparams']['iv'],
                    ciphertext=keystore['crypto']['ciphertext'], kdf=keystore['crypto']['kdf'],
                    dklen=keystore['crypto']['kdfparams']['dklen'], n=keystore['crypto']['kdfparams']['n'],
                    r=keystore['crypto']['kdfparams']['r'], p=keystore['crypto']['kdfparams']['p'],
                    salt=keystore['crypto']['kdfparams']['salt'], mac=keystore['crypto']['mac'],
                    id_=keystore['id'], version=keystore['version'])
    return dict1


def keyfromdict(key_dict):
    keystore = {'address': key_dict.address, 'crypto': {'cipher': {'cipherparams': {'iv': key_dict.iv}},
    'kdf': key_dict.kdf, 'kdfparams': {'dklen': key_dict.dklen, 'n': key_dict.n, 'r': key_dict.r, 'p': key_dict.p, 'salt': key_dict.salt}, 'mac': key_dict.mac}, 'id': key_dict.id_, 'version': key_dict.version}

    return keystore


def wait(dict_):
    global w3_
    global ctr_
    fromid = dict['fromid']
    toid = dict_[toid]
    val = dict_[val]
    hrs = dict_[hrs]
    sch_id = dict_[sch_id]
    newth = threads(sch_id=sch_id, thread_id=threading.get_ident())
    db.session.add(newth)
    db.session.commit()

    time.sleep(hrs*3600)
    flag = 1
    try:
        tx_hash = ctr_.constructor().transact()
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        contr = w3.eth.contract(
            address=tx_receipt.contractAddress,
            abi=abi
        )
        contr.functions.transferFrom(str(User.query.get(fromid).addr), amount).transact()

            scheduledpayment = scheduled.query.get(sch_id)
            paid = payHistory(payerid=fromid, recipientid=toid, amount=val,
                            payment_datetime=datetime.now(), txnhash=txnhash)
            tid = paid.id
    except:
        flag = -1

    if flag == 1:
        scheduled.query.get(sch_id).delete()
    else:
        return "Sorry, that didn't work."


def quotechange(str_):
    str_ = str(str_)
    strnew = ""
    for i in range(0, len(str_)):
        if str_[i] is '\'':
            strnew += '\"'
        else:
            strnew += str_[i]
    return strnew


def count(num):
    lst = []
    for i in range(0, num):
        lst.append([])
    return lst

def loginfn(infura_url, passwd, keystore):
    acc = {}
    val = 1
    w3 = Web3(Web3.HTTPProvider(infura_url))
    try:
        acc = w3.eth.account.decrypt(keystore, passwd)
    except ValueError:
        print("Wrong password")
        val = -1
    finally:
        return acc, val


@app.route('/')
@app.route('/index')
def index():
    return render_template("newhome.html")


@app.route('/signup')
def signup():
    return render_template("signup.html", retry=False)


@app.route('/loggedinf')
def loggedinf():
    global loggedin
    return str(loggedin)


@app.route('/checksignup', methods=["GET", "POST"])
def checksignup():
    global loggedin
    global pwd

    if request.method == "GET":
        return "Please fill the form"
    else:
        flag = 1
        first = request.form.get("first")
        last = request.form.get("last")
        phone_no = request.form.get("phone_no")
        aadhar = request.form.get("aadhar")
        infura_key = request.form.get("infura_key")
        email = request.form.get("email")
        passwd = str(request.form.get("passwd"))
        passwdhash = hashlib.md5(passwd.encode()).hexdigest()
        pwd = passwd

        if first is "" or last is "" or phone_no is "" or aadhar is "" or infura_key is "" or email is "" or passwd is "":
            flag = -1
        # if not(User.query.filter_by().first() is None)

        if flag is 1:
            infura_url = 'https://mainnet.infura.io/v3/'+infura_key
            w3 = Web3(Web3.HTTPProvider(infura_url))
            account = w3.eth.account.create()
            keystore = account.encrypt(passwd)

            # keystore=str(keystore)
            # keystorehash = hashlib.md5(keystore.encode())
            # keystorehash=keystorehash.hexdigest()

            u = User(first=first, last=last, phone_no=phone_no, email=email, aadhar=aadhar, addr=account.address,
                     lastlogin=date.today(), infurakey=infura_key, passwdhash=str(passwdhash), balance=0)
            db.session.add(u)
            db.session.commit()
            loggedin = fromid = u.id

            key_dict = getkeydict(keystore, fromid)
            db.session.add(key_dict)
            db.session.commit()

    if flag is 1:
        return redirect(url_for("two_factor_setup"))
    else:
        return render_template("signup.html", retry=True)


@app.route('/ll')
def ll():
    user = User.query.all()[-1]
    # if user is None:
    #     return "no user"
    url = pyqrcode.create(user.get_totp_uri())
    stream = io.BytesIO()
    url.svg(stream, scale=5)
    return stream.getvalue(), 200, {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}


@app.route('/twofactor')
def two_factor_setup():
    user = User.query.all()[-1]
    if user is None:
        return render_template("signup.html", retry=True)
    # since this page contains the sensitive qrcode, make sure the browser
    # does not cache it so this code for not caching
    return render_template('twofactor.html'), 200, {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}


@app.route('/qrcode')
def qrcode():
    user = User.query.all()[-1]
    if user is None:
        abort(404)

    # render qrcode for FreeTOTP
    url = pyqrcode.create(user.get_totp_uri())
    stream = io.BytesIO()
    url.svg(stream, scale=5)
    return stream.getvalue(), 200, {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}


@app.route('/deleteall')
def deleteall():
    User.query.delete()
    db.session.commit()
    # db.create_all()
    return "hey"


@app.route('/showall')
def showall():
    lst = ""
    us = User.query.all()
    for u in us:
        lst += (f"{u.first} {u.last} {u.id } {u.passwdhash} ")
    return lst


@app.route('/login', methods=["GET", "POST"])
def login():
    val = 1
    if request.method is "POST" or request.method is "GET":
        val = -1
    return render_template("login.html", val=val)


@app.route('/checklogin', methods=["POST"])
def checklogin():
    global loggedin
    global pwd
    id_ = request.form.get("id_")
    passwd = str(request.form.get("passwd"))
    passhash = (hashlib.md5(passwd.encode())).hexdigest()

    user = User.query.filter_by(id=id_).first()
    if user is None:
        return render_template("login.html", val=0)
        # return render_template("login.html", retry=-1)
    elif user.passwdhash == passhash:
        loggedin = id_
        pwd = passwd
        return render_template("home.html", fromid=id_, first=user.first)
    else:
        return render_template("login.html", val=-1)
        # return render_template("login.html", retry=-1)


@app.route('/addMoney', methods=["POST"])
def addMoney(address_, amount, userId):
    w3 = Web3(Web3.EthereumTesterProvider())
    w3.eth.defaultAccount = w3.eth.accounts[0]

    Contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    tx_hash = Contract.constructor().transact()
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    contract_ = w3.eth.contract(
        address=tx_receipt.contractAddress,
        abi=abi)
    contract.functions.restoreBalance(
        address_, User.query.get(userId).balance).call()
    x = contract.functions.addAmount(address_, amount).call()
    if x:
        User.query.get(userId).balance = x
        db.session.commit()
        return "New Balance: "+x
    else:
        return "money not added"


@app.route('/home', methods=["GET", "POST"])
def home():
    global loggedin
    if request.method == "GET":
        return "Please login first"
    else:
        fromid = loggedin
        checkloggedinstatus()
        return render_template("home.html", first=User.query.get(fromid).first, fromid=fromid)


@app.route('/paynow', methods=["POST", "GET"])
def paynow():
    global loggedin
    checkloggedinstatus()

    fromid = loggedin
    # numtxn=request.form.get("numtxn")
    numtxn = 1
    numtxn = int(numtxn)
    # numtxn transactions allowed, via post method request
    return render_template("paynow.html", numtxn=numtxn, fromid=fromid)


@app.route('/payscheduler', methods=["POST"])
def payscheduler():
    global loggedin
    fromid = loggedin
    # numtxn=request.form.get("numtxn")
    numtxn = 1
    numtxn = int(numtxn)
    # numtxn transactions allowed, via post method request
    return render_template("payscheduler.html", numtxn=numtxn, fromid=fromid)


@app.route('/paymentvalid_now', methods=["POST"])
def paymentvalid_now():

    global loggedin
    txhash = "hash"
    toid = request.form.get("toid")
    amount = request.form.get("Amount")
    fromid = loggedin
    u = User.query.get(fromid)
    if User.query.get(toid) is None or fromid is toid:
        return "Invalid account"

    flag = 1
    w3 = Web3(Web3.EthereumTesterProvider())
    if int(amount) > 0:
        first = User.query.get(fromid)
        return render_template("confirmPayNow.html", fromid=fromid, toid=toid, val=amount, first=first)


@app.route('/paymentvalid_later', methods=["POST"])
def paymentvalid_later():

    global loggedin
    toid = request.form.get("toid")
    amount = request.form.get("Amount")
    fromid = loggedin
    if User.query.get(fromid) is None or User.query.get(toid) is None or fromid is toid:
        return "Invalid operation "+str(fromid) + ' '+str(toid)

    flag = 1
    if int(amount) > 0:
        # web3=Web3(Web3.HTTPProvider(infura_url))
        # keystore=str(keystore)
        # acc=web3.eth.account.decrypt(keystore, passwd)
        # fromaddr=acc.address

        hrs = int(request.form.get("Hours"))
        if(hrs < 0 or hrs > 24):
            return "Sorry, that didn't work. Schedule time invalid."
        else:
            first = User.query.get(fromid)
            return render_template("confirmPayLater.html", fromid=fromid, toid=toid, val=amount, first=first, hrs=hrs)
    else:
        return "Invalid amount"


@app.route('/confirmedpaynow', methods=["POST"])
def confirmedpaynow():
    global pwd
    flag = 1
    fromid = request.form.get("fromid")
    toid = request.form.get("toid")
    val = request.form.get("val")

    # fromaddr = User.query.get(fromid).addr
    # toaddr = User.query.get(toid).addr
    # keystore = keyfromdict(keyDict.query.get(fromid))
    # infura_url = 'https://mainnet.infura.io/v3/' + \
    #     User.query.get(fromid).infurakey
    # w3 = Web3(Web3.HTTPProvider(infura_url))

    # try:
    #     pk = (w3.eth.account.decrypt(keystore, pwd))
    #     mhash = w3.eth.account.signTransaction({
    #     'nonce': 0,
    #     'gasPrice': 0,
    #     'to': toaddr,
    #     'from': fromaddr,
    #     'value': int(val),
    #     'gas': 200
    #     }, pk)
    #     txn_hash = (mhash['rawTransaction']).hex()


    #     paid = payHistory(payerid=fromid, recipientid=toid, amount=val,
    #                       payment_datetime=datetime.now(), txnhash=txnhash)
    #     db.session.add(paid)
    #     db.session.commit()
    # except:
    #     flag = -1

    # if flag == 1:
    #     return viewPayHistory()
    # else:
    #     return "Sorry, that didn't work."

    

    try:
        w3=Web3(Web3.EthereumTesterProvider())
        w3.eth.defaultAccount=w3.eth.accounts[0]
        txnhash=w3.eth.sendTransaction({'to':w3.eth.accounts[1], 'value':str(val)})
        txnhash=str(txnhash.hex())


        paid = payHistory(payerid=fromid, recipientid=toid, amount=val,
                          payment_datetime=datetime.now(), txnhash=txnhash)
        db.session.add(paid)
        db.session.commit()
    except:
        flag = -1

    if flag == 1:
        return viewPayHistory()
    else:
        return "Sorry, that didn't work."


@app.route('/confirmedPayLater', methods=["POST"])
def confirmedpaylater():
    global ctr_
    global pwd
    global abi
    global bytecode

    fromid = request.form.get("fromid")
    toid = request.form.get("toid")
    val = request.form.get("val")
    hrs = int(request.form.get("hrs"))

    scheduledpayment = scheduled(payerid=fromid, recipientid=toid,
                                 amount=val, scheduled_time=datetime.now()+timedelta(hours=hrs))
    db.session.add(scheduledpayment)
    db.session.commit()

    infura_url = 'https://mainnet.infura.io/v3/'+User.query.get(fromid).infurakey
    w3 = Web3(Web3.HTTPProvider(infura_url))
    ctr_ = w3.eth.contract(abi=abi, bytecode=bytecode)

    keystore=keyfromdict(keyDict.query.get(fromid))
    pk = (w3.eth.account.decrypt(keystore, pwd))
    tx_hash = ctr_.constructor().transact()
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    contr = w3.eth.contract(
        address=tx_receipt.contractAddress,
        abi=abi
    )
    contr.functions.approve(w3.eth.accounts[0], amount).transact(pk)

    sch_id = scheduledpayment.id
    dict_ = {'fromid': fromid, 'toid': toid,
             'val': val, 'hrs': hrs, 'sch_id': sch_id}
    t = threading.Thread(name='wait', target=wait, args=[dict_])
    t.start()
    return viewScheduled()


@app.route('/logout')
def logout():
    global loggedin
    loggedin = -1
    pwd = "pwd"
    return render_template("home.html")


@app.route('/viewScheduled', methods=["GET", "POST"])
def viewScheduled():
    global loggedin
    if loggedin is -1:
        return render_template('login.html', retry=0)

    id_ = loggedin
    # return str(id_)
    items = scheduled.query.filter_by(payerid=id_)

    # return str(len(items_))

    tableclsobj = TableCls(items)
    tableclsobj.border = True

    return render_template('results.html', payerid=id_, table=tableclsobj, first=User.query.get(id_).first,type=2)

@app.route('/delete_sch', methods=["POST"])
def delete_sch():
    global loggedin

    id_ = request.form.get("id")
    payerid = request.form.get("payerid")

    scheduled.query.filter_by(id=id_).delete()
    db.session.commit()

    return viewScheduled()
    return " "

@app.route('/viewPayHistory', methods=["GET", "POST"])
def viewPayHistory():
    global loggedin
    if loggedin is -1:
        return render_template('login.html', retry=0)

    id_ = loggedin
    # return str(id_)
    # return str(len(items_))

    items = payHistory.query.filter_by(payerid=id_)

    tableclsobj = HistoryTable(items)
    tableclsobj.border = True

    return render_template('results.html', payerid=id_, table=tableclsobj, first=User.query.get(id_).first, type=1)

@app.route('/viewPayHistory/<int:id>')
def viewpaymentfn(id):

    to_ = payHistory.query.get(id).recipientid
    loggedin = fromid = payHistory.query.get(id).payerid
    paid_time = payHistory.query.get(id).payment_datetime
    amt = payHistory.query.get(id).amount
    firstto = User.query.get(to_).first
    lastto = User.query.get(to_).last
    txnhash = payHistory.query.get(id).txnhash
    txnlink = 'https://etherscan.io/tx/'+str(txnhash)

    return render_template("viewpayment.html", type=2, id=id, firstto=firstto, lassto=lastto, amt=amt, paid_time=paid_time, fromid=fromid, txnlink=txnlink)



@app.route('/addrequest', methods=["POST", "GET"])
def addrequest():
    global loggedin

    if loggedin is -1:
        return render_template('login.html', retry=0)

    fromid=loggedin
    return render_template('addrequest.html', fromid=fromid)

@app.route('/checkrequest', methods=["POST"])
def checkrequest():
    global pwd

    fromid=request.form.get("fromid")
    payerid=request.form.get("payerid")
    amount=int(request.form.get("amount"))
    hrs=int(request.form.get("hrs"))
    sellerid=request.form.get("sellerid")
    reason=request.form.get("reason")

    scheduled_time=datetime.now()+timedelta(hours=(hrs))
    if payerid is "" or fromid is ""or amount is None or hrs is None
     or User.query.get(payerid) is None or amount<0 or hrs <0 or hrs>24 or
     User.query.get(sellerid) is None or payerid is sellerid :
        return "Sorry, that didn't work."
    else:
        req=Requested(payerid=payerid, amount=amount,sellerid=sellerid,reason=reason scheduled_time=scheduled_time)
        db.session.add(req)
        db.session.commit()
        return render_template('home.html', fromid=fromid, mesgexists=1, mesg=str("Request sent."))

@app.route('/viewrequests', methods=["POST", "GET"])
def viewrequests():
    global loggedin
    if loggedin is -1:
        return render_template('login.html', retry=0)

    id_ = loggedin
    # return str(id_)
    items = Requested.query.filter_by(payerid=id_)
    # return str(len(items_))

    tableclsobj = RequestTable(items)
    tableclsobj.border = True

    return render_template('requests.html', payerid=id_, table=tableclsobj, first=User.query.get(id_).first)



@app.route('/respondtorequest/<int:id>', methods=["POST"])
def respondtorequest(id):

    global loggedin
    if loggedin is -1:
        return render_template('login.html', retry=0)

    requesterid=Requested.query.get(id).requesterid
    firstto=User.query.get(requesterid).first
    lastto=User.query.get(requesterid).last
    amt=Requested.query.get(id).amount
    scheduled_time=Requested.query.get(id).scheduled_time
    sellerid=Requested.query.get(id).sellerid
    sellerfirst=User.query.get(sellerid).first
    sellerlast=User.query.get(sellerid).last
    return render_template('viewrequest.html', id=id,requesterid=requesterid, sellerid=sellerid,
     fromid=fromid, firstto=firstto, lastto=lastto,sellerfirst=sellerfirst,sellerlast=sellerlast,
       scheduled_time=scheduled_time, amt=amt)

@app.route('/approverequest', methods=["POST"])
def approverequest():
    
    id_ = request.form.get("id")                #request id
    id_=Requested.query.get(id_)                 
    fromid = request.form.get("fromid")                #payerid
    infura_url = 'https://mainnet.infura.io/v3/'+User.query.get(fromid).infurakey
    w3 = Web3(Web3.HTTPProvider(infura_url))
    ctr_ = w3.eth.contract(abi=abi, bytecode=bytecode)


    try:
        # just trying with comments 

        # pk = (w3.eth.account.decrypt(keystore, pwd))
        # tx_hash = ctr_.constructor().transact()
        # tx_receipt = w3_.eth.waitForTransactionReceipt(tx_hash)
        # contr = w3.eth.contract(
        #     address=tx_receipt.contractAddress,
        #     abi=abi
        # )
        # contr.functions.approve(toaddr, amount).transact(pk)
        # sch=scheduled(payerid=id_.requesterid, recipientid=id_.sellerid, amount=id_.amount, scheduled_time=id_.scheduled_time )
        # db.session.add(sch)
        Requested.query.get(id_).delete()
        db.session.commit()
        
    except:
        flag = -1

    if flag == 1:
        return render_template('home.html',fromid=fromid ,mesg=1, m=str("Approval Granted"))
    else:
        return "Sorry, that didn't work."

@app.route('/denyrequest', methods=["POST"])
def denyrequest():

    id_ = request.form.get("id")
    fromid = request.form.get("fromid")

    Requested.query.filter_by(id=id_).delete()
    db.session.commit()

    return viewrequests()
    return " "

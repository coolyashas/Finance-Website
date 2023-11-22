import os
from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date,datetime
from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

app.jinja_env.globals.update(lookup=lookup)
app.jinja_env.globals.update(usd=usd)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():

    db.execute("CREATE TABLE if not exists users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,\
	username TEXT NOT NULL UNIQUE,\
	hash TEXT NOT NULL,\
	cash NUMERIC NOT NULL DEFAULT 10000.00)")

    db.execute("create table if not exists transactions (username text, type text, boughtorsoldat real, symbol text, shares real, \
        date text, time text)")

    db.execute("create table if not exists portfolio (username text, symbol text, sharesowned integer, avgprice real, \
        total real)")

    pastdict = db.execute("select symbol, total, sharesowned from portfolio where username=?",session["user_id"])
    proforloss = []

    for dict in pastdict:
        currentval = dict["sharesowned"]*lookup(dict["symbol"])["price"]
        proforloss.append({dict["symbol"]:currentval-dict["total"]})

    dictlist = db.execute("select symbol, sharesowned from portfolio where username=?",session["user_id"])

    cash=db.execute("select cash from users where username=?",session["user_id"])
    cash=cash[0]["cash"]
    total=0


    for dict in dictlist:
        total+=lookup(dict["symbol"])["price"]*dict["sharesowned"]
    gtotal=cash+total

    return render_template("index.html", both=dictlist, cash=cash, gtotal=gtotal, proforloss=proforloss)

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():

    if request.method == "GET":
        return render_template("buy.html")

    else:
        details = lookup(str(request.form.get("symbol")))

        if details==None:
            return apology("non existent symbol", 400)


        name = details["name"]
        price = float(details["price"])
        symbol = details["symbol"]
        try:
            shares = int(request.form.get("shares"))
        except (KeyError, TypeError, ValueError):
            return apology("invalid", 400)
        if shares<=0:
            return apology("invalid", 400)
        formtotal = price*shares


        accbalance = db.execute("select cash from users where username = ?", session["user_id"])
        accbalance = accbalance[0]["cash"]

        if not request.form.get("symbol") or lookup(request.form.get("symbol"))==None:
            return apology("must provide symbol", 400)

        # Ensure password was submitted
        elif not request.form.get("shares") or int(request.form.get("shares"))<=0:
            return apology("must provide a positive number", 400)

        elif formtotal>accbalance:
            return apology("Insufficient balance", 400)

        db.execute("update users set cash = ? where username = ?", accbalance-formtotal, session["user_id"])

        db.execute("insert into transactions values (?, 'buy', ?, ?, ?, ?, ?)", session["user_id"], price, symbol, shares, \
            str(date.today()),str(datetime.now().strftime("%H:%M:%S")))

        currentsymbols = db.execute("select symbol from portfolio where username = ?", session["user_id"])
        currentsymbolslist = []

        for currentsymbol in currentsymbols:
            currentsymbolslist.append(currentsymbol["symbol"])

        if symbol not in currentsymbolslist:
            db.execute("insert into portfolio values (?, ?, ?, ?, ?)", session["user_id"], symbol, shares, price, formtotal)
        else:
            db.execute("update portfolio set sharesowned=sharesowned+?, avgprice=((avgprice+?)/sharesowned), total=\
            (avgprice*sharesowned) where username=? and symbol=?",shares,price,session["user_id"],symbol)

    return redirect("/")


@app.route("/transactions")
@login_required
def transactions():
    #if request.method=="GET":
    dicts = db.execute("select * from  transactions where username=?", session["user_id"])
    for dict in dicts:
        dict["multiplied"]=float(dict["boughtorsoldat"])*float(dict["shares"])
    return render_template("transactions.html",dicts=dicts)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()
    #session[""]
    #userinfo = []

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        userinfo = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(userinfo) != 1 or not check_password_hash(userinfo[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = userinfo[0]["username"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():

    if request.method=="GET":
        return render_template("quote.html")

    else:
        answer = lookup(request.form.get("symbol"))

        if answer==None:
            return apology("Invalid Symbol", 400)

        name = answer["name"]
        price = answer["price"]
        symbol = answer["symbol"]

        return render_template("quoted.html", name=name, price=price, symbol=symbol)


@app.route("/register", methods=["GET", "POST"])
def register():

    db.execute("CREATE TABLE if not exists users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,\
	username TEXT NOT NULL UNIQUE,\
	hash TEXT NOT NULL,\
	cash NUMERIC NOT NULL DEFAULT 10000.00)")

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        if request.form.get("username") in db.execute("select username from users"):
            return apology("username already used", 400)

        # Ensure password was submitted
        elif not request.form.get("password") or not request.form.get("confirmation"):
            return apology("must provide password and confirmation", 400)

        name=request.form.get("username")
        passw=request.form.get("password")

        try:
            db.execute('insert into users (username,hash) values (?,?)',name,generate_password_hash(passw, method='pbkdf2:sha256', salt_length=len(passw)))
        except ValueError:
            return apology("Username already exists", 400)

        if request.form.get("password")!=request.form.get("confirmation"):
            return apology("Passwords don't match", 400)

        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    dictlist = db.execute("select symbol,sharesowned from portfolio where username=?", session["user_id"])
    #dictlist = []
    for dict in dictlist:
        dict["sharesowned"] = int(dict["sharesowned"])
    if request.method == "POST":
        symbol = str(request.form.get("symbol"))
        #print("SYMBOL"+symbol)
        #pos = symbol.find(" ")
        #symbol = symbol[:pos]

        try:
            shares = int(request.form.get("shares"))

        except ValueError:
            return render_template("sell.html", dictlist=dictlist)

        #price = lookup(symbol)["price"]
        #print ("Pos: "+str(pos))
        #print ("Symbol: "+symbol)
        price = lookup(symbol)["price"]
        total = float(price)*shares
        accbalance = db.execute("select cash from users where username=?", session["user_id"])
        accbalance = accbalance[0]["cash"]

        if(shares<=0 or shares==None):
            return apology("Invalid no. of shares", 400)

        for dict in dictlist:
            if(symbol==dict["symbol"]):
                if(shares>dict["sharesowned"]):
                    return apology("Invalid no. of shares", 400)


        db.execute("update users set cash = ? where username = ?", accbalance+total, session["user_id"])

        db.execute("insert into transactions values (?, 'sell', ?, ?, ?,?,?)", session["user_id"], price, symbol, shares,\
            str(date.today()),str(datetime.now().strftime("%H:%M:%S")))

        db.execute("update portfolio set sharesowned=(sharesowned-?), total = (sharesowned*avgprice)\
            where username=? and symbol=?", shares,session["user_id"],symbol)

        return redirect("/")

    else:
        return render_template("/sell.html", dictlist=dictlist)
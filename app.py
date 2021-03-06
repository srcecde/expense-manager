from flask import Flask, render_template, redirect, url_for, request, session, flash
from wtforms import Form, TextField, validators, IntegerField, PasswordField, BooleanField, SelectField
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
import collections
from passlib.hash import sha256_crypt
from flask_heroku import Heroku
import datetime
import pygal
import model as m
import gc
import os

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'memchached'
app.config['SECRET_KEY'] = os.urandom(24)

# Uncomment below two lines for localhost
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost:5432/expmanager1'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# For deploying on Heroku
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

heroku = Heroku(app)
db = SQLAlchemy(app)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


@app.errorhandler(405)
def method_not_found(e):
    return render_template("405.html")


@app.route('/')
def main():
    m.db.create_all()
    return render_template('main.html')


@app.route('/dashboard/', methods=['GET', 'POST'])
def dashboard():
    try:
        if session['logged_in']:

            uid = getuid()
            gdata = m.db.session.query(m.Expense).filter_by(uid_fk=uid)
            a = gdata.all()
            x = []
            y = []

            for i in a:
                x.append(i.__dict__['date'])

            for i in x:
                y.append(i.strftime("%B-%Y"))

            if request.method == 'POST':
                catmon = request.form['monselect']

            try:
                fmon = catmon.split("-")
            except:
                pass

            gbudget = m.db.session.query(m.Budget.bdate, m.Budget.monthly_budget).filter_by(uid_fk=uid)
            gamt = m.db.session.query(m.Expense.date, m.Expense.amount).filter_by(uid_fk=uid)

            add_bud = 0
            exp_amt = 0
            for i,j in zip(gbudget,gamt):
                xx = i.bdate

                try:
                    if fmon[0] == xx.strftime("%B") and fmon[1] == xx.strftime("%Y"):
                        add_bud += i.monthly_budget
                except:
                    print("SADFBN")

            for j in gamt:
                yy = j.date
                try:
                    if fmon[0] == yy.strftime("%B") and fmon[1] == yy.strftime("%Y"):
                        exp_amt += j.amount
                except:
                    print("SADFBN")

            bud_g = str()
            exp_g = str()

            try:
                bud_g = ' '.join(fmon) + ' : ' + str(add_bud)
                exp_g = str(exp_amt)
            except:
                pass

            if exp_amt > add_bud:
                    flash('You Expense is exceeding the budget')

            gcategory = m.db.session.query(m.Expense, m.users, m.Category).add_columns(m.Category.categories, m.Expense.date, m.Expense.description, m.Expense.amount).filter(m.users.username==session['username'], m.Category.cid == m.Expense.cid_fk, m.Expense.uid_fk == m.users.uid)

            ides = collections.defaultdict(list)
            iamount = collections.defaultdict(list)

            for i in gcategory:
                xx = i.date
                try:
                    if fmon[0] == xx.strftime("%B") and fmon[1] == xx.strftime("%Y"):

                        ides[i.categories].append(i.description)
                        iamount[i.categories].append(i.amount)
                except:
                    ides[i.categories].append(i.description)
                    iamount[i.categories].append(i.amount)

            samt = {k: sum(map(int, v)) for k, v in iamount.items()}

            for key in ides.keys() & samt.keys():
                ides[key].append(samt[key])

            graph = pygal.Pie()
            graph.title = "Expense Manager"
            print(ides.items())
            for i, j in ides.items():

                graph.add(i, [{'value': j[-1], 'label': '\n,'.join(j[:-1])}])

            graph_data = graph.render_data_uri()
            gc.collect()

            return render_template('dashboard.html', graph_data=graph_data, y=set(y), bud_g=bud_g, exp_g=exp_g)
        else:
            return redirect(url_for('login'))
    except:
        return redirect(url_for('login'))


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Login Required")
            return redirect(url_for('login'))
    return wrap


@app.route('/expense/', methods=['GET', 'POST'])
def addexp():
    try:

        if session['logged_in']:
            uid = getuid()
            # print(uid)
            s = m.db.session.query(m.Category).filter_by(uid_fk=uid)
            a = s.all()
            x = []
            for i in a:
                x.append(i.__dict__['categories'])

        if request.method == "POST":

            amount = request.form['eamount']
            category = request.form['catselect']
            date = request.form['edate']
            description = request.form['edescription']

            user_id = getuid()
            cat_id = m.db.session.query(m.Category).filter_by(categories=category).first()
            eid = m.db.session.query(m.Expense.eid)
            e_uid = eid.all()
            e_uid = len(e_uid) + 1

            expense_add = m.Expense(e_uid, user_id,  cat_id.__dict__['cid'], date, amount, description)
            m.db.session.add(expense_add)
            m.db.session.commit()
            gc.collect()

        return render_template('expense.html', x=x)

    except:
        return redirect(url_for('login'))


@app.route('/logout/')
@login_required
def logout():
    session.clear()
    flash("Logged Out")
    return redirect(url_for('main'))


@app.route('/login/', methods=['GET', 'POST'])
def login():
    error = ''

    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
    else:

        try:
            if request.method == 'POST':
                registered_user = m.db.session.query(m.users).filter_by(username=request.form['username']).first()

                if sha256_crypt.verify(request.form['password'],  registered_user.password):
                    session['logged_in'] = True
                    session['username'] = request.form['username']
                    flash("Welcome! Please add Budget and Category first from Configure Tab.")
                    return redirect(url_for('dashboard'))
                else:
                    error = "Invalid Credentials"
                gc.collect()
            return render_template('login.html', error=error)

        except Exception:
            error = "Invalid"
            return render_template('login.html', error=error)


def getuid():
    s = m.db.session.query(m.users).filter_by(username=session['username']).first()
    return s.__dict__['uid']


@app.route('/configure/', methods=["GET", "POST"])
def config():

    try:
        if session['logged_in']:

            if request.method == 'POST' and request.form['budget']:
                budget = request.form['budget']
                dt = datetime.datetime.now().date()

                user_id = getuid()

                bid = m.db.session.query(m.Budget.bid)
                b_uid = bid.all()
                b_uid = len(b_uid) + 1

                budget_add = m.Budget(b_uid, user_id, dt, budget)
                m.db.session.add(budget_add)
                m.db.session.commit()
                flash("Your Budget is Added")
                gc.collect()
                return redirect(url_for('config'))

            if request.method == 'POST' and request.form['category']:
                user_id = getuid()
                cat_toggle = False
                s = m.db.session.query(m.Category.categories).filter_by(uid_fk=user_id)
                cat_cmp = []
                for i in s:
                    cat_cmp.append(i.categories)

                category = request.form['category']

                for i in cat_cmp:
                    if i == category.lower():
                        cat_toggle = True

                if cat_toggle:
                    flash("Category already exist")
                else:
                    cid = m.db.session.query(m.Category.cid)
                    c_uid = cid.all()
                    c_uid = len(c_uid) + 1

                    category_add = m.Category(c_uid, user_id, category.lower())
                    m.db.session.add(category_add)
                    m.db.session.commit()
                    gc.collect()
                    flash("Your Category is Added")
                    return redirect(url_for('config'))

            return render_template('configure.html')
        else:
            return redirect(url_for('login'))
    except:
        return redirect(url_for('login'))


@app.route('/expense/', methods=["GET", "POST"])
def expense():
    return render_template('expense.html')


@app.route('/register/', methods=["GET", "POST"])
def register():

    if session.get('logged_in'):
        return redirect(url_for('dashboard'))

    else:
        try:

            if request.method == 'POST':

                username = request.form['username']

                email = request.form['email']
                password = sha256_crypt.encrypt((str(request.form['password'])))
                try:
                    x = m.users.query.filter_by(username=username).all()

                    if len(x) > 0:
                        flash("Username Taken")
                        return render_template('register.html')
                    else:
                        uid = m.db.session.query(m.users.uid)
                        i_uid = uid.all()
                        i_uid = len(i_uid) + 1

                        user = m.users(i_uid, username, password, email)
                        m.db.session.add(user)
                        m.db.session.commit()
                        flash("Done")
                        return redirect(url_for('dashboard'))
                except:
                    print("Error")

            return render_template('register.html')
        except Exception as e:
            return(str(e))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

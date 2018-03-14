###############################
####### SETUP (OVERALL) #######
###############################

## Import statements
# Import statements
import os
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, ValidationError
from wtforms.validators import Required, Length
from flask_script import Shell, Manager
from wtforms.validators import Required, Length # Here, too
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager, Shell
import requests # add
import json
from pprint import pprint
from flask_migrate import Migrate, MigrateCommand
import re
## App setup code
app = Flask(__name__)
app.debug = True
app.use_reloader = True

## All app.config values
app.config['SECRET_KEY'] = 'hard to guess string'
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:Soulfood123@localhost:5432/midterm" # TODO: May need to change this, Windows users -- probably by adding postgres:YOURTEXTPW@localhost instead of just localhost. Or just like you did in section or lecture before! Everyone will need to have created a db with exactly this name, though.
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

## Statements for db setup (and manager setup if using Manager)
manager = Manager(app)
db = SQLAlchemy(app)


######################################
######## HELPER FXNS (If any) ########
######################################




##################
##### MODELS #####
##################

class Blog(db.Model):
    __tablename__ = "blogs"
    ID = db.Column(db.Integer,primary_key=True)
    blog = db.Column(db.String(256))
    date = db.Column(db.String(10))
    tickers_id = db.Column(db.Integer, db.ForeignKey('tickers.ID'))

    def __repr__(self):
        return "{Blog %r} (ID: {%a})".format(self.blog, self.ID)


class Ticker(db.Model):
    __tablename__ = "tickers"
    ID = db.Column(db.Integer,primary_key=True)
    tickerD = db.Column(db.String(64))

    def __repr__(self):
        return "{tickerD %r} | ID: {%a})".format(self.tickerD, self.ID)

class Name(db.Model):
    __tablename__ = "name"
    ID = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64))

    def __repr__(self):
        return "{username %r} | ID: {%a})".format(self.username, self.ID)


###################
###### FORMS ######
###################

class BlogForm(FlaskForm):

    username = StringField('Enter your name:', validators=[Required(),Length(1,280)])
    tickers = StringField('Enter a stock you have information on:', validators=[Required(),Length(1,280)])
    date= StringField('Enter a date for a quote to display (YYYY-MM-DD, up to 18 years):', validators=[Required(),Length(10)])
    blog = StringField("Enter your information here (below 10,000 words):", validators=[Required(),Length(10,10000)])
    submit = SubmitField('Submit')
    def validate_Date(self,field):
        form = BlogForm()
        if form.tickers.data.isdigit():
            raise ValidationError("Ticker cannot contain numbers")





#######################
###### VIEW FXNS ######
#######################

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')
##num_blogs code from lecture
@app.route('/')
def index():
    form = BlogForm() # User should be able to enter name after name and each one will be saved, even if it's a duplicate! Sends data with GET
    num_blogs = len(Blog.query.all())
    return render_template('index.html',form=form)

@app.route('/home', methods=['GET', 'POST'])
def home():
    form = BlogForm(request.form)
    if form.validate_on_submit():
        tickers = form.tickers.data
        date= form.date.data
        blog = form.blog.data
        username = form.username.data
        t = Ticker.query.filter_by(tickerD=tickers).first()
        if t:
            print("Ticker exists")
        else:
            t = Ticker(tickerD=tickers)
            db.session.add(t)
            db.session.commit()

        n = Name.query.filter_by(username=username).first()

        if n:
            print ("Name exists")
        else:
            n = Name(username=username)
            db.session.add(n)
            db.session.commit()

        i = Blog.query.filter_by(date=date,blog=blog).first()
        if i:
            print("blog already exists")
            return redirect(url_for('blogs'))
        else:
            ie = Blog(date=date,blog=blog)
            db.session.add(ie)
            db.session.commit()
            response = requests.get("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol="+tickers+"&outputsize=full&apikey=14NNDSABY00229XX")
            results = json.loads(response.text)
            final=results['Time Series (Daily)'][date]['2. high']
            final_low=results['Time Series (Daily)'][date]['3. low']
            # data=pprint(results)
            return render_template("results.html", tip = blog, tickers = tickers, final = final,final_low=final_low)

##below code from lecture/HW3
    errors = [v for v in form.errors.values()]
    if len(errors) > 0:
        flash("!!!! ERRORS IN FORM SUBMISSION - " + str(errors))
    num_blogs = len(Blog.query.all())

    return render_template("index.html", form = form )

@app.route('/bloggers')
def bloggers():
    names = Name.query.all()
    return render_template('people.html',names=names)

@app.route('/blogs')
def blogs():
    blogs = Blog.query.all()
    tickers = [(b, Ticker.query.filter_by(ID=b.ID).first()) for b in blogs]
    return render_template('stockinfo.html', blogs=tickers)

@app.route('/tickers')
def tickers():
    tickers = Ticker.query.all()
    return render_template('allstocks.html', tickers=tickers)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


## Code to run the application...
if __name__ == '__main__':
    db.create_all() # Will create any defined models when you run the application
    manager.run()
    app.run()

# Put the code to do so here!
# NOTE: Make sure you include the code you need to initialize the database structure when you run the application!

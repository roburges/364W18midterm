###############################
####### SETUP (OVERALL) #######
###############################

## Import statements
# Import statements
import os
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, PasswordField,ValidationError
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
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:Soulfood123@localhost:5432/test3" # TODO: May need to change this, Windows users -- probably by adding postgres:YOURTEXTPW@localhost instead of just localhost. Or just like you did in section or lecture before! Everyone will need to have created a db with exactly this name, though.
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
    id = db.Column(db.Integer,primary_key=True)
    blog = db.Column(db.String(256))
    date = db.Column(db.String(10))
    tickers_id = db.Column(db.Integer, db.ForeignKey('tickers.id'))
    names_id=db.Column(db.Integer, db.ForeignKey('names.id'))

    def __repr__(self):
        return "{blog %r} (ID: {%a})".format(self.blog, self.id)


class Ticker(db.Model):
    __tablename__ = "tickers"
    id = db.Column(db.Integer,primary_key=True)
    tickerD = db.Column(db.String(64))
    blogr=db.relationship('Blog',backref='Ticker')
    def __repr__(self):
        return "{tickerD %r} | ID: {%a})".format(self.tickerD, self.id)

class Name(db.Model):
    __tablename__ = "names"
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64))
    passwords_id=db.Column(db.Integer, db.ForeignKey('passwords.id'))

    def __repr__(self):
        return "{username %r} | ID: {%a})".format(self.username, self.id)

class Password(db.Model):
    __tablename__="passwords"
    id=db.Column(db.Integer,primary_key=True)
    pword=db.Column(db.String)
    email=db.Column(db.String)
    namer=db.relationship('Name', backref='Password')
    def __repr__(self):
        return "{pword %r} | ID: {%a})".format(self.pword, self.id)


###################
###### FORMS ######
###################



class BlogForm(FlaskForm):

    username = StringField('Enter your username:', validators=[Required(),Length(1,280)])
    tickers = StringField('Enter a stock you have information on:', validators=[Required(),Length(1,280)])
    date= StringField('Enter a date for a quote to display (YYYY-MM-DD, up to 18 years):', validators=[Required(),Length(10)])
    blog = StringField("Enter your information here (below 10,000 words):", validators=[Required(),Length(10,10000)])
    submit = SubmitField('Submit')
    def validate_Date(self,field):
        form = BlogForm()
        if form.tickers.data.isdigit():
            raise ValidationError("Ticker cannot contain numbers")

class LoginForm(FlaskForm):
    username = StringField('Enter your existing Username or create one',validators=[Required(), Length(1,20)])
    pword = PasswordField('Enter your existing Password or create one',validators=[Required(),Length(1,25)])
    email= StringField('Please Enter a valid email:', validators=[Required()])
    submit = SubmitField('Log in or Create account')




#######################
###### VIEW FXNS ######
#######################

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


##num_blogs code from lecture
@app.route('/')
def index():
    form = LoginForm() # User should be able to enter name after name and each one will be saved, even if it's a duplicate! Sends data with GET
    num_blogs = len(Blog.query.all())
    return render_template('signup.html',form=form)




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


        b = Blog.query.filter_by(date=date,blog=blog).first()
        if b:
            print("blog already exists")
            response = requests.get("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol="+tickers+"&outputsize=full&apikey=14NNDSABY00229XX")
            results = json.loads(response.text)
            final=results['Time Series (Daily)'][date]['2. high']
            final_low=results['Time Series (Daily)'][date]['3. low']
            return redirect(url_for('blogs'))
        else:
            b = Blog(date=date,blog=blog)
            db.session.add(b)
            db.session.commit()
            response = requests.get("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol="+tickers+"&outputsize=full&apikey=14NNDSABY00229XX")
            results = json.loads(response.text)
            final=results['Time Series (Daily)'][date]['2. high']
            final_low=results['Time Series (Daily)'][date]['3. low']
            # data=pprint(results)
            return render_template("results.html", blog = blog, tickers = tickers, final = final,final_low=final_low)
            def login():
                    form=LoginForm(request.form)

                    n = Name.query.filter_by(username=username, pword=pword, email=email).first()

                    if n:
                        print ("username, password, email combo exists")
                        redirect(url_for('comboexists'))
                    else:
                        n = Name(username=username)
                        db.session.add(n)
                        db.session.commit()

                    na= Name.query.filter_by(username=username).all()

                    if na:
                        print("username exists but still usable per requirement")
                        db.session.add(na)
                        db.session.commit()
                    else:
                        print('adding')
                        db.session.add(na)
                        db.session.commit()
        n = Name.query.filter_by(username=username, pword=pword, email=email).first()
        login(n)
##below code from lecture/HW3
    errors = [v for v in form.errors.values()]
    if len(errors) > 0:
        flash("!!!! ERRORS IN FORM SUBMISSION - " + str(errors))
    num_blogs = len(Blog.query.all())

    return render_template("index.html", form = form )


@app.route('/comboexists')
def comboexists():
    return render_template('comboexists.html')
@app.route('/bloggers')
def bloggers():
    names = Name.query.filter_by(username=username)
    return render_template('people.html',username=username)

@app.route('/blogs')
def blogs():
    blogs = Blog.query.all()
    tickers = [(b, Ticker.query.filter_by(id=b.id).first()) for b in blogs]
    return render_template('stockinfo.html', blogs=tickers, blog = blog, tickers = tickers, final = final,final_low=final_low, name=name, username=username)

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

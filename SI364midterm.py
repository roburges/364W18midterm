###############################
####### SETUP (OVERALL) #######
###############################

## Import statements
# Import statements
import os
import sys
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, PasswordField, BooleanField, SelectMultipleField, ValidationError
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from flask_script import Shell, Manager
from wtforms.validators import Required, Length # Here, too
from flask_sqlalchemy import SQLAlchemy
import random
from flask_script import Manager, Shell
from threading import Thread
import requests # add
import json
from werkzeug import secure_filename
from pprint import pprint
from flask_migrate import Migrate, MigrateCommand
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import LoginManager, login_required, logout_user, login_user, UserMixin, current_user
## App setup code
app = Flask(__name__)
app.debug = True
app.use_reloader = True

## All app.config values
app.config['SECRET_KEY'] = 'hard to guess string'
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:Soulfood123@localhost:5432/test4" # TODO: May need to change this, Windows users -- probably by adding postgres:YOURTEXTPW@localhost instead of just localhost. Or just like you did in section or lecture before! Everyone will need to have created a db with exactly this name, though.
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


## Statements for db setup (and manager setup if using Manager)
manager = Manager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db) # For database use/updating
manager.add_command('db', MigrateCommand) # Add migrate command to manager

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.init_app(app)

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
    names_id=db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return "{blog %r} (ID: {%a})".format(self.blog, self.id)


class Ticker(db.Model):
    __tablename__ = "tickers"
    id = db.Column(db.Integer,primary_key=True)
    tickerD = db.Column(db.String(64))
    blogr=db.relationship('Blog',backref='Ticker')
    def __repr__(self):
        return "{tickerD %r} | ID: {%a})".format(self.tickerD, self.id)

# class Name(db.Model):
#     __tablename__ = "names"
#     id = db.Column(db.Integer,primary_key=True)
#     username = db.Column(db.String(64))
#     passwords_id=db.Column(db.Integer, db.ForeignKey('passwords.id'))
#
#     def __repr__(self):
#         return "{username %r} | ID: {%a})".format(self.username, self.id)

# class Password(db.Model):
#     __tablename__="passwords"
#     id=db.Column(db.Integer,primary_key=True)
#     pword=db.Column(db.String)
#     email=db.Column(db.String)
#     namer=db.relationship('Name', backref='Password')
#     def __repr__(self):
#         return "{pword %r} | ID: {%a})".format(self.pword, self.id)
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    collection = db.relationship('Blog', backref='User')
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) # returns User object or None

###################
###### FORMS ######
###################



class BlogForm(FlaskForm):

    # username = StringField('Enter your username:', validators=[Required(),Length(1,280)])
    tickers = StringField('Enter a stock you have information on:', validators=[Required(),Length(1,280)])
    date= StringField('Enter a date for a quote to display (YYYY-MM-DD, up to 18 years):', validators=[Required(),Length(10)])
    blog = StringField("Enter your information here (below 10,000 words):", validators=[Required(),Length(10,10000)])
    submit = SubmitField('Submit')
    def validate_Date(self,field):
        form = BlogForm()
        if form.tickers.data.isdigit():
            raise ValidationError("Ticker cannot contain numbers")

# class LoginForm(FlaskForm):
#     username = StringField('Enter your existing Username or create one',validators=[Required(), Length(1,20)])
#     pword = PasswordField('Enter your existing Password or create one',validators=[Required(),Length(1,25)])
#     email= StringField('Please Enter a valid email:', validators=[Required()])
#     submit = SubmitField('Log in or Create account')

class RegistrationForm(FlaskForm):
    email = StringField('Email:', validators=[Required(),Length(1,64),Email()])
    username = StringField('Username:',validators=[Required(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,'Usernames must have only letters, numbers, dots or underscores')])
    password = PasswordField('Password:',validators=[Required(),EqualTo('password2',message="Passwords must match")])
    password2 = PasswordField("Confirm Password:",validators=[Required()])
    submit = SubmitField('Register User')

    #Additional checking methods for the form
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already taken')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1,64), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')



#######################
###### VIEW FXNS ######
#######################

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


#num_blogs code from lecture
@app.route('/')
def index():
    return login()
    # return render_template('signup.html',form=form)
@app.route('/login',methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(url_for('home'))
        flash('Invalid username or password.')
    return render_template('login.html',form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('index'))

@app.route('/register',methods=["GET","POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,username=form.username.data,password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You can now log in!')
        return redirect(url_for('login'))
    return render_template('register.html',form=form)


@app.route('/home', methods=['GET', 'POST'])
def home():
    form = BlogForm(request.form)
    if form.validate_on_submit():

        tickers = form.tickers.data
        date= form.date.data
        blog = form.blog.data
        username = RegistrationForm(request.form).username.data
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
        #     def login():
        #             form=LoginForm(request.form)
        #             if form.validate_on_submit():
        #                 username=form.username.data
        #                 pword=form.pword.data
        #                 email=form.email.data
        #
        #                 n = User.query.filter_by(namer=names.username, email=email).first()
        #
        #                 if n:
        #                     print ("username and email combo exists")
        #                     redirect(url_for('comboexists'))
        #                 else:
        #                     n = User(namer=names.username,pword=pword,email=email)
        #                     db.session.add(n)
        #                     db.session.commit()
        #
        #                 n= Name.query.filter_by(namer=names.username).all()
        #
        #                 if n:
        #                     print("username exists but still usable per requirement")
        #                     n = Name(username=username)
        #                     db.session.add(n)
        #                     db.session.commit()
        #                 else:
        #                     print('adding')
        #                     db.session.add(n)
        #                     db.session.commit()
        #
        # return login()



##below code from lecture/HW3
    errors = [v for v in form.errors.values()]
    if len(errors) > 0:
        flash("!!!! ERRORS IN FORM SUBMISSION - " + str(errors))
    num_blogs = len(Blog.query.all())

    return render_template("index.html", form = form )


# @app.route('/comboexists')
# def comboexists():
#     return render_template('comboexists.html')

@app.route('/bloggers')
def bloggers():
    names = User.query.all()
    return render_template('people.html',names=names)

@app.route('/blogs')
def blogs():
    blogs = Blog.query.all()
    names=User.query.all()
    ticker=Ticker.query.all()
    return render_template('stockinfo.html', blogs=blogs, names=names, ticker=ticker)

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

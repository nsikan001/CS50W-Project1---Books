import psycopg2
import os
import re
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms import BooleanField, SubmitField
from flask_session import Session
from wtforms.validators import InputRequired, DataRequired, Length, Email, EqualTo
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, session, render_template, request, redirect, flash, url_for, jsonify
import requests
import json
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, update, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.sql import text


app = Flask(__name__)
db = SQLAlchemy(app)
ma = Marshmallow(app)


# app.secret_key = '1234567'
app.config['SECRET_KEY'] = "617617"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"


engine = create_engine("postgres://qhoznpulvoulkq:dd2bf16c2a11182c78cce25af8af860eb58e25ccf979730b39ecea73b8c68d3a@ec2-52-202-146-43.compute-1.amazonaws.com:5432/dbikuhfvh5nkml")
Base = declarative_base()


class Users(UserMixin):
    def __init__(self, id):
        self.id = id



class RegForm(FlaskForm):

    username = StringField("username_label",
                           validators=[InputRequired(message='Username is required'), Length(min=4,
                                                                                             max=24, message='Username must be within the range of 4 to 20 characters')])
    email = StringField("email_label", validators=[InputRequired(message='Email is required'), Length(min=4,
                                                                                                      max=24, message='Email must not be less than 10 characters')])
    password = PasswordField("password_label", validators=[InputRequired(message='Password is required'), Length(min=4,
                                                                                                                 max=24, message='Password must not be less than 4 characters')])
    conf_password = PasswordField("confirm_password_label", validators=[InputRequired(message='Confirm password is required'),
                                                                        EqualTo('password', message='password and confirm password fields must match')])
    submit_btn = SubmitField('Submit')


class LoginForm(FlaskForm):

    email = StringField("email_label", validators=[InputRequired(message='Email is required'), Length(min=4,
                                                                                                      max=24, message='Email must not be less than 10 characters')])
    password = PasswordField("password_label", validators=[InputRequired(message='Password is required'), Length(min=4,
                                                                                                                 max=24, message='Password must not be less than 4 characters')])
    submit_btn = SubmitField('Login')


class SearchForm(FlaskForm):

    search = StringField("search_label", validators=[
                         InputRequired(message='search field must not be empty')])


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    reg_form = RegForm()
    if reg_form.validate_on_submit():
        username = reg_form.username.data
        email = reg_form.email.data
        passw = reg_form.password.data
        password = generate_password_hash(passw, method='sha256')
        # Check if user email exists
        user_object = engine.execute(text(
            """SELECT email FROM users WHERE email = :email"""), ({"email": email},)).fetchall()
        if user_object:
            flash('Email address already exists')
            return redirect('/signup2')
        new_user = engine.execute(text("""INSERT INTO users(username, email, password) VALUES(:username, :email, :password)"""), ({
                                  "username": username, "email": email, "password": password},))

        return redirect('/login')
    return render_template('signup.html', form=reg_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if request.method == 'POST' and login_form.validate_on_submit():
        email = login_form.email.data
        password = login_form.password.data

        db_email = engine.execute(text(
            """SELECT * FROM users WHERE email = :email"""), ({"email": email},)).fetchone()
        db_password = engine.execute(text(
            """SELECT password FROM users WHERE email = :email"""), ({"email": email},)).fetchall()
        passw_decrypt = check_password_hash(db_password, password)

        if not db_email or not db_password:
            flash('Please check your login details and try again.')
            return redirect('/login')

        user_id = db_email['id']
        session['logged_in'] = True
        session['email'] = email
        user_id = db_email['id']
        session['user_id'] = user_id
        return redirect(url_for('books'))
        # return check()
    else:
        if "user_id" and "email" in session:
            redirect(url_for('books'))
        return render_template('login.html', form=login_form)


@app.route('/books', methods=['GET', 'POST'])
def books():
    if "user_id" and "email" in session:
        email = session["email"]
        books = engine.execute("SELECT * FROM books")
        return render_template('books.html', email=email, books=books)
    return redirect(url_for('login'))


@app.route("/book/details/<int:det_id>")
def details(det_id):
    book = engine.execute(text(
        """SELECT * FROM books WHERE id = :det_id LIMIT 1"""), ({"det_id": det_id},)).fetchone()
    
    review_count = engine.execute(text(
        """SELECT COUNT(*) FROM reviews WHERE book_id = :det_id"""), ({"det_id": det_id},)).fetchone()[0]
    
    book_isbn = book['isbn']
    api_key = "ffG7OyJrqQx3qWkjsTPw"
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params = {"key":api_key, "isbns":book_isbn})

    if res.status_code != 200:
        raise Exception("Error: Please try again later")
    data = res.json()
    goodreads_reviews = data["books"][0]["reviews_count"]
    goodreads_rating = data["books"][0]["average_rating"]
    
    return render_template('book.html', book=book, review_count=review_count, goodreads_reviews=goodreads_reviews, goodreads_rating=goodreads_rating)


@app.route("/book_search", methods=['GET', 'POST'])
def book_search():
    if request.method == 'POST':
        search_term = request.form['book_srch']
        # search_filter = request.form['filter']
        if search_term != '':
            search_query = engine.execute(text(
                """SELECT * FROM books WHERE isbn ILIKE :search OR author ILIKE :search OR title ILIKE :search"""), ({"search": "%"+search_term+"%"},)).fetchall()
            return render_template('search_result.html', search_query=search_query)
        return 'Incomplete search term'


@app.route("/book/write_review/<int:rev_id>")
def review(rev_id):
    session['rev_id'] = rev_id
    # return render_template('write_review.html', rev_id=rev_id)
    return redirect(url_for('write_review'))


@app.route('/write_review', methods=['POST', 'GET'])
def write_review():
    if "rev_id" and "email" in session:
        email = session["email"]
        rev_id = session["rev_id"]
        return render_template('write_review.html')


@app.route('/submit_review', methods=['POST', 'GET'])
def submit_review():
    if request.method == 'POST':
        rating = request.form['rating']
        comment = request.form['comment']
        if "rev_id" and "email" in session:
            email = session["email"]
            rev_id = session["rev_id"]
            user = engine.execute(text(
                """SELECT * FROM users WHERE email = :email"""), ({"email": email},)).fetchone()
            user_isd = user['id']

            r = engine.execute(text(
                """SELECT * FROM reviews WHERE user_id = :user_isd AND book_id = :rev_id"""), ({"user_isd": user_isd, "rev_id": rev_id},)).fetchall()

            if not r:
                
                insert_review = engine.execute(text("""INSERT INTO reviews(book_id, user_id, scale, comment) VALUES(:book_id, :user_id, :scale, :comment)"""), ({
                                  "book_id": rev_id, "user_id": user_isd, "scale": rating, "comment": comment},))
                return redirect(url_for('books'))

            flash('Sorry, review for a particular book must be submitted only once.')
            return render_template('write_review.html')
          


@app.route("/book/reviews/<int:book_isd>")
def reviews(book_isd):
    session['book_isd'] = book_isd
    revs = engine.execute(text(
                """SELECT scale, comment, title FROM reviews JOIN books ON reviews.book_id = books.id WHERE reviews.book_id = :book_isd"""), ({"book_isd": book_isd},)).fetchall()
    # return book_isd
    return render_template('reviews.html', reviews=revs)
    # return redirect(url_for('write_review'))


@app.route("/api/<string:isbns>")
def api(isbns):
    book_isbn = isbns
    book = engine.execute(text(
        """SELECT * FROM books WHERE isbn = :isbns LIMIT 1"""), ({"isbns": isbns},)).fetchone()
    
    if book:
        api_key = "ffG7OyJrqQx3qWkjsTPw"
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params = {"key":api_key, "isbns":book_isbn})
        if res.status_code != 200:
            raise Exception("Error: Please try again later")
        data = res.json()
        goodreads_reviews = data["books"][0]["reviews_count"]
        goodreads_rating = data["books"][0]["average_rating"]
    
        return jsonify({"book": book['title'],
            "title":book['author'],
            "year":book['year'].strftime("%Y"),
            "isbn":book['isbn'],
            "review_count": goodreads_reviews,
            "average_score": goodreads_rating
        })
    raise Exception("Error: ISBN not found")

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('login', None)
    session.pop('user_id', None)
    session.pop('email', None)
    return redirect('/login')

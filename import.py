import psycopg2
import os
import re
import csv
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms import BooleanField, SubmitField
from flask_session import Session
from wtforms.validators import InputRequired, DataRequired, Length, Email, EqualTo
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, session, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, update
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.sql import text

engine = create_engine("postgres://qhoznpulvoulkq:dd2bf16c2a11182c78cce25af8af860eb58e25ccf979730b39ecea73b8c68d3a@ec2-52-202-146-43.compute-1.amazonaws.com:5432/dbikuhfvh5nkml")
Base = declarative_base()


try:
    file = open("books.csv", newline='')
    reader = csv.reader(file)

    header = next(reader)
    #makes use of the next() function to extract the headings of the csv file
    print(header)
    
    for isbn, title, author, year in reader:
        rows = [isbn, title, author, year]
        # the character conversions here follows datatype on the database table
        isbn = str(rows[0])
        title = str(rows[1])
        author = str(rows[2])
        year = datetime.strptime(rows[3], '%Y')

        engine.execute(text("""INSERT INTO books(isbn, title, author, year) VALUES(:isbn, :title, :author, :year)"""), ({"isbn": isbn, "title": title, "author": author, "year": year},))
       
except:
    print('false')
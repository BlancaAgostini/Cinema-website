from time import timezone
from . import db
from flask_login import UserMixin
from datetime import datetime, time

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10000))
    image = db.Column(db.String(10000))
    genre = db.Column(db.String(150))
    duration = db.Column(db.String(150))
    shows = db.relationship('Show')

class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String(150))
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))
    cinemahall_id = db.Column(db.Integer, db.ForeignKey('cinemahall.id'))
    bookings = db.relationship('Booking')
    showseats = db.relationship('Showseat')

class Cinemahall(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hall_number = db.Column(db.Integer)
    total_seats = db.Column(db.Integer)
    hallshows = db.relationship('Show')

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    bookings = db.relationship('Booking')

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number_seats = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'))
    showseats = db.relationship('Showseat')

class Showseat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Integer)
    seat = db.Column(db.String(150))
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'))
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'))
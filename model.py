"""Models for migraine tracking app."""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """A user."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    get_period = db.Column(db.String) #if gets periods

    headache = db.relationship("Headache", back_populates="user")
    period = db.relationship("Period", back_populates="user") #if gets periods

    def __repr__(self):
        return f"<User user_id={self.user_id} email={self.email}>"

class Headache(db.Model):
    """A headache."""

    __tablename__ = "headaches"

    headache_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    date_start = db.Column(db.DateTime)
    date_end = db.Column(db.DateTime)
    pain_scale = db.Column(db.Integer)
    headache_type = db.Column(db.String)
    additional_notes = db.Column(db.Text)

    user = db.relationship("User", back_populates="headache")
    triggers = db.relationship("Trigger", back_populates="headache")
    medication = db.relationship("Medication", back_populates="headache")

    def __repr__(self):
        return f"<Headache headache_id={self.headache_id} type={self.headache_type}>"


class Trigger(db.Model):
    """A trigger."""

    __tablename__ = "triggers"

    trigger_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    headache_id = db.Column(db.Integer, db.ForeignKey("headaches.headache_id"))
    trigger_name = db.Column(db.String)
    additional_notes = db.Column(db.Text)
    

    headache = db.relationship("Headache", back_populates="triggers")

    def __repr__(self):
        return f"<Trigger trigger_id={self.trigger_id} trigger_name={self.trigger_name}>"

class Period(db.Model):
    """A period cycle for users who menstruate.""" 

    __tablename__ = "periods"

    period_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    date_start = db.Column(db.DateTime)
    date_end = db.Column(db.DateTime)


    user = db.relationship("User", back_populates="period")

    def __repr__(self):
        return f"<Period period_id={self.period_id} start_date={self.date_start}>"


class Medication(db.Model):
    """A medication""" 

    __tablename__ = "medications"

    medication_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    headache_id = db.Column(db.Integer, db.ForeignKey("headaches.headache_id"))
    med_name = db.Column(db.String)
    efficacy = db.Column(db.String)
    
    headache = db.relationship("Headache", back_populates="medication")

    def __repr__(self):
        return f"<Medication medication_id={self.medication_id} med_name={self.med_name}>"



def connect_to_db(flask_app, db_uri="postgresql:///headaches", echo=True):
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    flask_app.config["SQLALCHEMY_ECHO"] = echo
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.app = flask_app
    db.init_app(flask_app)

    print("Connected to the db!")


if __name__ == "__main__":
    from server import app

    # Call connect_to_db(app, echo=False) if your program output gets
    # too annoying; this will tell SQLAlchemy not to print out every
    # query it executes.

    connect_to_db(app, echo=False)

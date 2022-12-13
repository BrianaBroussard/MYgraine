
"""Server for movie ratings app."""

from flask import (Flask, render_template, request, flash, session,
                   redirect)
from model import connect_to_db, db
import crud
from constants import headache_type

from jinja2 import StrictUndefined

app = Flask(__name__)

app.secret_key = "dev"
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def homepage():
    """View homepage"""
    return render_template('homepage.html')


@app.route("/login", methods=["POST"])
def process_login():
    """Process user login."""

    email = request.form.get("email")
    password = request.form.get("password")

    user = crud.get_user_by_email(email)
    if not user or user.password != password:
        flash("The email or password you entered was incorrect.")
    else:
        # Log in user by storing the user's email in session
        session["user_email"] = user.email
        flash(f"Welcome back, {user.email}!")
        return render_template('/userprofile.html', user = user, headache_type = headache_type)

    return redirect("/")


@app.route("/users", methods=["POST"])
def register_user():
    """Create a new user."""

    email = request.form.get("email")
    password = request.form.get("password")

    user = crud.get_user_by_email(email)
    if user:
        flash("Cannot create an account with that email. Try again.")
    else:
        user = crud.create_user(email, password)
        db.session.add(user)
        db.session.commit()
        flash("Account created! Please log in.")

    return redirect("/")


@app.route("/log-headache", methods=["POST"])
def log_headache():
    """Create and log a new headache."""
    logged_in_email = session.get("user_email")

    user = crud.get_user_by_email(logged_in_email)
    date_start = request.form.get('date-start')
    pain_scale = request.form.get('pain-scale')
    headache_type = request.form.get('headache-type')

    date_end = request.form.get('date-end')
    additional_notes = request.form.get('')

    headache = crud.create_headache(date_start, int(pain_scale), headache_type, user)

    db.session.add(headache)
    db.session.commit()

    flash(f"headache logged")

    return render_template("headaches.html", user = user)


if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)

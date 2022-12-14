
"""Server for movie ratings app."""

from flask import (Flask, render_template, request, flash, session,
                   redirect)
from model import connect_to_db, db
import crud
from constants import headache_type, trigger_names

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
        return render_template('user_profile.html', user = user)
        

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

        #instantiate constant triggers for new user
        for trigger in trigger_names:
            trigger_count = 0
            user = user
            trigger_name = trigger
            const_trigger = crud.create_trigger(user,
                                  trigger_name,
                                  trigger_count,
                                  )
            db.session.add(const_trigger)
            db.session.commit()                          
        

    return redirect("/")

@app.route("/go-to-headache-log")
def see_headache_log():
    """button route to render headache log form"""
    
    logged_in_email = session.get("user_email")
    user = crud.get_user_by_email(logged_in_email)

    return render_template('/log_headache.html', user = user, headache_type = headache_type)

@app.route("/log-headache", methods=["POST"])
def log_headache():
    """Create and log a new headache."""
    logged_in_email = session.get("user_email")

    user = crud.get_user_by_email(logged_in_email)
    date_start = request.form.get('date-start')
    pain_scale = request.form.get('pain-scale')
    headache_type = request.form.get('headache-type')    
    additional_notes = request.form.get('notes')
    
    date_ended = request.form.get('date-end')
    if date_ended:
        date_end = date_ended
    else:
        date_end = date_start

    headache = crud.create_headache(date_start,
                                    int(pain_scale),
                                    headache_type, 
                                    user,
                                    date_end, 
                                    additional_notes)

    db.session.add(headache)
    db.session.commit()

    flash(f"headache successfully logged")

    return render_template("log_trigger.html", user = user)


@app.route("/log-trigger",methods=["POST"])
def log_trigger():
    """Log trigger by incrementing count"""

    logged_in_email = session.get("user_email")
    user = crud.get_user_by_email(logged_in_email)

    triggers = request.form.getlist('triggers') #returns list of checked trigger_ids
    
    for trigger_id in triggers:
        crud.update_trigger(trigger_id)
       
    db.session.commit()       
    
    flash(f"trigger successfully logged")
    return render_template("user_profile.html", user = user)



@app.route("/add-trigger", methods=["POST","GET"])
def add_trigger():
    """Create new trigger"""

    logged_in_email = session.get("user_email")
    user = crud.get_user_by_email(logged_in_email)

    new_trigger = request.form.get('add-trigger') 
    trigger_count = 0
    
    trigger = crud.create_trigger(user,
                        new_trigger,
                        trigger_count
                        )
    db.session.add(trigger)
    db.session.commit()       
    
    flash(f"trigger successfully added")
    return render_template("log_trigger.html", user = user)



if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)

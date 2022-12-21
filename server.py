
"""Server for movie ratings app."""

from flask import (Flask, render_template, request, flash, session,
                   redirect, jsonify)
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
    #if session.get("user_email"):
    #    return redirect(("/user_dashboard"))

    return render_template('index.html')


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

        return redirect("/user_dashboard")
        

    return redirect("/")


@app.route("/user_dashboard")
def show_user_dashboard():
    """Show user's their dashboard"""
    
    logged_in_email = session.get("user_email")
    user = crud.get_user_by_email(logged_in_email)

    dict_users_triggers = crud.get_users_triggers_with_count(user.user_id)

    return render_template("user_profile.html", user = user, dict_users_triggers = dict_users_triggers )

@app.route("/sign-up")
def show_sign_up_form():
    """take use to sign-up form"""
    return render_template("create_account.html")


@app.route("/users", methods=["POST"])
def register_user():
    """Create a new user."""

    email = request.form.get("email")
    name = request.form.get("name").capitalize()
    password = request.form.get("password")
    phone = "+1" + request.form.get("phone_number")

    user = crud.get_user_by_email(email)
    if user:
        flash("That email already belongs to an account. Please log in.")
        return redirect("/")

    else:
        user = crud.create_user(email, password, name, phone)
        db.session.add(user)
        db.session.commit()
        flash("Account created! Lets get some more info.")
        session["user_email"] = user.email #may take this out if rearrange registration

    triggers = crud.show_all_default_triggers()
                
    return render_template("create_triggers.html", user = user, triggers = triggers)


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

    users_triggers = crud.get_users_triggers(user.user_id)


    return render_template("log_trigger.html", user = user, users_triggers = users_triggers)


@app.route("/make-users-triggers",methods=["POST"])
def make_users_default_triggers():
    """Instantiate UserTrigger for user with the preset triggers"""

    logged_in_email = session.get("user_email")
    user = crud.get_user_by_email(logged_in_email)
    user_id = user.user_id  

    triggers = request.form.getlist('default-triggers')     #returns list of checked trigger_ids

    for trigger_id in triggers:
        crud.add_trigger_for_user(user_id, trigger_id)
       
    
    return redirect("/user_dashboard")



@app.route("/log-trigger",methods=["POST"])
def log_trigger():
    """Log trigger by incrementing count"""

    logged_in_email = session.get("user_email")
    user = crud.get_user_by_email(logged_in_email)


    triggers = request.form.getlist('triggers') #returns list of checked trigger_ids
    
    for trigger_id in triggers:
        crud.update_trigger_count(user.user_id, trigger_id)
       
    db.session.commit()       
    
    flash(f"trigger successfully logged")


    return redirect("/user_dashboard")



@app.route("/add-trigger", methods=["POST","GET"])
def add_trigger():
    """Create new trigger for the user"""

    logged_in_email = session.get("user_email")
    user = crud.get_user_by_email(logged_in_email)

    add_trigger = request.form.get('add-trigger').capitalize()

    new_trigger = crud.check_trigger_db(add_trigger) #check in db for trigger name
    
   
    if new_trigger == None:
        trigger = crud.create_trigger(add_trigger)
        db.session.add(trigger)
        db.session.commit()
    
        crud.add_trigger_for_user(user.user_id, trigger.trigger_id)
        db.session.commit()   
        flash(f"Trigger successfully added") 
    else:
        if crud.check_users_triggers(user.user_id, new_trigger.trigger_id) == None:
            crud.add_trigger_for_user(user.user_id, new_trigger.trigger_id)
            flash(f"Trigger successfully added")
        else:
            flash(f"This trigger is already listed")           
    
    

    users_triggers = crud.get_users_triggers(user.user_id)


    return render_template("log_trigger.html", user = user, users_triggers = users_triggers)
    #there is a bug in this where first time added trigger duplicates
    #might use below if use AJAX call instead 
    #update_trigger_list = {'trigger_name': trigger.trigger_name, 'trigger_id': trigger.trigger_id}

    #could return JSON string instead to JS file and reload DOM instead of reloading 


@app.route('/users-triggers.json')
def get_users_triggers_and_count():
    """Get the user's current triggers and count"""

    logged_in_email = session.get("user_email")
    user = crud.get_user_by_email(logged_in_email)
    
    users_trigger_count_dic = crud.get_users_triggers_with_count(user.user_id)
    trigger_chart_list = []


    for trigger, count in users_trigger_count_dic.items():
        trigger_chart_list.append({'trigger': trigger, 'count':count})
    
    
    
    return jsonify({'data': trigger_chart_list})



    

if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)

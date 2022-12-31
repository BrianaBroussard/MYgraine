
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
    if session.get("user_email"):
        return redirect(("/user_dashboard"))

    return render_template('index.html')


@app.route("/login", methods=["GET", "POST"])
def process_login():
    """View login page and process user login."""
    
    if request.method == 'POST':
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
        

    return render_template("login.html")


@app.route("/logout")
def process_logout():
    """Log user out and clear the session."""

    del session["user_email"]
    return redirect("/")    


@app.route("/user_dashboard")
def show_user_dashboard():
    """Show user's their dashboard"""
    
    logged_in_email = session.get("user_email")
    user = crud.get_user_by_email(logged_in_email)

    dict_users_triggers = crud.get_users_triggers_with_count(user.user_id)
    users_triggers = crud.get_users_triggers(user.user_id)

    return render_template("user_profile.html", 
                            user = user, 
                            dict_users_triggers = dict_users_triggers,
                             headache_type = headache_type,
                             users_triggers = users_triggers )

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
    period = request.form.get("period")
    if period == 'True':
        get_period = True
    else:
        get_period = False

    user = crud.get_user_by_email(email)
    if user:
        flash("That email already belongs to an account. Please log in.")
        return redirect("/")

    else:
        user = crud.create_user(email, password, name, phone, get_period)
        db.session.add(user)
        db.session.commit()
        flash("Account created! Lets get some more info.")
        session["user_email"] = user.email #may take this out if rearrange registration

    triggers = crud.show_all_default_triggers()
                
    return render_template("create_triggers.html", user = user, triggers = triggers)


#@app.route("/go-to-headache-log")
#def see_headache_log():
    """button route to render headache log form""" #replaced with modal
    
#    logged_in_email = session.get("user_email")
#    user = crud.get_user_by_email(logged_in_email)
#    users_triggers = crud.get_users_triggers(user.user_id)

#    return render_template('log_headache.html', 
#                            user = user, 
#                            headache_type = headache_type, 
#                            users_triggers = users_triggers)


@app.route("/log-headache", methods=["POST"])
def log_headache():
    """Create and log a new headache."""
    logged_in_email = session.get("user_email")

    user = crud.get_user_by_email(logged_in_email)
    date_start = request.form.get('date-start')
    
    pain_scale = request.form.get('pain-scale')
    headache_type = request.form.get('headache-type')    
    additional_notes = request.form.get('notes')

    #if user gets periods
    period = request.form.get('period')
    period_start = request.form.get('period-start')
    
    if period == "True":
        on_period = True
    else:
        on_period = False

    date_ended = request.form.get('date-end')
    if date_ended:
        date_end = date_ended
    else:
        date_end = date_start

    time_start = request.form.get('time-start')
    if time_start:
        date_start = date_start + " " + time_start


    headache = crud.create_headache(date_start,
                                    int(pain_scale),
                                    headache_type, 
                                    user,
                                    date_end, 
                                    additional_notes,
                                    on_period)

    db.session.add(headache)
    db.session.commit()


    if period_start:
        new_period = crud.create_period(user.user_id, period_start)
        db.session.add(new_period)
        db.session.commit()


    headache_id = headache.headache_id

    triggers = request.form.getlist('triggers') #returns list of checked trigger_ids
    
    for trigger_id in triggers:
        crud.update_trigger_count(user.user_id, trigger_id)
        crud.create_headache_trigger(headache_id, trigger_id)
       
    db.session.commit()       
    
    flash(f"headache successfully logged")


    return redirect("/user_dashboard")

   


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




@app.route("/add-trigger.json", methods=["POST"])
def add_trigger():
    """Create new trigger for the user"""

    logged_in_email = session.get("user_email")
    user = crud.get_user_by_email(logged_in_email)

    add_trigger = request.json.get("trigger").capitalize()

    new_trigger = crud.check_trigger_db(add_trigger) #check in db for trigger name
    
   
    if new_trigger == None:
        trigger = crud.create_trigger(add_trigger)
        db.session.add(trigger)
        db.session.commit()

        trigger_name = trigger.trigger_name
        trigger_id = trigger.trigger_id
    
        crud.add_trigger_for_user(user.user_id, trigger.trigger_id)
        db.session.commit()   
        status = "Trigger successfully added" 
    else:
        if crud.check_users_triggers(user.user_id, new_trigger.trigger_id) == None:
            crud.add_trigger_for_user(user.user_id, new_trigger.trigger_id)
            trigger_name = new_trigger.trigger_name
            trigger_id = new_trigger.trigger_id
            status = "Trigger successfully added"
        else:
            status = "Error"
            trigger_name = new_trigger.trigger_name
            trigger_id = new_trigger.trigger_id           
    
    return jsonify({'trigger_name': trigger_name, 'trigger_id': trigger_id, "status": status})



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


@app.route("/headache/<headache_id>")
def show_headache(headache_id):
    """show user's headache details"""

    headache = crud.get_headache_by_id(headache_id)
    user = headache.user
    triggers = crud.get_triggers_for_headache(headache_id)
    trigger_names = []

    for trigger in triggers:
        trigger_names.append(trigger.trigger_name)

    users_triggers = crud.get_users_triggers(user.user_id)
    return render_template("headache_details.html",
                             headache = headache, 
                             user=user, 
                             triggers = trigger_names,
                             headache_type = headache_type,
                             users_triggers = users_triggers)
    

if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)

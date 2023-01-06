
"""Server for movie ratings app."""

from flask import (Flask, render_template, request, flash, session,
                   redirect, jsonify)
from model import connect_to_db, db, Trigger
import crud
from constants import headache_type
from statistics import mode 
from datetime import datetime
import humanize


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

    users_triggers = crud.get_users_triggers(user.user_id)

    # headache summery logic
    number_of_headaches = len(user.headaches)
    
    pain_lst = []
    HA_type_lst = []
    HA_dates = []
    
    #for users with periods
    HA_on_period = []

    for headache in user.headaches:
        HA_type_lst.append(headache.headache_type)
        HA_dates.append(headache.date_end)
        if headache.pain_scale > 0:
            pain_lst.append(headache.pain_scale)
        if headache.on_period:
            HA_on_period.append(headache)

    if len(pain_lst) > 0:
        avg_pain = (round(sum(pain_lst)/len(pain_lst), 2))
        max_pain = max(pain_lst)
    else:
        avg_pain = None
        max_pain = None    
    if len(HA_type_lst) > 0:    
        most_common_type = mode(HA_type_lst)
    else:
        most_common_type = None


    #for users with periods
    if len(HA_on_period) > 0:
        percent_on_period = (round((len(HA_on_period)/len(user.headaches)) * 100,2))
    else:
        percent_on_period = None

    # datetime object containing current date and time
    now = datetime.now()
    if number_of_headaches > 0: 
        most_recent_HA = max(HA_dates)
        time_since_most_recent = humanize.precisedelta((now - most_recent_HA),minimum_unit="minutes",format="%0.0f")
    else:
        most_recent_HA = None
        time_since_most_recent = None

    #top three user's triggers
    dict_users_triggers = crud.get_users_triggers_with_count(user.user_id)

    if len(dict_users_triggers) >= 3:
        top_triggers = crud.most_common_triggers(dict_users_triggers,3)
    elif len(dict_users_triggers) < 3:
        top_triggers = dict_users_triggers
        if len(dict_users_triggers) == 0:
            top_triggers = None
    else:
        top_triggers = None
    
     
    return render_template("user_profile.html", 
                            user = user, 
                            dict_users_triggers = dict_users_triggers,
                            top_triggers = top_triggers,
                            headache_type = headache_type,
                            users_triggers = users_triggers,
                            number_of_headaches = number_of_headaches,
                            avg_pain = avg_pain,
                            max_pain = max_pain,
                            most_common_type = most_common_type,
                            percent_on_period = percent_on_period,
                            time_since_most_recent = time_since_most_recent
                             )


@app.route("/user_calendar")
def show_user_calendar():
    """route to render user's calendar"""

    logged_in_email = session.get("user_email")
    user = crud.get_user_by_email(logged_in_email)
    users_triggers = crud.get_users_triggers(user.user_id)

    return render_template("user_calendar.html", 
                            user = user,
                            users_triggers = users_triggers, 
                            headache_type = headache_type
                            )

@app.route("/user_charts")
def show_user_charts():
    """route to render user's charts"""

    logged_in_email = session.get("user_email")
    user = crud.get_user_by_email(logged_in_email)
    users_triggers = crud.get_users_triggers(user.user_id)
    dict_users_triggers = crud.get_users_triggers_with_count(user.user_id)

    return render_template("user_charts.html", 
                            user = user,
                            users_triggers = users_triggers, 
                            headache_type = headache_type,
                            dict_users_triggers = dict_users_triggers
                            )


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
    wants_notifications = request.form.get("notifications")

    if wants_notifications == "True":
        scheduled_reminder = request.form.get("scheduled-reminder")
    else:
        scheduled_reminder = None

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
        user = crud.create_user(email, password, name, phone, scheduled_reminder, get_period)
        db.session.add(user)
        db.session.commit()
        flash("Account created! Lets get some more info.")
        session["user_email"] = user.email #may take this out if rearrange registration

    triggers = crud.show_all_default_triggers()
                
    return render_template("create_triggers.html",
                            user = user, 
                            triggers = triggers,
                            headache_type = headache_type)


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
        trigger_icon = trigger.icon 

        crud.add_trigger_for_user(user.user_id, trigger.trigger_id)
        db.session.commit()  
        
        status = "Trigger successfully added" 
    else:
        if crud.check_users_triggers(user.user_id, new_trigger.trigger_id) == None:
            crud.add_trigger_for_user(user.user_id, new_trigger.trigger_id)
            trigger_name = new_trigger.trigger_name
            trigger_id = new_trigger.trigger_id
            trigger_icon = new_trigger.icon
            status = "Trigger successfully added"
        else:
            status = "Error"
            trigger_name = new_trigger.trigger_name
            trigger_id = new_trigger.trigger_id 
            trigger_icon = new_trigger.icon          
    
    
    return jsonify({'trigger_name': trigger_name, 'trigger_id': trigger_id, 'trigger_icon': trigger_icon, 'status': status})



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


@app.route("/delete-headache/<headache_id>")
def delete_headache(headache_id):
    """button to delete headache""" 
    
    headache = crud.get_headache_by_id(headache_id)
    db.session.delete(headache)
    db.session.commit()
    flash("Headache Deleted")

    return redirect("/user_dashboard")

@app.route('/search-triggers.json', methods=['POST'])
def search():
    """Searches for triggers in autocomplete"""
    term = request.form['q']
    
    print ('term: ', term)
    
    all_triggers = []
    triggers = Trigger.query.all()
    filtered_search = []
  
    for trigger in triggers:
        all_triggers.append(trigger.trigger_name)
    
    for trigger in all_triggers:
        if trigger.lower().startswith(term.lower()[0]) and term.lower() in trigger.lower():
            filtered_search.append(trigger)

   
    resp = jsonify(filtered_search)
    resp.status_code = 200
    return resp

     

   


if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)


"""Server for movie ratings app."""

from flask import (Flask, render_template, request, flash, session,
                   redirect, jsonify)
from model import connect_to_db, db, Trigger, UserTrigger
import crud
from constants import headache_type
from statistics import mode 
from datetime import datetime, timedelta
import humanize
from passlib.hash import argon2
from jinja2 import StrictUndefined
import re
#below is all for google oauth
import os
import pathlib
import requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests


app = Flask(__name__)
app.secret_key = "dev"
app.jinja_env.undefined = StrictUndefined

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  #this is to set our environment to https because OAuth 2.0 only supports https environments
GOOGLE_CLIENT_ID = os.environ.get('google_client_id',None)
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")  #set the path to where the .json file you got Google console is
SCOPES = ["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"]



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


        if not user:
            flash("The email you entered was incorrect.")
            return render_template("login.html")
        elif not argon2.verify(password, user.password):   #returns True if entered password is correct 
            flash("The password you entered was incorrect.")
            return render_template("login.html")
        else:
            # Log in user by storing the user's email in session
            session["user_email"] = user.email
            flash(f"Welcome back, {user.name}!")

            return redirect("/user_dashboard")
        

    return render_template("login.html")


@app.route("/logout")
def process_logout():
    """Log user out and clear the session."""

    del session["user_email"]
    return redirect("/")    


@app.route("/create-account-with-Google") 
def create_account_google():
    """ the page where the user can login to Google """ 
    flow = Flow.from_client_secrets_file(  #Flow is OAuth 2.0 a class that stores all the information on how we want to authorize our users
    client_secrets_file=client_secrets_file,
    scopes= SCOPES,  #here we are specifing what do we get after the authorization
    redirect_uri="http://localhost:5000/google-create-account"  #and the redirect URI is the point where the user will end up after the authorization
)
    authorization_url, state = flow.authorization_url()  #asking the flow class for the authorization (login) url
    session["state"] = state
    return redirect(authorization_url)


@app.route("/google-create-account")  
def callback_create_account():
    """this is the page that will handle the callback process meaning process after the authorization"""
    flow = Flow.from_client_secrets_file(  #Flow is OAuth 2.0 a class that stores all the information on how we want to authorize our users
    client_secrets_file=client_secrets_file,
    scopes= SCOPES,  #here we are specifing what do we get after the authorization
    redirect_uri="http://localhost:5000/google-create-account"  #and the redirect URI is the point where the user will end up after the authorization
)
    flow.fetch_token(authorization_response=request.url)
    
    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    
    google_email = id_info.get("email")
    google_name = id_info.get("given_name")
    google_password = id_info.get("sub")
    triggers = crud.show_all_default_triggers()
    flash(f'OK {google_name}, lets get a litte more info before creating your account')

    return render_template("/create_account.html", 
                            triggers = triggers, 
                            google_name = google_name, 
                            google_email = google_email,
                            google_password = google_password)  



@app.route("/Login-with-Google")  
def login_with_google():
    """the page where the user can login to Google """
    flow = Flow.from_client_secrets_file(  #Flow is OAuth 2.0 a class that stores all the information on how we want to authorize our users
    client_secrets_file=client_secrets_file,
    scopes= SCOPES,  #here we are specifing what do we get after the authorization
    redirect_uri="http://localhost:5000/google-login"  #and the redirect URI is the point where the user will end up after the authorization
)
    authorization_url, state = flow.authorization_url()  #asking the flow class for the authorization (login) url
    session["state"] = state
    return redirect(authorization_url)


@app.route("/google-login") 
def callback_login():
    """this is the page that will handle the callback process meaning process after the authorization"""
    flow = Flow.from_client_secrets_file(  #Flow is OAuth 2.0 a class that stores all the information on how we want to authorize our users
    client_secrets_file=client_secrets_file,
    scopes= SCOPES,  #here we are specifing what do we get after the authorization
    redirect_uri="http://localhost:5000/google-login"  #and the redirect URI is the point where the user will end up after the authorization
)
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )
    
    
    email = id_info.get("email")
    password = id_info.get("sub")
    user = crud.get_user_by_email(email)


    if not user:
        flash("The email you entered was incorrect.")
        return render_template("login.html")
    elif not argon2.verify(password, user.password):   #returns True if entered password is correct 
        flash("The password you entered was incorrect.")
        return render_template("login.html")
    else:
        # Log in user by storing the user's email in session
        session["user_email"] = user.email
        flash(f"Welcome back, {user.name}!")

        return redirect("/user_dashboard")


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
    
    default_meds = crud.show_all_default_meds()


     
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
                            time_since_most_recent = time_since_most_recent,
                            default_meds = default_meds,
                            )


@app.route("/user_calendar")
def show_user_calendar():
    """route to render user's calendar"""

    logged_in_email = session.get("user_email")
    user = crud.get_user_by_email(logged_in_email)
    users_triggers = crud.get_users_triggers(user.user_id)
    default_meds = crud.show_all_default_meds()

    return render_template("user_calendar.html", 
                            user = user,
                            users_triggers = users_triggers, 
                            headache_type = headache_type,
                            default_meds = default_meds,
                            )

@app.route("/user_charts")
def show_user_charts():
    """route to render user's charts"""

    logged_in_email = session.get("user_email")
    user = crud.get_user_by_email(logged_in_email)
    users_triggers = crud.get_users_triggers(user.user_id)
    dict_users_triggers = crud.get_users_triggers_with_count(user.user_id)
    default_meds = crud.show_all_default_meds()

    return render_template("user_charts.html", 
                            user = user,
                            users_triggers = users_triggers, 
                            headache_type = headache_type,
                            dict_users_triggers = dict_users_triggers,
                            default_meds = default_meds,
                            )


@app.route("/sign-up")
def show_sign_up_form():
    """take use to sign-up form"""

    triggers = crud.show_all_default_triggers()
    
    return render_template("create_account.html",
                            triggers = triggers,
                            google_email = None)


@app.route("/users", methods=["POST"])
def register_user():
    """Create a new user."""

    email = request.form.get("email")
    name = request.form.get("name").capitalize()
    password = request.form.get("password")
    hashed_pw= argon2.hash(password)
    phone = request.form.get("phone_number")
    formatted_phone = "+1" + re.sub(r'^(?:\(\+\d+\))|\D', '', phone)
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
        user = crud.create_user(email, hashed_pw, name, formatted_phone, scheduled_reminder, get_period)
        db.session.add(user)
        db.session.commit()
        flash("Account created! Log your first headache now!")
        session["user_email"] = user.email 
    
    user_id = user.user_id  

    triggers = request.form.getlist('default-triggers')     #returns list of checked trigger_ids

    for trigger_id in triggers:
        crud.add_trigger_for_user(user_id, trigger_id)
    
    return redirect("/user_dashboard")



@app.route("/log-headache", methods=["POST"])
def log_headache():
    """Create and log a new headache."""
    logged_in_email = session.get("user_email")

    user = crud.get_user_by_email(logged_in_email)
            
    date_start = request.form.get('date-start')
    time_start = request.form.get('time-start')
    
    
    date_start = date_start + " " + time_start

    
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

    meds = request.form.getlist("meds")  #returns a list of checked medications med_ids
   
    for med_id in meds:
        efficacy = request.form.get(f"efficacy-{med_id}")
        dosage = request.form.get(f"dose-{med_id}")
        if dosage:
            dose = dosage
        else:
            dose = 1
        headache_med = crud.create_headache_med(headache_id, med_id, dose, efficacy)


    flash(f"Headache successfully logged!")

    if request.form.get('user-route') == "from-calendar":
        return redirect("/user_calendar")

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

    meds_lst = crud.get_meds_for_headache(headache_id)
    
    
    if headache.date_end == headache.date_start:
        HA_length = None
    else:
        HA_length = humanize.precisedelta((headache.date_end - headache.date_start),minimum_unit="minutes",format="%0.0f")
 

    default_meds = crud.show_all_default_meds()
    users_triggers = crud.get_users_triggers(user.user_id)

    return render_template("headache_details.html",
                             headache = headache, 
                             user=user, 
                             triggers = trigger_names,
                             headache_type = headache_type,
                             HA_length = HA_length,
                             users_triggers = users_triggers,
                             meds_lst = meds_lst,
                             default_meds = default_meds,
                             )


@app.route("/delete-headache/<headache_id>")
def delete_headache(headache_id):
    """button to delete headache""" 
    
    headache = crud.get_headache_by_id(headache_id)
    user_id = headache.user.user_id
    
    
    headache_meds = headache.headache_meds
    for headache_med in headache_meds:
        db.session.delete(headache_med)

    headache_triggers = headache.headache_trigger
    for headache_trigger in headache_triggers:
        trigger_id = headache_trigger.trigger_id
        updated_trigger = UserTrigger.query.filter(UserTrigger.user_id == user_id, 
                          UserTrigger.trigger_id ==trigger_id).first()

        updated_trigger.trigger_count -= 1
        db.session.delete(headache_trigger)

    db.session.delete(headache)
    db.session.commit()
    flash("Headache Deleted")

    return redirect("/user_calendar")


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


@app.route("/api/quotes")
def get_quotes():
    """Return random inspo quote from API call."""

    url = 'https://api.goprogram.ai/inspiration'
    headers = {'content-type': 'application/json'}
    res_obj = requests.get(url, headers=headers)
    quotes = res_obj.json()

    return jsonify(quotes)



@app.route("/edit-account", methods=["GET", "POST"])
def edit_account():
    """Shows Edit Account Page and Allows Users to Edit Notifications"""

    logged_in_email = session.get("user_email")
    user = crud.get_user_by_email(logged_in_email)
    phonevalue = user.phone_number[2:]
    
    if request.method == 'POST':
        phone = request.form.get("phone_number")
        formatted_phone = "+1" + re.sub(r'^(?:\(\+\d+\))|\D', '', phone)
        user.phone_number = formatted_phone
        wants_notifications = request.form.get("notifications")

        if wants_notifications == "True":
            scheduled_reminder = request.form.get("scheduled-reminder")
            user.scheduled_reminder = scheduled_reminder
        else:
            if user.scheduled_reminder:
                user.scheduled_reminder = None
            

        db.session.commit()
        flash("Account Updated")
        return redirect("/edit-account")

    default_meds = crud.show_all_default_meds()
    users_triggers = crud.get_users_triggers(user.user_id)
            
        

    return render_template("edit_account.html",                            
                            user = user,
                            users_triggers = users_triggers, 
                            headache_type = headache_type,
                            default_meds = default_meds,
                            phonevalue = phonevalue
                            )




if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)

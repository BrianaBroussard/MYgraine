
from twilio.rest import Client
import os
from datetime import datetime, date, timedelta
from server import app
from model import db, connect_to_db, User


account_sid = os.environ['account_sid']
auth_token = os.environ['auth_token']

twilio_number = os.environ['twilio_number']



with app.app_context():
    connect_to_db(app)
    
   #Returns list of tuples with all user's name and phone number
     
    users_phone_scheduled_reminder = []
    query = User.query.filter(User.phone_number == "+19498387000", User.user_id == 9).all() #test query change id for test user prn 
    # query = User.query.all()
    
    
    for user in query:
        if user.phone_number and user.scheduled_reminder:
            users_phone_scheduled_reminder.append((user.name, user.phone_number, user.scheduled_reminder))
    
   
    for users in users_phone_scheduled_reminder: 
        

        client = Client(account_sid, auth_token)
        #time needs to be + timedelta(minutes=61) from time program is run 
        #running program at midnight with cronjob 
        #and did not allow users to schedule between 12:00am and 1:01 to get around this 
        
        send_when = date.today().isoformat() + "T" + users[2].isoformat() + "-08:00" #formats time and adjusts for local timezone with -08:00 
        
        
   
        message_service_sid = os.environ['message_service_sid']

        message = client.messages.create(
                from_= message_service_sid,
                to=users[1],
                body=f'Hi {users[0]}, did you have a headache today. You should log it in MYgraine!',
                schedule_type='fixed',
                send_at=send_when,
            )

        print(message.sid)






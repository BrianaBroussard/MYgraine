from twilio.rest import Client
import os
from crud import get_users_phone
from server import app
from model import db, connect_to_db


account_sid = os.environ['account_sid']
auth_token = os.environ['auth_token']
twilio_number = os.environ['twilio_number']


with app.app_context():
    connect_to_db(app)
    for phone in get_users_phone():
        

        client = Client(account_sid, auth_token)

        message = client.messages \
            .create(
                body='Did you have a headache today. You should log it in MYgraine!',
                from_=twilio_number,
                to=phone
            )

        print(message.sid)






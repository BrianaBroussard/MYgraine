"""Script to seed database."""

import os
import json
from random import choice, randint
from datetime import datetime
from constants import trigger_names

import crud
import model
import server

os.system("dropdb headaches")
os.system('createdb headaches')

model.connect_to_db(server.app)
model.db.create_all()

#create preset triggers
for trigger in trigger_names:
    const_trigger = crud.create_trigger(trigger, is_default = True )
                                  
    model.db.session.add(const_trigger)
model.db.session.commit()




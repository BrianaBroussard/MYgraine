"""Script to seed database."""

import os
from constants import trigger_names, medications

import crud
import model
import server

os.system("dropdb headaches")
os.system('createdb headaches')

model.connect_to_db(server.app)
model.db.create_all()

#create preset triggers
for trigger in trigger_names:
    const_trigger = crud.create_trigger(trigger[0], trigger[1], is_default = True )
                                  
    model.db.session.add(const_trigger)
model.db.session.commit()

#create preset medications
for med in medications:
    const_med = crud.create_medications(med[0], med[1], med[2], is_default = True)
    model.db.session.add(const_med)
model.db.session.commit()


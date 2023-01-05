"""Script to seed database."""

import os
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
    const_trigger = crud.create_trigger(trigger[0], trigger[1], is_default = True )
                                  
    model.db.session.add(const_trigger)
model.db.session.commit()




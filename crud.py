"""CRUD operations."""

from model import db, User, Headache, Trigger, Medication, Period, UserTrigger, connect_to_db

def create_user(email, password, name, phone_number):
    """Create and return a new user."""

    user = User(email=email, password=password, name=name, phone_number=phone_number)

    return user

def create_headache(date_start, pain_scale, headache_type, user, date_end, additional_notes=" "):
    """Create and return a new headache."""

    headache = Headache(date_start=date_start, 
                  pain_scale=pain_scale, 
                  headache_type=headache_type,
                  user = user,
                  date_end = date_end,
                  additional_notes = additional_notes,
                )

    return headache

def get_headache_by_id(headache_id):
    """return headache by id"""
    
    return Headache.query.get(headache_id)
    

def create_trigger(trigger_name, is_default = False):
    """Create and return a new trigger"""

    trigger = Trigger(trigger_name=trigger_name, is_default = is_default)
                      
    return trigger

def add_trigger_for_user(user_id, trigger_id):
    """add trigger to user profile"""

    user_trigger = UserTrigger(user_id=user_id,
                               trigger_id=trigger_id,
                               )
    
    db.session.add(user_trigger)
    db.session.commit() 


def update_trigger_count(user_id, trigger_id):
    """ Update a trigger given trigger_name and the updated count. """
    
    updated_trigger = UserTrigger.query.filter(UserTrigger.user_id == user_id, 
                                               UserTrigger.trigger_id ==trigger_id).first()

    updated_trigger.trigger_count += 1
    db.session.commit()
  


def get_user_by_email(email):
    """Verifies if a user email exists"""
    return User.query.filter(User.email == email).first()


def get_user_id(user):
    """get user_id by user"""
    user_id = user.user_id

    return user_id

def show_all_default_triggers():
    """queries and displays all seeded triggers"""

    default_triggers = Trigger.query.filter(Trigger.is_default == True).all()

    return default_triggers

def get_users_triggers_with_count(user_id):
    """provide dictionary of user's triggers and their count"""

    user = User.query.get(user_id) #gives us User object
    usertriggerlist = user.user_triggers #gives us a list of usertrigger objects for user 

    trigger_count_dic = {}

    for usertrigger in usertriggerlist: #iterates through UserTrigger object to get triggers
        user_trigger_count = usertrigger.trigger_count
        triggerobject = usertrigger.trigger   #this is the trigger object for the user
        trigger_name = triggerobject.trigger_name
        if user_trigger_count > 0:
            trigger_count_dic[trigger_name] = user_trigger_count

    return trigger_count_dic

def get_users_triggers(user_id):     
    """get list of user's triggers as objects"""

    user = User.query.get(user_id) #gives us User object
    usertriggerobjects = user.user_triggers #gives us a list of usertrigger objects for user  
    users_triggers = []

    for trigger in usertriggerobjects:
        users_triggers.append(trigger.trigger)
    
    return users_triggers    #returns list of trigger objects for the user


def check_trigger_db(trigger_name):
    """Check if trigger name already in trigger table"""
    #will return None if not in table, will return Trigger object if it is

    return Trigger.query.filter(Trigger.trigger_name == trigger_name).first()


def check_users_triggers(user_id, trigger_id):
    """Check if trigger already in user's table"""

    return UserTrigger.query.filter(UserTrigger.user_id == user_id, 
                                               UserTrigger.trigger_id ==trigger_id).first()


def get_users_phone():
    """Returns list of tuples with all user's name and phone number"""
    
    users_phone = []
    query = User.query.all()
    for user in query:
        users_phone.append(user.phone_number)
    
    return users_phone

   


if __name__ == '__main__':
    from server import app
    connect_to_db(app)
"""CRUD operations."""

from model import db, User, Headache, Trigger, Medication, Period, connect_to_db

def create_user(email, password):
    """Create and return a new user."""

    user = User(email=email, password=password)

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

def create_trigger(user, trigger_name, trigger_count):
    """Create and return a new trigger"""

    trigger = Trigger(user=user,
                      trigger_name=trigger_name,
                      trigger_count=trigger_count
                      )
    return trigger

def update_trigger(trigger_id):
    """ Update a trigger given trigger_name and the updated count. """
    
    trigger = Trigger.query.get(trigger_id)

    trigger.trigger_count += 1
  


def get_user_by_email(email):
    """Verifies if a user email exists"""
    return User.query.filter(User.email == email).first()



if __name__ == '__main__':
    from server import app
    connect_to_db(app)
"""CRUD operations."""

from model import db, User, Headache, Trigger, Medication, Period, connect_to_db

def create_user(email, password):
    """Create and return a new user."""

    user = User(email=email, password=password)

    return user

def create_headache(date_start, pain_scale, headache_type, user):
    """Create and return a new headache."""

    headache = Headache(date_start=date_start, 
                  pain_scale=pain_scale, 
                  headache_type=headache_type,
                  user = user
                )

    return headache


def get_user_by_email(email):
    """Verifies if a user email exists"""
    return User.query.filter(User.email == email).first()



if __name__ == '__main__':
    from server import app
    connect_to_db(app)
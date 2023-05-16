from search import Base
from sqlalchemy import Column, Integer, String

class Profile(Base):

    __tablename__ = "profiles"

    pid = Column("pid", Integer, primary_key = True)
    name = Column("name", String)

    def __init__(self, name):
        self.name = name
        self.collection_list = []

def create_profile(new_username):
    return Profile(new_username)

def select_profile(username):
    for profile in Profile.all:
        if profile.name is username:
            return profile
    print("That is not an existing profile.")
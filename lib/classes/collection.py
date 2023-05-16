from search import Base
from classes.profile import Profile
from time import gmtime, strftime
from sqlalchemy import Column, Integer, String, ForeignKey

class Collection(Base):

    __tablename__ = "collections"

    cid = Column("cid", Integer, primary_key = True)
    name = Column("name", String)
    pid = Column(Integer, ForeignKey("profiles.pid"))
    profile = Column("profile", Profile)
    last_time_active = Column("last_time_active", Integer)

    all = []

    def __init__(self, name, pid, profile, last_time_active):
        self.name = name
        self.pid = pid
        self.profile = profile
        self.last_time_active = last_time_active
        self.url_list = []

        Collection.all.append(self)
        profile.collection_list.append(self)


def create_collection(new_collection_name, pid, profile):
    last_time_active = int(strftime("%Y%m%d%H%M%S", gmtime()))
    return Collection(new_collection_name, pid, profile, last_time_active)

def select_collection(collection_name):
    for collection in Collection.all:
        if collection.name is collection_name:
            collection.last_time_active = int(strftime("%Y%m%d%H%M%S", gmtime()))
            return collection
    print("That is not an existing collection. Please create a new one.")
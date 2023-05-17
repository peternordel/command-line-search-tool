from sqlalchemy import Column, Integer, String

from shared import Base
# from classes.collection import Collection
# from classes.site import Site

class Profile(Base):

    __tablename__ = "profiles"

    pid = Column("pid", Integer, primary_key = True)
    name = Column("name", String)
    last_time_active = Column("last_time_active", Integer)

    def __init__(self, name, last_time_active):
        self.name = name
        self.last_time_active = last_time_active
        self.collection_list = []

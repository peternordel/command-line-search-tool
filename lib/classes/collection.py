from sqlalchemy import Column, Integer, String, ForeignKey

from shared import Base
# from classes.profile import Profile
# from classes.site import Site

class Collection(Base):

    __tablename__ = "collections"

    cid = Column("cid", Integer, primary_key = True)
    name = Column("name", String)
    pid = Column(Integer, ForeignKey("profiles.pid"))
    last_time_active = Column("last_time_active", Integer)

    def __init__(self, name, pid, last_time_active):
        self.name = name
        self.pid = pid
        self.last_time_active = last_time_active

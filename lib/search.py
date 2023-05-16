#!/usr/bin/env python3

import argparse, webbrowser
from time import sleep

from sqlalchemy import create_engine, desc, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

# from classes.profile import Profile, create_profile, select_profile

from time import gmtime, strftime

class Profile(Base):

    __tablename__ = "profiles"

    pid = Column("pid", Integer, primary_key = True)
    name = Column("name", String)
    last_time_active = Column("last_time_active", Integer)

    def __init__(self, name, last_time_active):
        self.name = name
        self.last_time_active = last_time_active

def create_profile(new_username):
    last_time_active = int(strftime("%Y%m%d%H%M%S", gmtime()))
    return Profile(new_username, last_time_active)

def select_profile(username):
    for profile in Profile.all:
        if profile.name is username:
            profile.last_time_active = int(strftime("%Y%m%d%H%M%S", gmtime()))
            return profile
    print("That is not an existing profile.")

#

# from classes.collection import Collection, create_collection, select_collection

from time import gmtime, strftime

class Collection(Base):

    __tablename__ = "collections"

    cid = Column("cid", Integer, primary_key = True)
    name = Column("name", String)
    pid = Column(Integer, ForeignKey("profiles.pid"))
    last_time_active = Column("last_time_active", Integer)

    # I think we need to do this as a query instead so we can pull previously created collections.
    all = []

    def __init__(self, name, pid, last_time_active):
        self.name = name
        self.pid = pid
        self.last_time_active = last_time_active

        # see above
        Collection.all.append(self)

def create_collection(new_collection_name, pid):
    last_time_active = int(strftime("%Y%m%d%H%M%S", gmtime()))
    return Collection(new_collection_name, pid, last_time_active)

def select_collection(collection_name):
    # perhaps query here for all existing collections filtered by profile
    for collection in Collection.all:
        if collection.name is collection_name:
            collection.last_time_active = int(strftime("%Y%m%d%H%M%S", gmtime()))
            return collection
    print("That is not an existing collection. Please create a new one.")

#

# from classes.site import Site

VALID_SITE_EXTENSIONS = (".gov", ".edu", ".com", ".net", ".mil", ".org")

class Site(Base):

    __tablename__ = "sites"

    sid = Column("sid", Integer, primary_key = True)
    url = Column("url", String)
    cid = Column(Integer, ForeignKey("collections.cid"))

    def __init__(self, url, cid, collection):
        self.url = url
        self.cid = cid
        self.collection = collection

    @property
    def get_url(self):
        return self._url

    @get_url.setter
    def set_url(self, new_url):
        if type(new_url) is str and new_url[-4:] in VALID_SITE_EXTENSIONS and " " not in new_url:
            self._url = new_url
        else:
            raise Exception("URL must be a string that ends in a valid website extension.")

#

engine = create_engine("sqlite:///search.db", echo = True)
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()

active_profile = session.query(Profile).order_by(desc(Profile.last_time_active)).first()
active_collection = session.query(Collection).order_by(desc(Collection.last_time_active)).first()

if active_profile is not None:
    # profile_collection_objects = session.query(Collection).filter(Collection.pid == active_profile.pid)
    # active_profile.collection_list = []
    # for collection in profile_collection_objects:
    #     active_profile.collection_list.append(collection)
    active_profile.collection_list = session.query(Collection).filter(Collection.pid == active_profile.pid)

# This prevents the user from creating a profile and accessing another profile's collection.
if active_collection is not None and active_profile.pid != active_collection.pid:
    active_collection = None

# I don't think this is needed but am hesitant to delete because everything is working
session.close()

def run():

    if active_profile is not None and active_collection is not None:
        parser = argparse.ArgumentParser(prog="search assistant", description="searches google based on search query and saved sites")
        parser.add_argument('query', metavar='N', type=str, nargs='+', help='enter your search query')
        search_query = "+".join(parser.parse_args().query)

        site_urls = []
        collection_site_objects = session.query(Site).filter(Site.cid == active_collection.cid)
        for site in collection_site_objects:
            site_urls.append("site%3A" + site.url)
        sites = "+OR+".join(site_urls)
        # print(f"https://google.com/search?q={search_query}+site{sites}")
        webbrowser.open_new(f"https://google.com/search?q={search_query}+{sites}")

    else:
        print("No collection selected. Please use the searchconfig command to create or select a profile and/or collection.")

def config():
    all_commands = """
        Available commands (case insensitive):
        • pCreate: creates a profile.
        • pSelect: selects a profile.
        • cCreate: creates a collection.
        • cSelect: selects a collection.
        • sAdd: adds URL to active collection.
        • Show: shows active profile name and collection.
        • Help: shows this list of commands.
        • Quit: quits the input function. You can use search after quitting.
    """
    print(all_commands)

    is_inputting = True
    while is_inputting:
        user_input = input("Enter command: ")

        if user_input.lower() == "pcreate":
            profile_create()

        elif user_input.lower() == "pselect":
            profile_select()

        elif user_input.lower() == "ccreate":
            collection_create()

        elif user_input.lower() == "cselect":
            collection_select()

        elif user_input.lower() == "sadd":
            site_add()

        elif user_input.lower() == "show":
            show()

        elif user_input.lower() == "help":
            print(all_commands)

        elif user_input.lower() == "quit":
            is_inputting = False

        else:
            print("""
            That is not an availble command. Please use commands from the list above. Use help to show available commands again.
            
            """)
            sleep(1)

def profile_create():
    global active_profile, active_collection
    command_input = input("Enter new profile username: ")
    active_profile = create_profile(command_input)
    active_collection = None

    session.add(active_profile)
    session.commit()

def profile_select():
    global active_profile, active_collection
    # if len(Profile.all) == 0 then stop this, do the same with collections
    print("Existing profiles: ")
    for profile in Profile.all:
        print(f"• {profile.name}")
    command_input = input("Enter profile name: ")
    active_profile = select_profile(command_input)
    active_collection = None

def collection_create():
    if active_profile is None:
        print("There is no active profile. Please create or select one.")
    else:
        global active_collection
        command_input = input("Enter new collection: ")
        active_collection = create_collection(command_input, active_profile.pid)

        session.add(active_collection)
        session.commit()

def collection_select():
    if active_profile is None:
        print("There is no active profile. Please create or select one.")
    else:
        global active_collection
        print("Existing collections for this profile: ")
        for collection in collection.all:
            print(f"• {collection.name}")
        command_input = input("Enter collection name: ")
        active_collection = select_collection(command_input)

def site_add():
    if active_collection is None:
        print("There is no active collection. Please create or select one.")
    else:
        command_input = input("Enter a URL to add to the active collection: ")
        stripped_input = command_input.strip()

        # this list is to support inputting lists if time permits.
        inputted_site_list = []
        inputted_site_list.append(stripped_input)

        for url in inputted_site_list:
            new_site = Site(url, active_collection.cid, active_collection)
            if new_site is not None:
                session.add(new_site)
                session.commit()

def show():
    if active_profile is None:
        print("There is no active profile.")
    elif active_collection is None:
        print(f"""
            Active profile: {active_profile.name}
            There is no active collection.
        """)
    else:
        print(f"""
            Active profile: {active_profile.name}
            Active collection: {active_collection.name}
        """)


# profile_create()
# # peternordel

# collection_create()
# # computer_science

# site_add()
# # stackoverflow.com
# site_add()
# # stackexchange.com
# site_add()
# # quora.com

# import ipdb
# ipdb.set_trace()
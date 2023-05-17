#!/usr/bin/env python3

### MODULE IMPORTS ###
import argparse, webbrowser
from time import gmtime, strftime, sleep
from sqlalchemy import create_engine, desc, orm

### FILE IMPORTS ###
from shared import Base
from classes.profile import Profile
from classes.collection import Collection
from classes.site import Site

engine = create_engine("sqlite:///search.db", echo = False)
Base.metadata.create_all(bind=engine)

Session = orm.sessionmaker(bind=engine)
session = Session()

all_profiles = session.query(Profile).order_by(desc(Profile.last_time_active)).all()

if len(all_profiles) == 0:
    active_profile = None
else:
    active_profile = all_profiles[0]

active_collection = session.query(Collection).order_by(desc(Collection.last_time_active)).first()

def get_collections_for_profile(profile):
    profile.collection_list = session.query(Collection).filter(Collection.pid == profile.pid).all()
    return profile.collection_list

def get_sites_for_collection(collection):
    site_list = session.query(Site).filter(Site.cid == collection.cid).all()
    return site_list

if active_profile is not None:
    get_collections_for_profile(active_profile)

# This prevents the user from creating a profile and accessing another profile's collection.
if active_collection is not None and active_profile.pid != active_collection.pid:
    active_collection = None

def run():

    if active_profile is not None and active_collection is not None:
        parser = argparse.ArgumentParser(prog="search assistant", description="searches google based on search query and saved sites")
        parser.add_argument('query', metavar='N', type=str, nargs='+', help='enter your search query')
        search_query = "+".join(parser.parse_args().query)

        site_list = get_sites_for_collection(active_collection)
        query_sites = []
        for index in range(len(site_list)):
            query_sites.append("site%3A" + site_list[index].url)
        sites = "+OR+".join(query_sites)

        webbrowser.open_new(f"https://google.com/search?q={search_query}+{sites}")

    else:
        print("No collection selected. Please use the searchconfig command to create or select a profile and/or collection.")

def config():
    global all_cmds
    all_cmds = """
Available commands (case insensitive):
• pCreate: creates a profile.
• pSelect: selects a profile.
• pDelete: deletes a profile.
• cCreate: creates a collection.
• cSelect: selects a collection.
• cDelete: deletes a collection.
• sAdd: adds URL to active collection.
• sDelete: deletes URL from active collection.
• Show: shows active profile name and collection.
• Help: shows this list of commands.
• Quit: quits the input function. You can use search after quitting.
    """
    print(all_cmds)

    cmd_to_function = {
        "pcreate": profile_create,
        "pselect": profile_select,
        "pdelete": profile_delete_by_user_input,
        "ccreate": collection_create,
        "cselect": collection_select,
        "cdelete": collection_delete_by_user_input,
        "sadd": site_add,
        "sdelete": site_delete_by_user_input,
        "show": show,
        "help": help,
        "quit": quit
    }

    global is_inputting
    is_inputting = True

    while is_inputting:
        user_input = input("\nEnter command: ")
        if user_input.lower() in cmd_to_function.keys():
            cmd_to_function[user_input.lower()]()
        else:
            print("""
    That is not an availble command. Please use commands from the list above. Use help to show available commands again.""")
            sleep(1)
        session.commit()

def profile_list_print():
    print("""
    Existing profiles: """)
    for profile in all_profiles:
            print(f"    • {profile.name}")
    
def profile_create():
    global active_profile, active_collection
    command_input = input("""
    Enter new profile username: """)

    last_time_active = int(strftime("%Y%m%d%H%M%S", gmtime()))
    active_profile = Profile(command_input, last_time_active)
    active_collection = None
    session.add(active_profile)

def profile_select():
    global active_profile, active_collection
    if len(all_profiles) == 0:
        print("""
    There are no profiles to select from. Please use pCreate to create one.""")
    else:
        active_collection = None
        profile_list_print()
        command_input = input("""
    Enter profile name: """)

        for profile in all_profiles:
            if profile.name == command_input:
                profile.last_time_active = int(strftime("%Y%m%d%H%M%S", gmtime()))
                active_profile = profile
                get_collections_for_profile(active_profile)
                return
        print("""
    That is not an existing profile.""")

def profile_delete_by_user_input():
    if len(all_profiles) == 0:
        print("""
    No profiles exist. Please use pcreate to create one, which you can then delete to your heart's content!""")
    else:
        global active_profile, active_collection
        profile_list_print()
        command_input = input("""
    Enter profile name to delete: """)

        for profile in all_profiles:
            if profile.name == command_input:
                if profile.name == active_profile.name:
                    active_profile = None
                    active_collection = None
                get_collections_for_profile(profile)
                for collection in get_collections_for_profile(profile):
                    collection_delete(collection)
                    session.query(Profile).filter(Profile.pid == profile.pid).delete()
                return
        print("""
    That is not an existing profile. Returning to main command line.""")

def collection_list_print():
    print("""
    Existing collections for this profile: """)
    for collection in active_profile.collection_list:
        print(f"    • {collection.name}")

def collection_create():
    if active_profile is None:
        print("""
    There is no active profile. Please create or select one.""")

    else:
        global active_collection
        command_input = input("""
    Enter new collection: """)

        last_time_active = int(strftime("%Y%m%d%H%M%S", gmtime()))
        active_collection = Collection(command_input, active_profile.pid, last_time_active)

        active_profile.collection_list.append(active_collection)
        session.add(active_collection)

def collection_select():
    if active_profile is None:
        print("""
    There is no active profile. Please create or select one.""")
    elif len(active_profile.collection_list) == 0:
        print("""
    There are no collections created for this profile. Please use cCreate to create one.""")
    else:
        collection_list_print()
        command_input = input("""
    Enter collection name to select: """)
        for collection in active_profile.collection_list:
            if collection.name == command_input:
                collection.last_time_active = int(strftime("%Y%m%d%H%M%S", gmtime()))
                global active_collection
                active_collection = collection
                return
        print("""
    That is not an existing collection. Please create a new one.""")

def collection_delete_by_user_input():
    if len(active_profile.collection_list) == 0:
        print("""
    No collections exist for this profile. Please use ccreate to create one, which you can then delete to your heart's content!""")
    else:
        collection_list_print()
        command_input = input("""
    Please enter a collection name to delete: """)
        for collection in active_profile.collection_list:
            if collection.name == command_input:
                if collection.name == active_collection.name:
                    active_collection = None
                collection_delete(collection)
                return
        print("""
    That collection does not exist. Returning to main command line.""")
                
def collection_delete(collection):
    session.query(Site).filter(Site.cid == collection.cid).delete()
    session.query(Collection).filter(Collection.cid == collection.cid).delete()

def site_list_print_and_return():
    site_list = get_sites_for_collection(active_collection)
    if len(site_list) == 0:
        print(f"""
    No sites created for this collection. Please use sAdd to add sites""")
    else:
        for site in site_list:
            print(f"    • {site.url}")
    return site_list

def site_add():
    if active_collection is None:
        print("""
    There is no active collection. Please create or select one.""")
        
    else:
        command_input = input("""
    Enter a URL to add to the active collection: """)
        stripped_input = command_input.strip()

        # this list is to support inputting lists if time permits.
        inputted_site_list = []
        inputted_site_list.append(stripped_input)

        for url in inputted_site_list:
            new_site = Site(url, active_collection.cid)
            if new_site is not None:
                session.add(new_site)

def site_delete_by_user_input():
    site_list = site_list_print_and_return()
    if len(site_list) != 0:
        command_input = input("""
    Please enter a site to delete: """)
        for site in site_list:
            if command_input == site.url:
                session.query(Site).filter(Site.url == site.url).delete()
                return
    print("""
    That is not a site in this collection. Returning to main command line.""")

def show():
    if active_profile is None:
        print("""
    There is no active profile.""")
        
    elif active_collection is None:
        print(f"""
    Active profile: {active_profile.name}
    There is no active collection.""")
        
    else:
        print(f"""
    Active profile: {active_profile.name}
    Active collection: {active_collection.name}
    Sites in {active_collection.name}:""")
        site_list_print_and_return()

def help():
    print(all_cmds)

def quit():
    global is_inputting
    is_inputting = False

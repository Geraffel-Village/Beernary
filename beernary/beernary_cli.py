#!/usr/bin/python3

"""
This application provides commong maintenance options for the beernary application.
"""

import sys

import configparser

import modules.database

CONFIG_FILE_PATH    = "/etc/beernary/config.ini"

def new_keg(database, event_id):
    """Adds new keg with given volume to database."""
    print("Enter keg volume in liters: ")
    volume = input()

    database.new_keg(event_id, volume)

def new_user(database):
    """Adds new user with tag ID to database."""
    print("Enter user tag ID as string: ")
    user_id = input()

    print("Enter user name as string: ")
    user_name = input()

    database.add_user(user_id, user_name)

if __name__ == "__main__":

    if len(sys.argv)>1:

        if sys.argv[1] == "new-keg" or sys.argv[1] == "new-user":

            config = configparser.ConfigParser(allow_no_value=True)
            config.read(CONFIG_FILE_PATH)

            mysql_host              = config.get("mysql",            "hostname")
            mysql_user              = config.get("mysql",            "username")
            mysql_password          = config.get("mysql",            "password")
            mysql_database          = config.get("mysql",            "database")


            database   = modules.database.BeernaryMysqlTransaction(host=mysql_host,
                                                               user=mysql_user,
                                                               passwd=mysql_password,
                                                               database=mysql_database)

            event_data  = database.get_active_event()
            event_id    = event_data[0]
            event_name  = event_data[1]

            if sys.argv[1] == "new-keg":
                new_keg(database, event_id)

            elif sys.argv[1] == "new-user":
                new_user(database)

        else:
            print(f"Invalid task: {sys.argv[1]}")
            sys.exit(1)

    else:
        print("No task given. Use new-keg or new-user.")

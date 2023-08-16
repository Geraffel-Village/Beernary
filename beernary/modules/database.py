#!/usr/bin/python3

"""
Controls the beenary`s persistent data operations. Supports different types (abstract base class).
"""

from abc import ABC, abstractmethod

import pymysql
from loguru import logger

class BeernaryTransactionLogicError(Exception):
    "Raised in case of any logical errors when running transactions."


class BeernaryTransaction(ABC):
    """Abstract base class to describe a transaction in any kind of storage backend."""

    @abstractmethod
    def __init__(self):
        """Abstract constructor to initialize the transaction processor (e.g. open mysql)."""

    # User transactions

    @abstractmethod
    def check_user(self, user_id):
        """
        Abstract method to check if a user`s ID is allowed.

        Parameters:
        user_id   - ID of a user to check
        """

    @abstractmethod
    def get_users(self):
        """Abstract method to get a list of all users."""

    @abstractmethod
    def add_user(self, user_id, tap_id, user_name):
        """
        Abstract method to add a user.

        Parameters:
        user_id    - ID of the new user
        tap_id     - ID of the tap to use (1/2)
        user_name  - Name of the new user
        """

    @abstractmethod
    def delete_user(self, user_id):
        """
        Abstract method to delete a user.

        Parameters:
        user_id    - ID of the user to delete
        """

    # Draft transactions

    @abstractmethod
    def store_draft(self, user_id, pulses):
        """
        Abstract method to store a user`s draft transaction.

        Parameters:
        user_id   - ID of the user who drafted
        pulses    - Amount of pulses to store
        """

    # Keg transactions

    @abstractmethod
    def get_keg_pulses(self, keg_id):
        """
        Abstract method to get a keg`s pulses.

        Parameters:
        keg_id - Number of keg to get pulses of
        """

    @abstractmethod
    def set_keg_pulses(self, keg_id, pulses):
        """
        Abstract method to set a keg`s pulses.

        Parameters:
        keg_id - Number of keg to set pulses for
        pulses     - Amount of pulses to set
        """

    @abstractmethod
    def get_events(self):
        """Abstract method to get list of all events."""

    @abstractmethod
    def new_keg(self, event_id, volume):
        """
        Abstract method to add a new keg.

        Parameters:
        event_id   - ID of the keg`s event
        volume     - Volume of the keg in liters
        """

    @abstractmethod
    def get_current_keg(self, event_id):
        """
        Abstract method to get the current keg.

        Parameters:
        event_id   - ID of the current event
        """

    # Event transactions

    @abstractmethod
    def get_event_name(self, event_id):
        """
        Abstract method to get name of the event.

        Parameters:
        event_id   - ID of the event to get name of
        """

    @abstractmethod
    def get_active_event(self):
        """Abstract method to get the current event."""


class BeernaryMysqlTransaction(BeernaryTransaction):
    """Represents the currently used mysql database storage backend."""

    def __init__(self, **kwargs):

        self.connection = pymysql.connect(**kwargs)
        self.cursor     = self.connection.cursor()

    # User transactions

    def check_user(self, user_id):
        self.connection.begin()
        self.cursor.execute (f"SELECT name,tapid FROM `users` WHERE id = '{user_id}';")

        result = self.cursor.fetchone()
        if result is not None:
            return result[0], result[1]
        else:
            return None

    def get_users(self):
        self.connection.begin()
        self.cursor.execute ("SELECT id,name,timestamp FROM `users` ORDER BY timestamp DESC;") # pylint: disable=line-too-long
        return self.cursor.fetchall()

    def add_user(self, user_id, tap_id, user_name):
        self.cursor.execute(f"SELECT id FROM `users` WHERE id = '{user_id}';")

        if self.cursor.rowcount != 0:
            logger.critical(f"User with ID {user_id} is already registered")
            raise BeernaryTransactionLogicError("ID already registered")

        self.cursor.execute(f"SELECT name FROM `users` WHERE name = '{user_name}';")

        if self.cursor.rowcount != 0:
            logger.critical(f"User with name {user_name} already has tag assigned")
            raise BeernaryTransactionLogicError("Name already registered")

        self.cursor.execute(f"INSERT IGNORE INTO `users` SET id = '{user_id}', tapid = {tap_id}, name = '{user_name}';") # pylint: disable=line-too-long
        self.connection.commit()
        logger.info(f"Added user with ID {user_id} and name {user_name}")

    def delete_user(self, user_id):
        try:
            self.cursor.execute(f"DELETE from `users` where id = {user_id};")
            self.connection.commit()

        except Exception as exception:
            logger.critical(f"Could not delete user: {user_id}")
            raise BeernaryTransactionLogicError("Error while deleting user: ", exception) from exception # pylint: disable=line-too-long

    # Draft transactions

    def store_draft(self, user_id, pulses):
        self.cursor.execute (f"Insert INTO `consume` (id, pulses) VALUES ('{user_id}', {pulses})")
        self.connection.commit()

        logger.debug(f"Added draft of {pulses} to user {user_id}")

    # Keg transactions

    def get_keg_pulses(self, keg_id):
        self.connection.begin()
        self.cursor.execute (f"SELECT pulses FROM `keg` WHERE kegid={keg_id}")
        return self.cursor.fetchone()[0]

    def set_keg_pulses(self, keg_id, pulses):
        self.cursor.execute (f"UPDATE `keg` SET pulses = {pulses} WHERE kegid = {keg_id}")
        self.connection.commit()
        logger.debug(f"Added {pulses} pulses to keg {keg_id}")

    def get_events(self):
        self.connection.begin()
        self.cursor.execute ("SELECT name, eventid FROM `event` ORDER by name")
        return self.cursor.fetchall()

    def new_keg(self, event_id, volume):

        # mark current keg as empty (implict by method usage)
        self.cursor.execute(f"UPDATE `keg` SET isempty = True WHERE eventid = {event_id} AND isEmpty = False;") # pylint: disable=line-too-long

        if self.cursor.rowcount == 0:
            logger.info("No non-empty kegs detected, adding first")

        if self.cursor.rowcount == 1:
            logger.debug("Marked previous keg as empty (was non-empty)")

        elif self.cursor.rowcount != 1:
            self.connection.rollback()
            logger.critical("Invalid amount of non-empty kegs - aborting")
            raise BeernaryTransactionLogicError("More than one non-empty keg in database")

        self.cursor.execute (f"INSERT INTO `keg` (eventid, volume) VALUES ({event_id}, {volume})")
        self.connection.commit()

    def get_current_keg(self, event_id):
        self.connection.begin()
        self.cursor.execute(f"SELECT kegid FROM `keg` WHERE eventid = {event_id} AND isEmpty = False;") # pylint: disable=line-too-long

        if self.cursor.rowcount != 1:
            logger.critical("Invalid amount of non-empty kegs - aborting")
            raise BeernaryTransactionLogicError("More than one non-empty keg in database")

        assert self.cursor.rowcount == 1
        return self.cursor.fetchone()[0]

    # Event transactions

    def get_event_name(self, event_id):
        self.connection.begin()
        self.cursor.execute (f"SELECT `name` FROM `event` WHERE eventid = {event_id};")
        return self.cursor.fetchone()[0]

    def get_active_event(self):
        self.connection.begin()
        self.cursor.execute("SELECT eventid, name FROM `event` where selected = true;")

        if self.cursor.rowcount != 1:
            logger.critical("Invalid amount of active events - aborting")
            raise BeernaryTransactionLogicError("More than one active event in database")

        assert self.cursor.rowcount == 1
        return self.cursor.fetchone()

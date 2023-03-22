"""
This file contains SymbolManager, which keeps track of the symbol list, 
validates new lists, and interfaces with the SQLite database.

Symbol lists are stored on a per-profile basis in the the collections database, 
which is referenecd by mw.col.db. There is a separate profiles database that
Anki uses to store user profiles (mw.pm.db). 
"""

import sys
import string
import json
import aqt

from .default_symbols import DEFAULT_MATCHES, SPECIAL_KEYS

class SymbolManager(object):
    """ 
    SymbolManager takes in a callback function so that when the symbol list
    is updated, each Anki editor window can be reloaded with the updated
    symbol list.
    """

    TBL_NAME = 'ins_symbols'

    SUCCESS = 0
    ERR_NO_DATABASE = -1
    ERR_INVALID_FORMAT = -2
    ERR_KEY_CONFLICT = -3

    def __init__(self, main_window, update_callback):
        self._mw = main_window
        self._symbols = None
        self._defaults = None
        self._update_callback = update_callback

    def on_profile_loaded(self):
        """ 
        Called when a new profile is loaded. First tries to load the symbol 
        list from the database. If that is not successful, loads the default 
        symbol list instead, then saves it to the database.
        """
        is_load_successful = self._check_db_exists()

        if not is_load_successful:
            self._create_db()
        else:
            code = self._load_from_db()
            is_load_successful = (code == self.SUCCESS)

        # At this point, the database should have been created already. If load
        # wasn't successful for whatever reason, use the default list and save 
        # it to the database.
        if not is_load_successful:
            self._symbols = self.get_default_list()
            self._save_to_db()


    """ Getters """

    def get_match_list(self):
        """
        Converts the symbol list into a match list sorted by key length in
        descending order. Each entry contains the key/value plus a flag 
        indicating the type of entry.

        Flag: 2 = HTML block, 1 = immediate, 0 = normal
        """
        if not self._symbols:
            return None

        symbols = sorted(self._symbols, key=lambda x: len(x[0]), reverse=True)
        output = []
        for key, val in symbols:
            if key.startswith('::') and key.endswith('::'):
                flag = 2
            elif (key.startswith(':') and key.endswith(':') 
                or key in SPECIAL_KEYS):
                flag = 1
            else:
                flag = 0

            output.append({"key": key,"val": val, "f": flag})
        return output

    def get_JSON(self):
        """ 
        Returns a JSON version of the match list
        """
        output = self.get_match_list()
        if not output:
            return "'[]'"
        # sys.stderr.write(json.dumps(output))
        # sys.stderr.write(json.dumps(json.dumps(output)))
        return json.dumps(json.dumps(output))

    def get_list(self):
        """
        Returns a copy of the symbol list sorted in alphabetical order. 
        """
        return sorted(self._symbols, key=lambda x: x[0])

    def get_default_list(self):
        """ 
        Returns a copy of the default symbol list sorted in alphabetical order.
        """
        return sorted(DEFAULT_MATCHES, key=lambda x: x[0])


    """ Setters """

    def _set_symbol_list(self, new_list):
        """ 
        Performs error-checking, then updates self._symbols. Returns None if 
        there are no errors, or otherwise returns a tuple of the format 
        (ERROR_CODE, ERRORS) as detailed below:

         Error Code:         Content of ERRORS:
        -------------       ----------------------
        ERR_INVALID_FORMAT  List of indices where format of new_list is wrong.
        ERR_KEY_CONFLICT    List of key conflicts in new_list.
        """
        errors = SymbolManager.check_format(new_list)
        if errors:
            return (self.ERR_INVALID_FORMAT, errors)

        errors = SymbolManager.check_for_duplicates(new_list)
        if errors:
            return (self.ERR_KEY_CONFLICT, errors)

        self._symbols = new_list
        return None

    def update_and_save_symbol_list(self, new_list):
        """ 
        Attempts to update the symbol list, and if successful, saves the symbol 
        list to database and calls the callback function. Returns the same 
        output as _set_symbol_list().
        """
        errors = self._set_symbol_list(new_list)
        if not errors:
            self._save_to_db()
            self._update_callback()
        return errors


    """ Validation Static Functions """

    @staticmethod
    def check_format(kv_list, ignore_empty=False):
        """ 
        Checks that each entry is of the format (key, value), and that each key
        is not None or the empty string. This function can be set to ignore 
        emtpy lines.

        @param kv_list: A list.
        @param ignore_empty: Whether to skip empty lines (represented as an 
          empty list)
        @return: Returns a list of (index, line_contents), or None if no 
          invalid lines.
        """
        has_error = False
        errors = []
        for i in range(len(kv_list)):
            item = kv_list[i]
            if ignore_empty and len(item) == 0:
                continue

            if len(item) != 2 or not item[0] or not item[1]:
                has_error = True
                err_str = ' '.join(map(str, item))
                errors.append(tuple((i + 1, err_str)))
        return errors if has_error else None

    @staticmethod
    def check_if_key_valid(key):
        """ Checks whether key is a valid standalone key. """
        return not True in [c in key for c in string.whitespace]

    @staticmethod
    def check_if_key_duplicate(new_key, kv_list):
        """ 
        Checks to see if the new key would be a duplicate of any existing keys
        in the given key-value list.
        """
        for k, v in kv_list:
            if new_key == k:
                return True
        return None

    @staticmethod
    def check_for_duplicates(kv_list):
        """
        Checks for duplicate keys within the key-value list and returns a list
        of duplicate keys. This function accepts empty lines within the key-
        value list, empty list.

        @return: Returns a set of duplicate keys, or None if there are no 
          duplicates.
        """
        has_duplicate = False
        duplicates = set()

        for i in range(len(kv_list)):
            if len(kv_list[i]) == 0:
                continue

            for j in range(i):
                if len(kv_list[j]) == 0:
                    continue
                k1 = kv_list[i][0]
                k2 = kv_list[j][0]

                if k1 == k2:
                    has_duplicate = True
                    duplicates.add(k1)

        return duplicates if has_duplicate else None


    """ 
    Database Access Functions
    """

    def _check_db_exists(self):
        """ Returns whether the symbol database exists. """
        query = "SELECT * FROM sqlite_master WHERE type='table' AND name='%s'"
        return self._mw.col.db.first(query % self.TBL_NAME)

    def _create_db(self):
        """ Creates a new table for the symbol list. """
        query = "CREATE TABLE %s (key varchar(255), value varchar(255))"
        self._mw.col.db.execute(query % self.TBL_NAME)

    def _load_from_db(self):
        """ 
        Attempts to load the symbol list from the database, and returns a code 
        indicating the result. 
        """
        symbols = self._mw.col.db.all("SELECT * FROM %s" % self.TBL_NAME)

        if not symbols:
            return self.ERR_NO_DATABASE
        errors = self._set_symbol_list(symbols)

        return errors[0] if errors else self.SUCCESS

    def _save_to_db(self):
        """ 
        Deletes all old values, then writes the symbol list into the database. 
        """
        self._mw.col.db.execute("delete from %s" % self.TBL_NAME)
        for (k, v) in self._symbols:
            query = "INSERT INTO %s VALUES (?, ?)"
            self._mw.col.db.execute(query % self.TBL_NAME, k, v)
        self._mw.col.db.commit()


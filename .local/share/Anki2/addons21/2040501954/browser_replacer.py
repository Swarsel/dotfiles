"""
This file contains BrowserReplacer, which replicates the function of 
replacer.js for the Browser search bar.
"""


from aqt.qt import *

class BrowserReplacer(object):

    def __init__(self, match_list):
        self._match_list = match_list

    def on_browser_init(self, browser, mw, card = None, search = None):
        """ Set up hooks to the search box. """
        self._browser = browser

        search_box = self.get_search_box()
        if search_box:
            search_box.textEdited.connect(self.on_text_edited)
            search_box.returnPressed.connect(self.on_return_pressed)

    def update_list(self, match_list):
        self._match_list = match_list

    def get_search_box(self):
        """ Underlying QLineEdit object can get deleted. """
        searchEdit = self._browser.form.searchEdit
        if not searchEdit:
            return None
        else:
            return searchEdit.lineEdit()


    """ Event Handling """

    def on_return_pressed(self):
        search_box = self.get_search_box()
        if search_box:
            current_text = search_box.text()
            self._check_for_replacement(current_text, True)

    def on_text_edited(self, current_text):
        self._check_for_replacement(current_text, False)


    """ Matching Functions """

    def _is_whitespace(self, string, i):
        """ Checks whether string[i] is whitespace. """
        if i < 0 or i >= len(string):
            return False
        return string[i].isspace()

    def _check_for_replacement(self, text, is_enter_pressed):
        """ 
        Port of code in replacer.js. The major difference is that this function
        is triggered after a whitespace character is inserted, whereas it isn't
        in the Javascript code. 
        """
        search_box = self.get_search_box()
        if not text or not search_box:
            return

        cursor_pos = search_box.cursorPosition()
        if is_enter_pressed:
            is_whitespace_pressed = False
        else:
            is_whitespace_pressed = self._is_whitespace(text, cursor_pos-1)

        match = self._matches_keyword(text, cursor_pos, 
            is_whitespace_pressed, is_enter_pressed)
        if match:
            self._perform_replacement(text, match[0], match[1], match[2])

    def _matches_keyword(self, text, cursor_pos, is_whitespace_pressed, 
        is_enter_pressed):
        """ Port of code in replacer.js. """
        for item in self._match_list:
            key = item['key']
            val = item['val']
            trigger_on_space = (item['f'] == 0)

            if trigger_on_space:
                # Make sure to 1) only trigger after whitespace and 2) ignore 
                # any trailing spaces:
                if is_enter_pressed:
                    end_index = cursor_pos
                elif is_whitespace_pressed:
                    end_index = cursor_pos - 1
                else:
                    continue
            else:
                end_index = cursor_pos

            start_index = max(end_index - len(key), 0)
            if text[start_index : end_index] == key:
                if trigger_on_space:
                    # Check that character preceding key is whitespace:
                    prior_idx = start_index - 1
                    if prior_idx >= 0 and not self._is_whitespace(text, prior_idx):
                        continue
                return (val, start_index, end_index)
        return None

    def _perform_replacement(self, old_text, value, start_idx, end_idx):
        """ Port of code in replacer.js. """
        new_text = old_text[:start_idx] + value + old_text[end_idx:]
        self.get_search_box().setText(new_text)
        self.get_search_box().setCursorPosition(start_idx + len(value))


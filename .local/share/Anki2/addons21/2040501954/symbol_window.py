""" 
This file houses the controller for Ui_SymbolWindow, which is the PyQt GUI that 
lets users edit the symbol list.

All symbol edits are performed on a local copy of the list owned by 
SymbolWindow (henceforth referred to as the "working list"). No changes are 
made to the symbolList in SymbolManager until the 'OK' button is clicked, which
internally triggers a call to SymbolWindow.accept().
"""

import aqt
import io
import csv

from aqt.qt import *

from .get_version import *
from .symbol_manager import SymbolManager
from .Ui_SymbolWindow import Ui_SymbolWindow

ANKI_VER = get_anki_version()

class SymbolWindow(QDialog):
    """
    SymbolWindow is a controller for Ui_SymbolWindow. It makes changes to the
    working list and updates the GUI in accordance with user input.

    The working list must obey the following rules at all times:
    1. It must be sorted in alphabetical order by key
    2. There must be no duplicate or conflicting keys (ie. keys that are 
      substrings of one another).
    """

    def __init__(self, parent_widget, symbol_manager):
        super(SymbolWindow, self).__init__(parent_widget)
        self._sym_manager = symbol_manager
        self._working_list = None
        self._selected_row = -1

        self.ui = Ui_SymbolWindow()
        self.ui.setupUi(self)
        
        self.ui.importButton.clicked.connect(self.import_list)
        self.ui.exportButton.clicked.connect(self.export_list)
        self.ui.okButton.clicked.connect(self.accept)
        self.ui.cancelButton.clicked.connect(self.reject)
        self.ui.resetButton.clicked.connect(self.reset_working_list)

        self.ui.addReplaceButton.clicked.connect(self.add_pair_to_list)
        self.ui.deleteButton.clicked.connect(self.delete_pair_from_list)

        # This is the text box labeled 'key':
        self.ui.keyLineEdit.textEdited.connect(self.on_key_text_changed)
        self.ui.keyLineEdit.returnPressed.connect(self.on_kv_return_pressed)

        # This is the text box labeled 'value':
        self.ui.valueLineEdit.textEdited.connect(self.on_value_text_changed)
        self.ui.valueLineEdit.returnPressed.connect(self.on_kv_return_pressed)

        self.ui.tableWidget.cellClicked.connect(self.on_cell_clicked)
        h_header = self.ui.tableWidget.horizontalHeader()
        if ANKI_VER == ANKI_VER_PRE_2_1_0:
            h_header.setResizeMode(0, QHeaderView.ResizeMode.Stretch)
            h_header.setResizeMode(1, QHeaderView.ResizeMode.Stretch)
        else:
            h_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            h_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)


    """ Editor State Getters """

    def _get_key_text(self):
        return self.ui.keyLineEdit.text().strip()

    def _get_val_text(self):
        return self.ui.valueLineEdit.text()#.strip()

    def is_row_selected(self):
        """ Returns true if a row in the tableWidget is selected. """
        return self._selected_row >= 0

    def is_key_valid(self):
        text = self._get_key_text()
        return bool(text) and SymbolManager.check_if_key_valid(text)

    def is_val_valid(self):
        return bool(self._get_val_text())

    def is_val_different(self):
        """ 
        Checks if the value in the LineEdit is different than the value of the
        selected k-v entry. If nothing is selected, return False.
        """
        if not self.is_row_selected(): 
            return False
        old = self._working_list[self._selected_row][1]
        new = self._get_val_text()
        return old != new


    """ 
    UI Update Functions 

    An add operation (where no existing k-v pair is selected) can occur if:
     - The new key is valid
     - The new value is valid

    A replace operation (where an existing k-v pair is selected) can occur if:
     - The new key is valid 
     - The new value is valid 
     - The new value is different from the selected k-v pair's value
    """

    def _on_row_selected(self, row, enable_add_replace):
        """ 
        Called when a row in the tableView is selected, which occurs either 
        A) when the user types a string into keyLineEdit that matches an 
        existing key or B) when the user clicks on a cell in the tableView. 

        Changes addReplaceButton to replace mode and enables the delete 
        command. In scenario A addReplaceButton may be enabled if the text in 
        valueLineEdit is different (so that users may replace the existing 
        entry), but in scenario B addReplaceButton should NOT be enabled since 
        both keyLineEdit and valueLineEdit are updated to cell contents.
        """
        if self._selected_row == -1:
            self.ui.addReplaceButton.setText("Replace")
            self.ui.addReplaceButton.clicked.disconnect(self.add_pair_to_list)
            self.ui.addReplaceButton.clicked.connect(self.replace_pair_in_list)

        self.ui.addReplaceButton.setEnabled(enable_add_replace)
        self.ui.deleteButton.setEnabled(True)
        self._selected_row = row

    def _on_row_deselected(self, enable_add_replace):
        """ 
        Called when a row in the tableView is deselected, which occurs either 
        A) when the user types a string into keyLineEdit that doesn't match any
        existing keys or B) when the working list is somehow otherwise updated. 

        Changes addReplaceButton to add mode and disables the delete command. 
        In scenario A addReplaceButton may be enabled if the text in 
        valueLineEdit is different (so that users may add a new entry), but in
        scenario B addReplaceButton should NOT be enabled since both 
        keyLineEdit and valueLineEdit will be reset.
        """
        if self._selected_row != -1:
            self.ui.addReplaceButton.setText("Add")
            self.ui.addReplaceButton.clicked.disconnect(
                self.replace_pair_in_list)
            self.ui.addReplaceButton.clicked.connect(self.add_pair_to_list)
            
        self.ui.addReplaceButton.setEnabled(enable_add_replace)
        self.ui.deleteButton.setEnabled(False)
        self._selected_row = -1

    def _on_working_list_updated(self):
        """ 
        Called when the working list is updated. Clears keyLineEdit, 
        valueLineEdit, and deselects any selected rows in the tableView. 
        """
        self.ui.keyLineEdit.setText("")
        self.ui.valueLineEdit.setText("")

        self._on_row_deselected(False)
        self._check_table_widget_integrity()

    def _scroll_to_index(self, index):
        if len(self._working_list) <= 0:
            return
        # Scroll to last row if key would be placed at the end
        index = min(index, self.ui.tableWidget.rowCount() - 1)

        item = self.ui.tableWidget.item(index, 0)
        self.ui.tableWidget.scrollToItem(item, QAbstractItemView.ScrollHint.PositionAtTop)

    def on_key_text_changed(self, current_text):
        """ 
        Called when the text in keyLineEdit is changed. First scrolls the 
        tableWidget, then updates add/replace and delete buttons.
        """
        current_text = current_text.strip()
        found, idx = self._find_prospective_index(current_text)
        self._scroll_to_index(idx)

        if not self.is_key_valid():
            self._on_row_deselected(False)
        else:
            # If current_text is not found, this should be an add operation.
            # Otherwise, this should be a replace.
            if found:
                can_replace = self.is_val_valid() and self.is_val_different()
                self._on_row_selected(idx, can_replace)
            else:
                self._on_row_deselected(self.is_val_valid())

    def on_value_text_changed(self, current_text):
        """ 
        Called when the text in valueLineEdit is changed. Toggles whether 
        addReplaceButton is clickable.
        """
        if self.is_row_selected():
            can_replace = (self.is_key_valid() and self.is_val_valid() 
                and self.is_val_different())
            self.ui.addReplaceButton.setEnabled(can_replace)
        else:
            can_add = (self.is_key_valid() and self.is_val_valid())
            self.ui.addReplaceButton.setEnabled(can_add)

    def on_kv_return_pressed(self):
        """ 
        Called when the Enter key is pressed while either keyLineEdit or 
        valueLineEdit has focus, and performs an add or replace action if 
        allowed.
        """
        if self.is_row_selected():
            can_replace = (self.is_key_valid() and self.is_val_valid() 
                and self.is_val_different())
            if can_replace:
                self.replace_pair_in_list()
        else:
            can_add = (self.is_key_valid() and self.is_val_valid())
            if can_add:
                self.add_pair_to_list()

    def on_cell_clicked(self, row, col):
        """ 
        When a cell in the tableWidget is clicked, update keyLineEdit, 
        valueLineEdit, and tableWidget to select that key-value pair. 
        """
        self.ui.keyLineEdit.setText(self.ui.tableWidget.item(row, 0).text())
        self.ui.valueLineEdit.setText(self.ui.tableWidget.item(row, 1).text())
        self._on_row_selected(row, False)


    """ Protected Actions """

    def _reload_view(self):
        """ 
        Reloads the entire editor and populates it with the working list.
        """
        self.ui.tableWidget.clear()

        count = 0
        for k, v in self._working_list:
            self.ui.tableWidget.insertRow(count)
            self.ui.tableWidget.setItem(count, 0, QTableWidgetItem(k))
            self.ui.tableWidget.setItem(count, 1, QTableWidgetItem(v))
            count += 1

        self.ui.tableWidget.setRowCount(count)  
        self._on_working_list_updated()

    def _save(self):
        """
        Attemps to save the working list. This is the ONLY time where changes 
        are pushed to SymbolManager.
        """
        errors = self._sym_manager.update_and_save_symbol_list(
            self._working_list)
        
        if errors:
            if errors[0] == SymbolManager.ERR_INVALID_FORMAT:
                aqt.utils.showInfo(self._make_err_str_format(errors, 
                    'Changes will not be saved', 'Row'))
            elif errors[0] == SymbolManager.ERR_KEY_CONFLICT:
                aqt.utils.showInfo(self._make_err_str_duplicate(errors[1], 
                    'Changes will not be saved'))
            else:
                aqt.utils.showInfo("Error: Invalid key-value list to save. "
                    "Changes will not be saved.")
            return False
        return True


    """ Open & Close Actions """

    def open(self):
        """ Opens the editor and sets up the UI. """
        super(SymbolWindow, self).open()
        self._working_list = self._sym_manager.get_list()
        self._reload_view()

    def accept(self):
        """ Saves changes if possible, then closes the editor. """
        self._save()
        super(SymbolWindow, self).accept()

    def reject(self):
        """ Closes the editor without saving. """
        old_list = self._sym_manager.get_list()

        if old_list != self._working_list:
            confirm_msg = "Close without saving?"
            reply = QMessageBox.question(self, 'Message', confirm_msg, 
                QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                super(SymbolWindow, self).reject()
        else:
            super(SymbolWindow, self).reject()


    """ 
    Working List Update Actions 

    These functions update the working list and the UI, but does NOT push any 
    changes back to SymbolManager.
    """

    def _find_prospective_index(self, key):
        """ 
        Checks if the given key exists in the working list. If it does, returns 
        the index where the key can be found. If it does not, returns the index 
        where the key would be inserted.

        @return: (key_exists, index)
        """
        low, high = 0, len(self._working_list) - 1
        mid = 0

        while low <= high:
            mid = int((low + high) / 2)
            k = self._working_list[mid][0]

            if key == k:
                return (True, mid)
            elif k < key:
                low = mid + 1
                mid += 1
            else:
                high = mid - 1
        return (False, mid)

    def add_pair_to_list(self):
        """ 
        Adds an entry to the working list, performs validation, and then 
        updates the UI. 
        """
        if self.is_row_selected():
            aqt.utils.showInfo("Error: Cannot add entry when a row is "
                "already selected.")
            return

        new_key = self._get_key_text()
        new_val = self._get_val_text()

        has_conflict = SymbolManager.check_if_key_duplicate(new_key, 
            self._working_list)
        if has_conflict:
            aqt.utils.showInfo(("Error: Cannot add '%s' as a key with the same"
                " name already exists." % (new_key)))
            return

        (_, idx) = self._find_prospective_index(new_key)
        self._working_list.insert(idx, (new_key, new_val))

        self.ui.tableWidget.insertRow(idx)
        self.ui.tableWidget.setItem(idx, 0, QTableWidgetItem(new_key))
        self.ui.tableWidget.setItem(idx, 1, QTableWidgetItem(new_val))
        self._on_working_list_updated()

    def replace_pair_in_list(self):
        """ Replaces an existing key-value pair from the working list. """
        if not self.is_row_selected():
            aqt.utils.showInfo("Error: Cannot replace when no valid "
                "row is selected.")
            return

        new_val = self._get_val_text()
        old_pair = self._working_list[self._selected_row]

        self._working_list[self._selected_row] = (old_pair[0], new_val)

        widget_item = self.ui.tableWidget.item(self._selected_row, 1)
        widget_item.setText(new_val)
        self._on_working_list_updated()

    def delete_pair_from_list(self):
        """ Deletes an existing key-value pair from the working list. """
        if not self.is_row_selected():
            aqt.utils.showInfo("Error: Cannot delete when no valid "
                "row is selected.")
            return

        del self._working_list[self._selected_row]

        self.ui.tableWidget.removeRow(self._selected_row)
        self._on_working_list_updated()

    def reset_working_list(self):
        """ Resets the working list to the default symbol list. """
        confirm_msg = ("Load default symbols? This will delete any "
            "unsaved changes!")
        reply = QMessageBox.question(self, 'Message', confirm_msg, 
            QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self._working_list = self._sym_manager.get_default_list()
            self._reload_view()


    """ Import and Export Actions """

    def import_list(self):
        """ 
        Imports key-value pairs from a .txt file into the editor. The import 
        procedure is successful only if each and every entry in the .txt file 
        is valid; otherwise, an error will be displayed and the operation
        will abort.
        """
        if ANKI_VER == ANKI_VER_PRE_2_1_0:
            fname = QFileDialog.getOpenFileName(self, 'Open file', '', 
                "CSV (*.csv)")
        else:
            fname, _ = QFileDialog.getOpenFileName(self, 'Open file', '',
                "CSV (*.csv)")
        if not fname:
            return

        with io.open(fname, 'r', encoding='utf8') as file:
            reader = csv.reader(file)
            new_list = []

            for row in reader:
                new_list.append(row)

            if self._validate_imported_list(new_list):
                # Filter out empty lines before updating the list, but do so 
                # AFTER error checking so that accurate line numbers will be 
                # shown during error checking.
                new_list = [x for x in new_list if len(x) > 0]

                new_list = sorted(new_list, key=lambda x: x[0])
                self._working_list = new_list
                self._reload_view()

    def _validate_imported_list(self, new_list):
        """ 
        Checks that the imported file is valid, and displays an error message 
        if not. This function takes in a list that DOES contain empty lines 
        (which will be an empty list) so that accurate line numbers will be 
        displayed.
        """
        errors = SymbolManager.check_format(new_list, ignore_empty=True)
        if errors:
            aqt.utils.showInfo(self._make_err_str_format(errors, 
                'Unable to import', 'Line'))
            return False

        errors = SymbolManager.check_for_duplicates(new_list)
        if errors:
            aqt.utils.showInfo(self._make_err_str_duplicate(errors, 
                'Unable to import'))
            return False

        return True

    def export_list(self):
        """ 
        Exports the current symbol list into a .txt file. Before exporting, 
        the list displayed in the editor must match the symbol list stored 
        in the system. 
        """
        old_list = self._sym_manager.get_list()

        if old_list != self._working_list:
            confirm_msg = "You must save changes before exporting. Save now?"
            reply = QMessageBox.question(self, 'Message', confirm_msg, 
                QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                is_success = self._save()
                if is_success:
                    aqt.utils.showInfo('The symbol list has been saved.')
                else:
                    return
            else:
                return

        if ANKI_VER == ANKI_VER_PRE_2_1_0:
            fname = QFileDialog.getSaveFileName(self, 'Save file', '', 
                "CSV (*.csv)")
        else:
             fname, _ = QFileDialog.getSaveFileName(self, 'Save file', '', 
                "CSV (*.csv)")
        if not fname:
            return

        with io.open(fname, 'w', newline='\n', encoding='utf-8') as file:
            writer = csv.writer(file)
            for k, v in self._working_list:
                writer.writerow([k, v])
            aqt.utils.showInfo("Symbol list written to: " + fname)


    """ Error Strings """

    def _make_err_str_format(self, errors, op_desc, entry_type):
        """ 
        Creates an error message for format errors:

        @param op_desc: Which operation is being performed.
        @param entry_type: Either 'Line' or 'Row'
        """
        err_str = ("Error: %s due to incorrect format in the following lines "
            "(expecting <key> <value>).\n\n") % op_desc

        for i, string in errors:
            err_str += "%s %d: %s\n" % (entry_type, i, string)
        return err_str

    def _make_err_str_duplicate(self, errors, op_desc):
        """ 
        Creates an error message for key conflicts. 

        @param op_desc: Which operation is being performed.
        @param entry_type: Either 'Line' or 'Row'
        """
        err_str = ("Error: %s as the following duplicate keys "
            "were detected: \n\n" % op_desc)
            
        for key in errors:
            err_str += "%s\n" % key
        return err_str


    """ Validation Functions """

    def _check_table_widget_integrity(self):
        """ 
        Checks that the tableWidget displays the same items in the same order 
        as the working list. 
        """
        wl_len = len(self._working_list)
        tw_len = self.ui.tableWidget.rowCount()

        # Checks that tableWidget has same # of entries as the working list:
        if wl_len != tw_len:
            aqt.utils.showInfo(("Error: working list length %d does not match "
                "tableWidget length %d.") % (wl_len, tw_len))
            return

        # Checks that entries in the tableWidget & working list match:
        for i in range(wl_len):
            tw_k = self.ui.tableWidget.item(i, 0).text()
            tw_v = self.ui.tableWidget.item(i, 1).text()

            l_k = self._working_list[i][0]
            l_v = self._working_list[i][1]

            k_match = (tw_k == l_k)
            v_match = (tw_v == l_v)

            if not k_match or not v_match:
                err_str = ("Error: kv pair at row %d does not match.\n"
                    "List: %s, %s\nWidget: %s, %s") % (i, l_k, l_v, tw_k, tw_v)
                aqt.utils.showInfo(err_str)
                return

        # Checks that the tableWidget is displaying entries in alphabetical 
        # order by key:
        sorted_list = sorted(self._working_list, key=lambda x: x[0])
        has_error = False
        err_str = ""

        for i in range(wl_len):
            l_k = self._working_list[i][0]
            s_k = sorted_list[i][0]

            if l_k != s_k:
                has_error = True
                err_str += ("at row %d key is %s, but should be %s\n" 
                    % (i, l_k, s_k))

        if has_error:
            aqt.utils.showInfo("Error: list not alphabetical:" + err_str)

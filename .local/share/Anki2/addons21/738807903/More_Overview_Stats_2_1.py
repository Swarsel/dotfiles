# -*- coding: utf-8 -*-

"""
More Overview Stats 2.1
=====================
Statistics add-on for Anki 2.1 -- based on "More Overview Stats 2" by
Martin Zuther (http://www.mzuther.de/) which is based on
"More Overview Stats" by Calumks <calumks@gmail.com>

Copyright (c) 2021 Kazuwuqt <kazuwuqt@yahoo.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Thank you for using free software!
"""

from .config import AddonConfig
from .data import DeckData
from .table import Table
import os
from aqt import gui_hooks
from aqt.overview import Overview
from aqt.webview import AnkiWebView


def overview_table(self) -> str:
    """Generate the table for Anki's overview page.

    Fetches data of the currently active deck and presents it in a formatted
    table.

    Returns
    -------
    str
        The formatted overview table or an error string if the deck doesn't
        contain cards.
    """

    deck_data.refresh()

    if deck_data.is_empty_deck():
        return "<p>No cards found.</p>"

    return table.get_html()


def prepend_table(web: AnkiWebView) -> None:
    """Prepend the overview table to Anki's congrats dialog."""

    page_uri: str = os.path.basename(web.page().url().path())
    if page_uri != "congrats.html":
        return None

    html_style: str = """
    <style>
        #table {margin: 0 auto; display: table}
    </style>
    """

    # Need to check if id "table" already exists to avoid adding the table
    # multiple times because Anki can call the hook more than once
    web.eval(
        """
        if (document.getElementById("table") == null) {
            div = document.createElement("div");
            div.id = "table";
            div.innerHTML = `"""
        + html_style
        + overview_table(Overview)
        + """`;
            document.body.prepend(div);
        }
        """
    )


# Load addon config
config = AddonConfig()
# Initialize data manager
deck_data = DeckData(config=config)
# Initialize table manager
table = Table(config=config, deck_data=deck_data)

# Overwrite Anki's stats table
Overview._table = overview_table
# Inject overview table into Anki's congrats webview
try:
    gui_hooks.webview_did_inject_style_into_page.append(prepend_table)
except Exception as excp:
    print(excp)
    pass

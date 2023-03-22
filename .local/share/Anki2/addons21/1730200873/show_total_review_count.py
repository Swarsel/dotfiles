import anki
import aqt
from aqt import mw
from datetime import datetime
from anki.hooks import addHook, wrap
from aqt.deckbrowser import DeckBrowser

from .config import getUserOption, writeConfig

def generateStats():
	totalreviews = mw.col.db.scalar("""select count(id) from revlog""")
	totalreviews = str(totalreviews)
	
	styling = f"""
"font-family: {getUserOption('fontfamily')};
font-size: {getUserOption('fontsize')};
color: {getUserOption('color')};
"""
	if getUserOption('bold'):
		styling += " font-weight: bold;"

	styling += '"'
	sep = getUserOption('thousand_separator')
	if totalreviews == "0":
		string = f"<span style={styling}><br/>no reviews done yet</span>"
	else:
		reviews = '{:,}'.format(int(totalreviews)).replace(',', sep)
		before = getUserOption('message_before')
		after = getUserOption('message_after')
		string = f"<span style={styling}><br/>{before}{reviews}{after}</span>"
	return string

def renderStats(self, _old):
	return _old(self) + generateStats()

def db_wrc(deck_browser, content):
	content.stats += generateStats()

## code taken fro somebody else, who?
# for some reason it works offline, but not when adding it via ankiweb(order in which the plugin loads, probably)
# honestly no clue what this does but it fixes this problem, thanks glutanimate??
try:
	from aqt.gui_hooks import deck_browser_will_render_content
	deck_browser_will_render_content.append(db_wrc)
except (ImportError, ModuleNotFoundError):
	DeckBrowser._renderStats = wrap(DeckBrowser._renderStats, renderStats, 'around')


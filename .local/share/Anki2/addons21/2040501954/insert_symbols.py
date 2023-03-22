"""
This file is run when the plugin is first loaded. It contains functions to set 
up the plugin, open the symbol list editor, and broadcast symbol list updates
to editor windows that are open. 

Note: For debugging, use either sys.stderr.write() or aqt.utils.showInfo().
"""

import os
import sys

import aqt
from anki.hooks import addHook, wrap
from aqt import browser, editor, mw, reviewer
from aqt.editor import EditorWebView

from .browser_replacer import BrowserReplacer
from .get_version import *
from .symbol_manager import SymbolManager
from .symbol_window import SymbolWindow

""" Loads filenames based on Anki version  """

ANKI_VER = get_anki_version()

# Add-on path changed between Anki 2.0 and Anki 2.1
if ANKI_VER == ANKI_VER_PRE_2_1_0:
    sys_encoding = sys.getfilesystemencoding()
    ADDON_PATH = os.path.dirname(__file__).decode(sys_encoding)
else:
    ADDON_PATH = os.path.dirname(__file__)

# Webview requires different JS between Anki 2.1.40 and Anki 2.1.41
if ANKI_VER <= ANKI_VER_PRE_2_1_41:
    JS_FILE = "replacer_pre-2.1.41.js"
else:
    JS_FILE = "replacer.js"

""" Keeps track of all WebViews with symbol replacement Javascript. """
ins_sym_webviews = {
    "editors": [],
    "reviewer": None
}

def _update_JS(webview: EditorWebView):
    """ Updates the symbol list in the Javascript file. """
    json = mw.ins_sym_manager.get_JSON()
    webview.eval("insert_symbols.setMatchList(%s)" % json)

def _load_JS(webview: EditorWebView):
    """ 
    Loads replacer.js, the Javascript file which performs symbol replacement, 
    into the given WebView.
    """
    js_path = os.path.join(ADDON_PATH, JS_FILE)
    with open(js_path, 'r') as js_file:
        js = js_file.read()
        webview.eval(js)
        _update_JS(webview)

def update_symbols():
    """
    This function is called by SymbolManager whenever the symbol list is 
    updated. It updates the symbolList for every editor that is open.
    """
    for web in ins_sym_webviews['editors']:
        _update_JS(web)

    if ins_sym_webviews['reviewer']:
        _update_JS(ins_sym_webviews['reviewer'])

    mw.ins_sym_replacer.update_list(mw.ins_sym_manager.get_match_list())

""" 
Editor Actions 

These actions occur when an instance of the card editor defined in Anki's 
aqt/editor.py (ie. Add Card window, Card Browser, or Reviewer) is opened.
"""

def on_editor_set_note(self, note, hide=True, focus=False):
    """
    Anki calls Editor.setNote() when the Add Card window / Card Browser either 
    should show a note (NOTE = the note) or is closed (NOTE = None). Note that 
    SELF refers to Editor in aqt/editor.py.
    
    FYI: In Anki 2.1, focus=False becomes focusTo=None.
    """
    editor_webviews = ins_sym_webviews['editors']
    if note:
        if self.web not in editor_webviews:
            editor_webviews.append(self.web)
            #sys.stderr.write("Open Editors: " + str(len(editor_webviews)))
    else:
        if self.web in editor_webviews:
            editor_webviews.remove(self.web)
            #sys.stderr.write("Open Editors: " + str(len(editor_webviews)))

def on_editor_load_note(self, focusTo=None):
    """ 
    Anki calls Editor.loadNote() to refresh the editor's WebView, which occurs 
    after setNote(), onHtmlEdit(), and bridge() / onBridgeCmd() in Editor is 
    called. Editor.loadNote() resets Javascript code, so we must re-add our JS
    after every loadNote(). Note that SELF refers to Editor in aqt/editor.py.

    FYI: In Anki 2.1, 1) the focusTo=None argument is new and 2) there is now 
    a hook for loadNote().
    """
    _load_JS(self.web)

def on_reviewer_initweb(self):
    """
    Anki calls Reviewer._initWeb() to update the WebView, which occurs when the
    reviewer is first opened or after every 100 cards have been reviewed. Note
    that SELF refers to the Reviewer in aqt/reviewer.py.
    """
    ins_sym_webviews['reviewer'] = self.web
    _load_JS(self.web)
    # aqt.utils.showInfo("on_reviewer_start() called")

def on_reviewer_cleanup():
    """ This event is triggered when the Reviewer is about to be closed. """
    ins_sym_webviews['reviewer'] = None
    # aqt.utils.showInfo("on_reviewer_end() called")

def on_show_qa():
    """ 
    This event is triggered when the Reviewer shows either a question or an
    answer. Since the Editable Fields plugin makes the fields editable when 
    each card is created, key listeners need to be set up after each time.
    """
    webview = ins_sym_webviews['reviewer']
    if webview:
        webview.eval("insert_symbols.setupReviewerKeyEvents()")
    # aqt.utils.showInfo("on_show_qa() called")


""" 
Profile Loading Actions 

These actions occur when a new profile is opened. TOOD: Update all wrappers
to use the new Anki hooks.
"""

def on_profile_loaded():
    """ Perform setup when a new profile is loaded. """
    mw.ins_sym_manager = SymbolManager(mw, update_symbols)
    mw.ins_sym_manager.on_profile_loaded()

    mw.ins_sym_window = SymbolWindow(mw, mw.ins_sym_manager)
    mw.ins_sym_replacer = BrowserReplacer(mw.ins_sym_manager.get_match_list())

    # Add editor wrappers here so that if other plugins modify Editor.loadNote
    # this function will still work. There IS a hook for loadNote in Anki 2.1, 
    # but it doesn't exist in 2.0, so will keep using wrap() for consistency:
    editor.Editor.setNote = wrap(editor.Editor.setNote, 
        on_editor_set_note, 'after')
    editor.Editor.loadNote = wrap(editor.Editor.loadNote, 
        on_editor_load_note, 'after')

    # Add browser search bar wrappers:
    browser.Browser.__init__ = wrap(browser.Browser.__init__, 
        mw.ins_sym_replacer.on_browser_init, 'after')

    # Add reviewer wrappers:
    reviewer.Reviewer._initWeb = wrap(reviewer.Reviewer._initWeb, 
        on_reviewer_initweb, 'after')
    addHook("reviewCleanup", on_reviewer_cleanup)
    addHook("showQuestion", on_show_qa)
    addHook("showAnswer", on_show_qa)

addHook("profileLoaded", on_profile_loaded)

# Add menu button
open_action = aqt.qt.QAction("Insert Symbol Options...", mw, 
    triggered=lambda: mw.ins_sym_window.open())
mw.form.menuTools.addAction(open_action)

""" 
Debugging Functions 

Note: In Anki 2.1, the bridge() function in editor is renamed to onBridgeCmd().
"""

# def on_editor_bridge(self, string, _old=None):
# 	# Note: this doesn't quite work in Anki 2.1 yet
#     if string.startswith("debug_err"):
#         (_, value) = string.split(":", 1)
#         sys.stderr.write(value)
#     elif string.startswith("debug_div"):
#         (_, value) = string.split(":", 1)
#         self.web.eval('$(".debug").html("%s")' % value)

# if ANKI_VER == ANKI_VER_PRE_2_1_0:
#     editor.Editor.bridge = wrap(editor.Editor.bridge, 
#         on_editor_bridge, 'before')
# else:
#     editor.Editor.bridge = wrap(editor.Editor.onBridgeCmd, 
#         on_editor_bridge, 'before')

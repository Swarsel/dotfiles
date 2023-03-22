import re
import anki
from aqt.utils import tooltip, showInfo
try:
    from aqt.utils import (
            HelpPage,
            TR,
            tr,
            )
except:
    pass
from aqt.qt import *
from aqt import mw
try:
    from aqt.operations.card import set_card_deck
except:
    pass


def get_version():
    """Return the integer subversion of Anki on which the addon is run ("2.1.11" -> 11)"""
    return int(anki.version.split('.')[2])

def cs_editor_on_alt_cloze(self):
    self.saveNow(self.cs_u_onAltCloze, keepFocus=True)

def cs_editor_on_std_cloze(self):
    self.saveNow(self.cs_u_onStdCloze, keepFocus=True)

def cs_editor_generate_cloze(self, altModifier = False):
        # check that the model is set up for cloze deletion
    if not re.search('{{(.*:)*cloze:',self.note.model()['tmpls'][0]['qfmt']):
        if self.addMode:
            tooltip(_("Warning, cloze deletions will not work until "
                "you switch the type at the top to Cloze."))
        else:
            showInfo(_("""\
To make a cloze deletion on an existing note, you need to change it \
to a cloze type first, via Edit>Change Note Type."""))
            return
        # find the highest existing cloze
    highest = 0
    for name, val in list(self.note.items()):
        m = re.findall(r"\{\{c(\d+)::", val)
        if m:
            highest = max(highest, sorted([int(x) for x in m])[-1])
        # reuse last?
    if not altModifier:
        highest += 1
    highest = max(1, highest)
    self.web.eval("wrap('{{c%d::', '}}');" % highest)

#If the shortcut has "+++" in it for multiple duplications,
#Truncate the shortcut from that point to get the original name
def normalizeShortcutName(scut):
    prefix_idx = scut.find('+++')
    if scut.find('+++') != -1:
        # If the multiple duplicates "+++" is found,
        # truncate the shortcut to the proper name
        scut = scut[:prefix_idx]
    return scut

#Converts json shortcuts into functions for the reviewer
#sToF: shortcutToFunction
def review_sToF(self,scut):

    #"reviewer" is retained for copy-pastability, may be removed later
    #"self.mw.onEditCurrent" is exactly how it was in reviewer.py, DO NOT CHANGE
    sdict = {
        "reviewer edit current": self.mw.onEditCurrent,
        "reviewer flip card": self.onEnterKey,
        "reviewer flip card 1": self.onEnterKey,
        "reviewer flip card 2": self.onEnterKey,
        "reviewer flip card 3": self.onEnterKey,
        "reviewer options menu": self.onOptions,
        "reviewer record voice": self.onRecordVoice,
        "reviewer play recorded voice": self.onReplayRecorded,
        "reviewer play recorded voice 1": self.onReplayRecorded,
        "reviewer play recorded voice 2": self.onReplayRecorded,
        "reviewer delete note": self.onDelete,
        "reviewer suspend card": self.onSuspendCard,
        "reviewer suspend note": self.onSuspend,
        "reviewer bury card": self.onBuryCard,
        "reviewer bury note": self.onBuryNote,
        "reviewer mark card": self.onMark,
        "reviewer set flag 1": lambda: self.setFlag(1),
        "reviewer set flag 2": lambda: self.setFlag(2),
        "reviewer set flag 3": lambda: self.setFlag(3),
        "reviewer set flag 4": lambda: self.setFlag(4),
        "reviewer set flag 0": lambda: self.setFlag(0),
        "reviewer replay audio": self.replayAudio,
        "reviewer replay audio 1": self.replayAudio,
        "reviewer replay audio 2": self.replayAudio,
        "reviewer choice 1": lambda: self._answerCard(1),
        "reviewer choice 2": lambda: self._answerCard(2),
        "reviewer choice 3": lambda: self._answerCard(3),
        "reviewer choice 4": lambda: self._answerCard(4),
    }
    if get_version() >= 20:
        sdict["reviewer pause audio"] = self.on_pause_audio
        sdict["reviewer seek backward"] = self.on_seek_backward
        sdict["reviewer seek forward"] = self.on_seek_forward
    if get_version() >= 33:
        sdict["reviewer more options"] = self.showContextMenu
    if get_version() >= 41:
        sdict["reviewer set due date"] = self.on_set_due
    if get_version() >= 45:
        sdict["reviewer card info"] = self.on_card_info
        sdict["reviewer set flag 5"] = lambda: self.setFlag(5)
        sdict["reviewer set flag 6"] = lambda: self.setFlag(6)
        sdict["reviewer set flag 7"] = lambda: self.setFlag(7)
    if get_version() >= 48:
        sdict["reviewer previous card info"] = self.on_previous_card_info

    scut = normalizeShortcutName(scut)
    if scut in sdict:
        return sdict[scut]
    return None

#Converts json shortcuts into functions for the reviewer
#sToF: shortcutToFunction
def editor_sToF(self,scut):
    sdict = {
            "editor card layout": (self.onCardLayout, True),
            "editor bold": (self.toggleBold,),
            "editor italic": (self.toggleItalic,),
            "editor underline": (self.toggleUnderline,),
            "editor superscript": (self.toggleSuper,),
            "editor subscript": (self.toggleSub,),
            "editor remove format": (self.removeFormat,),
            "editor foreground": (self.onForeground,),
            "editor change col": (self.onChangeCol,),
            "editor cloze": (self.cs_onStdCloze,),
            "editor cloze alt": (self.cs_onAltCloze,),
            "editor add media": (self.onAddMedia,),
            "editor record sound": (self.onRecSound,),
            "editor insert latex": (self.insertLatex,),
            "editor insert latex equation": (self.insertLatexEqn,),
            "editor insert latex math environment": (self.insertLatexMathEnv,),
            "editor insert mathjax inline": (self.insertMathjaxInline,),
            "editor insert mathjax block": (self.insertMathjaxBlock,),
            "editor html edit": (self.onHtmlEdit,),
            "editor focus tags": (self.onFocusTags, True),
            "editor toggle sticky current": (self.csToggleStickyCurrent,),
            "editor toggle sticky all": (self.csToggleStickyAll,),


        }
    if get_version() >= 45:
        sdict.update({
            "editor html edit": (lambda:
                self.web.eval(
                    """{const currentField = getCurrentField(); if (currentField) { currentField.toggleHtmlEdit(); }}"""
                ), ),
            "editor block indent": (lambda:
                self.web.eval(
                    """ document.execCommand("indent"); """
                ), ),
            "editor block outdent": (lambda:
                self.web.eval(
                    """ document.execCommand("outdent") """
                ), ),
            "editor list insert unordered": (lambda:
                self.web.eval(
                    """ document.execCommand("insertUnorderedList"); """
                ), ),
            "editor list insert ordered": (lambda:
                self.web.eval(
                    """ document.execCommand("insertOrderedList"); """
                ), ),
                })

    scut = normalizeShortcutName(scut)
    if scut in sdict:
        return sdict[scut]
    return None

def editor_changeDeck(self):
        if not self.card:
            return
        from aqt.studydeck import StudyDeck
        cid = self.card.id
        did = self.card.did
        current = self.mw.col.decks.get(did)["name"]
        ret = StudyDeck(
                self.mw,
                current=current,
                accept=tr(TR.BROWSING_MOVE_CARDS),
                title=tr(TR.BROWSING_CHANGE_DECK),
                help=HelpPage.BROWSING,
                parent=self.mw,
                )
        if not ret.name:
            return
        did = self.mw.col.decks.id(ret.name)
        try:
            set_card_deck(parent=self.widget, card_ids=[cid], deck_id=did).run_in_background()
        except:
            self.mw.col.set_deck([cid], did)


#Performs a preliminary check for if any filter is saved before removing it
def remove_filter(self):
    name = self._currentFilterIsSaved()
    if name:
        self._onRemoveFilter()

#For reviewer shortcut assignments:
#Takes as input ls (the list of shortcuts, of the form (shortcut, function pointer))
#and replacements (a dict mapping function pointers to new shortcuts)
#Then, for every tuple in the list, if its function pointer has a replacement shortcut, replace it
#Changes the list in-place
def reviewer_find_and_replace_functions(ls, replacements):
    for i, val in enumerate(ls):
        func = val[1]
        if func in replacements:
            ls[i] = (replacements[func].pop(), func)
            if not replacements[func]:
                replacements.pop(func)

#For reviewer shortcut assignments:
#Takes as input ls (the list of shortcuts, of the form (shortcut, function pointer))
#and replacements (a dict mapping old shortcuts to new shortcuts)
#Then, for every tuple in the list, if its shortcut is in the list, replace it
#Changes the list in-place
#Prefer reviewer_find_and_replace_functions to this because functions are less fragile
def reviewer_find_and_replace_scuts(ls, replacements):
    for i, val in enumerate(ls):
        scut = val[0]
        if scut in replacements:
            ls[i] = (replacements.pop(scut), val[1])

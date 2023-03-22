# -*- coding: utf-8 -*-
#
# Fastbar with nightmode support: an Anki 2.1 add-on adds a toolbar and toggle the sidebar
# in the Card Browser of Anki 2.1.
#
# GitHub: https://github.com/AnKingMed/Fastbar-with-nightmode-support
# 
# License: GNU AGPL, version 3 or later; http://www.gnu.org/copyleft/agpl.html
#
# Copyright: 2017 Luminous Spice <luminous.spice@gmail.com>
#                  (https://github.com/luminousspice/anki-addons/)
#            2020+ ijgnd
#            2020+ The AnKing (https://www.ankingmed.com/)
#
#
# Third party softwares used with Fastbar:
#     QtAwesome 1.1.1 (slightly modified for this add-on)
#         Copyright © 2015–2021 Spyder Project Contributors
#         Released under the MIT License.
#         https://github.com/spyder-ide/qtawesome/blob/master/LICENSE.txt
#         The Font Awesome is licensed under the SIL Open Font License.



def get_anki_version():
    try:
        # 2.1.50+ because of bdd5b27715bb11e4169becee661af2cb3d91a443, https://github.com/ankitects/anki/pull/1451
        from anki.utils import point_version
    except:
        try:
            # introduced with 66714260a3c91c9d955affdc86f10910d330b9dd in 2020-01-19, should be in 2.1.20+
            from anki.utils import pointVersion
        except:
            # <= 2.1.19
            from anki import version as anki_version
            return int(anki_version.split(".")[-1]) 
        else:
            return pointVersion()
    else:
        return point_version()
anki_21_version = get_anki_version()


from aqt.qt import (
    QAction,
    QMenu,
    QSize,
    QToolBar,
    Qt,
)

from aqt import mw
if anki_21_version >= 24:
    from aqt import gui_hooks

from aqt.forms.browser import Ui_Dialog
from aqt.browser import Browser

if anki_21_version >= 45:
    from aqt.utils import ensure_editor_saved, skip_if_selection_is_empty, tooltip

if anki_21_version >=45:
    from aqt.operations.scheduling import (
        bury_cards,
    )
if anki_21_version >=50:
    from aqt.operations.scheduling import (
        unbury_cards,
    )
from anki.utils import ids2str
from anki.hooks import addHook, wrap


from . import qtawesome as qta


def gc(arg, fail=False):
    conf = mw.addonManager.getConfig(__name__)
    if conf:
        return conf.get(arg, fail)
    return fail


def maybe_import_other_addon(addon_id):
    try: 
        a = __import__(addon_id)
    except ModuleNotFoundError:
        return None
    else:
        return a


def check_other_addons():
    global BetterSearchAddon
    global ExtendedTagAddon
    BetterSearchAddon = maybe_import_other_addon("1052724801")  # BetterSearch
    ExtendedTagAddon = maybe_import_other_addon("1135507717")  # Extended Tag Add/Edit Dialog
if anki_21_version >= 24:
    gui_hooks.profile_did_open.append(check_other_addons)
else:
    addHook('profileLoaded', check_other_addons)


if anki_21_version < 20:
    class Object():
        pass
    theme_manager = Object()
    theme_manager.night_mode = False
else:
    from aqt.theme import theme_manager


night_mode_on = False
def refresh_night_mode_state(nm_state):
    global night_mode_on
    if gc("switch to dark theme when add-on night mode is enabled"):
        night_mode_on = nm_state
addHook("night_mode_state_changed", refresh_night_mode_state)


night_mode_stylesheet = """
QToolBar { 
    background-color: #272828!important;
    background: #272828!important;
    spacing: 0px;
    color:  #272828!important;
    border: 0px;
}
QToolBar::separator{
    border: 0px solid #272828!important;
    background-color: #272828!important;
    background: #272828!important;
    margin-left: 0px;
    margin-right: 0px;
    width: 1px;
}
QToolButton {
    border: 0px solid #272828;
    border-radius: 0px;
    background-color: #272828;
    background: #272828!important;
    color:  #d7d7d7;
    margin-left: 0px;
    margin-right: 0px;
}    
QToolBar::handle {
    color: #272828;
    background:#272828;
    background-color: #272828;
}
QMacToolBar {
    border: 0px solid #272828!important;
    background-color: #272828!important;
    background: #272828!important;
    color: #272828!important;   
    spacing:0px;             
}
"""



def isBuried__pre_45(self):  # self is browser
    if mw.col.schedVer() == 1:
        return not not (self.card and self.card.queue == -2)
    if mw.col.schedVer() in [2, 3]:
        return not not (self.card and self.card.queue in [-2, -3])


def _onBury__pre_45(self):  # self is browser
    bur = not isBuried__pre_45(self)
    c = self.selectedCards()
    if bur:
        self.col.sched.buryCards(c)
    else:
        self.col.sched.unbury_cards(c)
    self.model.reset()
    self.mw.requireReset()


def onBury(self):  # self is browser
    if anki_21_version < 45:
        self.editor.saveNow(lambda b=self: _onBury__pre_45(b))
    elif anki_21_version < 58:
        _onBury_45(self)
    else:
        _onBury_58(self)



if anki_21_version >= 45:
    # in 2.1.50 beta2 Anki added a new unbury function, see cad0c64
    # see https://github.com/ankitects/anki/commit/cad0c64105b5b41cbcba405a1dea7327de75a45a
    # so for versions 45-49 I have to build it myself.
    if anki_21_version < 50:
        ## modeled after aqt.operations.scheduling.bury_cards
        from typing import Sequence
        from aqt.qt import QWidget
        from aqt.operations import CollectionOp
        from anki.cards import CardId
        from anki.collection import (
            OpChangesWithCount,
        )
        def unbury_cards(
            *,
            parent: QWidget,
            card_ids: Sequence[CardId],
        ) -> CollectionOp[OpChangesWithCount]:
            return CollectionOp(parent, lambda col: col.sched.unbury_cards(card_ids))


    def all_cards_buried(self, cid_list):  # self is browser
        for c in cid_list:
            card = self.mw.col.get_card(c)
            if mw.col.sched_ver() == 1:
                if not card.queue == -2:
                    return
            else:
                if not card.queue in [-2, -3]:
                    return
        return True


    @skip_if_selection_is_empty
    @ensure_editor_saved
    def _onBury_45(self):  # self is browser
        c = self.selected_cards()
        if not all_cards_buried(self, c):
            bury_cards(parent=self.mw, card_ids=c,).success(lambda res: tooltip(f"buried {res.count} cards")).run_in_background()
        else:
            unbury_cards(parent=self.mw, card_ids=c,).success(lambda res: tooltip("unburied cards")).run_in_background()


if anki_21_version >= 58:
    # this uses thew newly introduced method bury_selected_cards from commit 77bba53 from 2023-01-30
    def _onBury_58(self):  # self is browser
        c = self.selected_cards()
        if not all_cards_buried(self, c):
            self.bury_selected_cards(True)
        else:
            self.bury_selected_cards(False)





def sidebar_toggle(self):
    new_state = False if self.sidebarDockWidget.isVisible() else True
    self.sidebarDockWidget.setVisible(new_state)


def fastbar_toggle(self):
    self.fbar.toggleViewAction().trigger()


def make_and_add_toolbar(self):  # self is browser
    fbar = QToolBar("Fastbar")
    fbar.setObjectName("Fastbar")
    fbar.setIconSize(QSize(15, 15))
    fbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

    self.form.actionToggle_Sidebar.triggered.connect(lambda _, b=self: sidebar_toggle(b))
    self.form.actionToggle_Bury.triggered.connect(lambda _, b=self: onBury(b))
    self.form.actionToggle_Fastbar.triggered.connect(lambda _,b=self: fastbar_toggle(b))

    self.form.actionDelete.setText("Delete Note")

    all_actions = gc("sidebar_actions")
    if not all_actions:  # if no user config provided use the default
        all_actions = [
            ["actionToggle_Fastbar", "ei.remove-sign"],
            ["actionToggle_Sidebar", "fa.exchange"],
            ["actionAdd", "fa.plus-square"],
            ["action_Info", "fa.info-circle"],
            ["actionToggle_Mark", "fa.star"],
            ["actionToggle_Suspend", "fa.pause-circle"],
            ["actionToggle_Bury", "fa.step-backward"],
            ["actionChange_Deck", "fa.inbox"],
            ["actionChangeModel", "fa.leanpub"],
            ["actionAdd_Tags", "fa.tag"],
            ["actionRemove_Tags", "fa.eraser"],
            ["actionClear_Unused_Tags", "fa.magic"],
            ["actionDelete", "fa.trash-o"],
            ["addon_extended_tag", "fa.tags"],
            ["addon_bettersearch", "fa.search-plus"],
            ["action_reschedule_set_due_date", "fa.history"],
            ["actionReposition", "fa.sign-in"],
        ]
    # maybe remove add-on actions and set commands used according to your anki verison
    for idx, act_list in enumerate(all_actions):
        if act_list[0] == "action_reschedule_set_due_date":
            all_actions[idx] = ["actionReschedule" if anki_21_version < 41 else "action_set_due_date", act_list[1]]
        if act_list[0] == "addon_extended_tag":
            if hasattr(self, "ExTaDiAction"):
                all_actions[idx] = [self.ExTaDiAction, act_list[1]]
        if act_list[0] == "addon_bettersearch":
            if hasattr(self, "BeSeAction"):
                all_actions[idx] = [self.BeSeAction, act_list[1]]

    for idx, val in enumerate(all_actions):
        action_name, icon_name = val

        if isinstance(action_name, str):
            action = getattr(self.form, action_name, None)
        else:
            action = action_name

        if action is None:
            continue
        if gc("enable compact mode"):
            # TODO: Create custom QToolBar widget to handle word-wrapping
            # properly
            action_text = action.text()
            if " " in action_text:
                word_wrapped_text = action_text.replace(" ", "\n", 1)
            else:
                # hacky way to align single-line labels
                # "\n" contains an invisible space, since qt strips tailing whitespace
                word_wrapped_text = action_text + "\n‎"
            action.setText(word_wrapped_text)
        icon = qta.icon(icon_name, color="white" if night_mode_on or theme_manager.night_mode else "black")  
        action.setIcon(icon)
        fbar.addAction(action)
        # if idx != len(all_actions)-1:  # python uses zero-based indexing
        #     tb.addSeparator()

    if night_mode_on:
        fbar.setStyleSheet(night_mode_stylesheet)
    else:
        # border: 0px; is needed for correct background color in MacOS
        fbar.setStyleSheet("QToolBar{spacing:0px; border: 0px;}")
    self.addToolBar(fbar)  # addToolBar is a method of QMainWindow (that the Browser inherits from)
    self.fbar = fbar
    if gc("do not show by default"):
        self.fbar.setVisible(False)


# taken from https://github.com/AnKingMed/Study-Timer/commit/c3d89949c6523fd4f51121e2dc2ff0fffab5f202
def getMenu(parent, menuName):
    menubar = parent.form.menubar
    for a in menubar.actions():
        if menuName == a.text():
            return a.parent()
    else:
        return menubar.addMenu(menuName)


def onSetupMenus(self):
    def createQAction(objname, text):
        out = QAction(self)
        out.setObjectName(objname)
        out.setText(text)
        return out

    self.form.actionToggle_Sidebar = createQAction("toggleSidebar", "Toggle Sidebar")
    self.form.actionToggle_Bury = createQAction("toggleBury", "Toggle Bury")
    self.form.actionToggle_Fastbar = createQAction("toggleFastbar", "Toggle Fastbar")

    if anki_21_version < 58:
        self.form.menu_Cards.addSeparator()
        self.form.menu_Cards.addAction(self.form.actionToggle_Bury)
    
    menu_view = getMenu(self, "&View")
    if not hasattr(self, "menuView"):
        self.menuView = menu_view
    menu_view.addSeparator()
    menu_view.addAction(self.form.actionToggle_Sidebar)
    menu_view.addAction(self.form.actionToggle_Fastbar)


if anki_21_version >= 24:
    gui_hooks.browser_menus_did_init.append(onSetupMenus)
    gui_hooks.browser_will_show.append(make_and_add_toolbar)
else:
    def old_browser_setup_helper(self):
        onSetupMenus(self)
        make_and_add_toolbar(self)
    addHook("browser.setupMenus", old_browser_setup_helper)

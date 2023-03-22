# -*- coding: utf-8 -*-
# See github page to report issues or to contribute:
# https://github.com/hssm/advanced-browser
from anki.cards import Card
from anki.consts import *
from anki.hooks import addHook, remHook
from aqt.utils import tr
from anki.utils import intTime
from aqt.utils import askUser


class InternalFields:

    def __init__(self):
        self.noteColumns = []
        self.cardColumns = []

    def onBuildContextMenu(self, contextMenu):
        nGroup = contextMenu.newSubMenu("- Note (internal) -")
        cGroup = contextMenu.newSubMenu("- Card (internal) -")

        for cc in self.noteColumns:
            nGroup.addItem(cc)
        for cc in self.cardColumns:
            cGroup.addItem(cc)

    def onAdvBrowserLoad(self, advBrowser):
        """Called when the Advanced Browser add-on has finished
        loading. Create and add all custom columns owned by this
        add-on here.

        """

        # Clear existing state
        self.noteColumns = []
        self.cardColumns = []

        def setData(c: Card, value: str):
            try:
                value = int(value)
            except ValueError:
                return False
            if not askUser(_("Do you really want to change the id of the note ? This may create problems during synchronisation if the note has been modified on another computer.")):
                return False
            old_nid = c.nid
            n = c.note()
            cards = n.cards()
            n.id = value
            n.flush()
            for card in cards:
                card.nid = value
                card.flush()
            c.col._remNotes([old_nid])
            return True

        cc = advBrowser.newCustomColumn(
            type="nid",
            name="Note ID",
            onData=lambda c, n, t: str(n.id),
            onSort=lambda: "n.id asc nulls last",
            setData=setData,
        )
        self.noteColumns.append(cc)

        def setData(c: Card, value: str):
            if not askUser(_("Do you really want to change the globally unique id of the note ? This may create problems during synchronisation if the note has been modified on another computer.")):
                return False
            n = c.note()
            n.guid = value
            n.flush(mod=intTime())
            return True

        cc = advBrowser.newCustomColumn(
            type="nguid",
            name="Note Guid",
            onData=lambda c, n, t: str(n.guid),
            onSort=lambda: "n.guid asc nulls last",
            setData=setData,
        )
        self.noteColumns.append(cc)

        cc = advBrowser.newCustomColumn(
            type="nmid",
            name="Model ID",
            onData=lambda c, n, t: str(n.mid),
            onSort=lambda: "n.mid asc nulls last"
        )
        self.noteColumns.append(cc)

        def setData(c: Card, value: str):
            try:
                value = int(value)
            except ValueError:
                return False
            c.col.db.execute("update cards set usn=? where id=?", value, c.id)
            
        cc = advBrowser.newCustomColumn(
            type="nusn",
            name="Note USN",
            onData=lambda c, n, t: str(n.usn),
            onSort=lambda: "n.usn asc nulls last",
            setData=setData,
        )
        self.noteColumns.append(cc)

        def setData(c: Card, value: str):
            n = c.note()
            fields = value.split(u"\u25A0")
            if len(fields) != len(n.fields):
                return False
            n.fields = fields
            n.flush()
            advBrowser.editor.loadNote()
            return True

        cc = advBrowser.newCustomColumn(
            type="nfields",
            name="Note Fields",
            onData=lambda c, n, t: u"\u25A0".join(n.fields),
            onSort=lambda: "n.flds asc nulls last",
            setData=setData,
        )
        self.noteColumns.append(cc)

        cc = advBrowser.newCustomColumn(
            type="nflags",
            name="Note Flags",
            onData=lambda c, n, t: n.flags,
            onSort=lambda: "n.flags asc nulls last"
        )
        self.noteColumns.append(cc)

        cc = advBrowser.newCustomColumn(
            type="ndata",
            name="Note Data",
            onData=lambda c, n, t: n.data,
            onSort=lambda: "n.data asc nulls last"
        )
        self.noteColumns.append(cc)

        def setData(c: Card, value: str):
            try:
                value = int(value)
            except ValueError:
                return False
            if not askUser(_("Do you really want to change the id of the card ? This may create problems during synchronisation if the note has been modified on another computer.")):
                return False
            old_cid = c.id
            c.id = value
            c.flush()
            c.col.remCards([old_cid], notes=False)
            c.col.db.execute(
                "update revlog set cid = ?, usn=? where cid = ?", value, c.col.usn(), old_cid)
            return True

        cc = advBrowser.newCustomColumn(
            type="cid",
            name="Card ID",
            onData=lambda c, n, t: str(c.id),
            onSort=lambda: "c.id asc nulls last",
            setData=setData,
        )
        self.cardColumns.append(cc)

        def setData(c: Card, value: str):
            new_deck = c.col.decks.get(value, default=False)
            if new_deck is None:
                return False
            old_deck = c.col.decks.get(c.did)
            if new_deck["dyn"] == DECK_DYN and old_deck["dyn"] == DECK_STD:
                # ensuring that if the deck is dynamic, then a
                # standard odid is set
                c.col.sched._moveToDyn(new_deck["id"], [c.id])
            else:
                c.did = new_deck["id"]
                if new_deck["dyn"] == DECK_STD and old_deck["dyn"] == DECK_DYN:
                    # code similar to sched.emptyDyn
                    if c.type == CARD_TYPE_LRN:
                        c.queue = QUEUE_TYPE_NEW
                        c.type = CARD_TYPE_NEW
                    else:
                        c.queue = c.type
                    c.due = c.odue
                    c.odue = 0
                    c.odid = 0
                c.flush()
            return True

        cc = advBrowser.newCustomColumn(
            type="cdid",
            name="Deck ID",
            onData=lambda c, n, t: str(c.did),
            onSort=lambda: "c.did asc nulls last",
            setData=setData,
        )
        self.cardColumns.append(cc)

        def setData(c: Card, value: str):
            if not c.odid:
                # only accept to change odid if there is already one
                return False
            deck = c.col.decks.get(value, default=False)
            if deck is None:
                return False
            if deck["dyn"] == DECK_DYN:
                return False
            c.flush()
            return True

        cc = advBrowser.newCustomColumn(
            type="codid",
            name="Original Deck ID",
            onData=lambda c, n, t: str(c.odid),
            onSort=lambda: "c.odid asc nulls last",
            setData=setData,
        )
        self.cardColumns.append(cc)

        def setData(c: Card, value: str):
            try:
                value = int(value)
            except ValueError:
                return False
            n = c.note()
            m = n.note_type()
            if value < 0:
                return False
            if m["type"] == MODEL_STD and value >= len(m["tmpls"]):
                # only accept values of actual template
                return False
            if not askUser(_("Do you really want to change the ord of the card ? The card may be empty, or duplicate, unless you know exactly what you do.")):
                return False
            c.ord = value
            return True

        cc = advBrowser.newCustomColumn(
            type="cord",
            name="Card Ordinal",
            onData=lambda c, n, t: str(c.ord),
            onSort=lambda: "c.ord asc nulls last",
            setData=setData,
        )
        self.cardColumns.append(cc)

        def setData(c: Card, value: str):
            try:
                value = int(value)
            except ValueError:
                return False
            c.col.db.execute("update cards set usn=? where id=?", value, c.id)

        cc = advBrowser.newCustomColumn(
            type="cusn",
            name="Card USN",
            onData=lambda c, n, t: str(c.usn),
            onSort=lambda: "c.usn asc nulls last",
            setData=setData,
        )
        self.cardColumns.append(cc)

        def setData(c: Card, value: str):
            try:
                value = int(value)
                if not 0 <= value <= 3:
                    return False
            except ValueError:
                value = {"new": 0, "lrn": 1, "rev": 2,
                         "relearning": 3}.get(value.strip().lower())
                if value is None:
                    return False
            if not askUser(_("Do you really want to change the card type of the card ? Values may be inconsistents if you don't change the queue type, due value, etc....")):
                return False
            c.type = value
            c.flush()
            return True

        cc = advBrowser.newCustomColumn(
            type="ctype",
            name="Card Type",
            onSort=lambda: "c.type asc nulls last",
            onData=lambda c, n, t: {
                0: tr(TR.ACTIONS_NEW),
                1: "Lrn", # transalation missing
                2: "Rev", # transalation missing
                3: tr(TR.STATISTICS_COUNTS_RELEARNING_CARDS),
            }.get(c.type, c.type),
        )
        self.cardColumns.append(cc)

        def setData(c: Card, value: str):
            try:
                value = int(value)
                if not -3 <= value <= 4:
                    # 4 should not occur with V1
                    return False
            except ValueError:
                value = {"manually buried": -3, "sibling buried": -2, "suspended": -1, "new": 0,
                         "lrn": 1, "rev": 2, "day learn relearn": 3, "preview": 4}.get(value.strip().lower())
                if value is None:
                    return False
            if not askUser("Do you really want to change the queue type of the card ? Values may be inconsistents if you don't change the card type, due value, etc...."): # transalation missing
                return False
            c.type = value
            c.flush()
            return True

        cc = advBrowser.newCustomColumn(
            type="cqueue",
            name="Card Queue",
            onData=lambda c, n, t: {
                -3: tr(TR.STUDYING_MANUALLY_BURIED_CARDS),
                -2: tr(TR.STUDYING_BURIED_SIBLINGS),
                -1: tr(TR.BROWSING_SUSPENDED),
                0: tr(TR.ACTIONS_NEW),
                1: "Lrn", # transalation missing
                2: "Rev", # transalation missing
                3: "Day learn relearn", # transalation missing
                4: tr(TR.CARD_TEMPLATES_PREVIEW_BOX),
            }.get(c.queue, c.queue),
            onSort=lambda: "c.queue asc nulls last",
            setData=setData,
        )
        self.cardColumns.append(cc)

        def setData(c: Card, value: str):
            try:
                value = int(value)
            except ValueError:
                return False
            c.left = value
            return True

        cc = advBrowser.newCustomColumn(
            type="cleft",
            name="Card Left",
            onData=lambda c, n, t: str(c.left),
            onSort=lambda: "c.left asc nulls last",
            setData=setData,
        )
        self.cardColumns.append(cc)

        def setData(c: Card, value: str):
            try:
                value = int(value)
            except ValueError:
                return False
            if not askUser("Do you really want to change the original due. If the card is not already in a filtered deck, or moved to one, it may creates unexpected effect."): # Translation missing
                return False
            c.odue = value
            c.flush()
            return True

        cc = advBrowser.newCustomColumn(
            type="codue",
            name="Card Original Due",
            onData=lambda c, n, t: str(c.odue),
            onSort=lambda: "c.odue asc nulls last",
            setData=setData,
        )
        self.cardColumns.append(cc)



iff = InternalFields()

# -*- coding: utf-8 -*-
# See github page to report issues or to contribute:
# https://github.com/hssm/advanced-browser

# Built-in columns which are not sortable by default are made sortable here.
#
# Question/Answer columns are too slow so they are not handled.
# Note: the onData function of the columns is None as the data will still
# be fetched from the original source and that function is never reached.

from anki.cards import Card
from anki.consts import *
from anki.hooks import addHook
from aqt.utils import tr
from aqt.utils import askUser


class BasicFields:

    def onAdvBrowserLoad(self, advBrowser):
        """Called when the Advanced Browser add-on has finished
        loading. Create and add all custom columns owned by this
        module."""

        # Store a list of CustomColumns managed by this module. We later
        # use this to build our part of the context menu.
        self.customColumns = []

        def setData(c: Card, value: str):
            n = c.note()
            m = n.note_type()
            if m["type"] == MODEL_CLOZE:
                tmpl = m["tmpls"][0]
                tmpl_name = tmpl["name"]
                if not value.startswith(tmpl_name):
                    return False
                value = value[len(tmpl_name):]
                try:
                    c.ord = int(value)-1
                except ValueError:
                    return False
            else:
                value = value.strip().lower()
                right_tmpl = None
                for tmpl in m["tmpls"]:
                    if tmpl["name"].strip().lower() == value:
                        right_tmpl = tmpl
                        break
                if right_tmpl is None:
                    return False
                c.ord = right_tmpl["ord"]
            c.flush()
            return True

        def sortTableFunction():
            col = advBrowser.mw.col
            col.db.execute("drop table if exists tmp")
            col.db.execute("create temporary table tmp (mid int, ord int, v text, primary key (mid, ord)) without rowid;")

            for model in col.models.all():
                templates = model['tmpls']
                for template in templates:
                    ord = template['ord']
                    if model['type'] == MODEL_CLOZE:
                        name = templates[0]['name'] + f" {ord + 1}"
                    else:
                        name = template['name']

                    advBrowser.mw.col.db.execute(
                        "insert into tmp values (?,?,?)", model['id'], ord, name
                    )

        cc = advBrowser.newCustomColumn(
            type="template",
            name="Card",
            onData=None,
            sortTableFunction=sortTableFunction,
            onSort=lambda: "(select v from tmp where mid = n.mid and ord = c.ord) collate nocase asc",
            setData=setData,
        )
        self.customColumns.append(cc)

        def setData(c: Card, value: str):
            n = c.note()
            n.setTagsFromStr(value)
            n.flush()
            advBrowser.editor.loadNote()
            return True

        cc = advBrowser.newCustomColumn(
            type="noteTags",
            name="Tags",
            onData=None,
            onSort=lambda: "(case when trim(n.tags) = '' then null else n.tags end) asc nulls last",
            setData=setData,
        )
        self.customColumns.append(cc)

        def sortTableFunction():
            col = advBrowser.mw.col
            col.db.execute("drop table if exists tmp")
            col.db.execute("create temp table tmp (k int primary key, v text)")
            for model in col.models.all():
                advBrowser.mw.col.db.execute(
                    "insert into tmp values (?,?)", model['id'], model['name']
                )

        cc = advBrowser.newCustomColumn(
            type="note",
            name="Note",
            onData=None,
            sortTableFunction=sortTableFunction,
            onSort=lambda: "(select v from tmp where k = n.mid) collate nocase asc",
        )
        self.customColumns.append(cc)

        def sortTableFunctionDeckName():
            col = advBrowser.mw.col
            col.db.execute("drop table if exists tmp")
            col.db.execute("create temp table tmp (k int primary key, v text)")
            for deck in col.decks.all():
                advBrowser.mw.col.db.execute(
                    "insert into tmp values (?,?)", deck['id'], deck['name']
                )
        cc = advBrowser.newCustomColumn(
            type="deck",
            name="Deck",
            onData=None,
            sortTableFunction=sortTableFunctionDeckName,
            onSort=lambda: "(select v from tmp where k = c.did) collate nocase asc",
        )
        self.customColumns.append(cc)

        def setData(c: Card, value: str):
            value = value.strip()
            if value.endswith("%"):
                value = value[:-1]
            try:
                f = float(value)
            except ValueError:
                return False
            c.factor = f * 10
            c.flush()
            return True

        cc = advBrowser.newCustomColumn(
            type="cardEase",
            name="Ease",
            onData=None,
            onSort=lambda: f"(case when type = {CARD_TYPE_NEW} then null else factor end) asc nulls last",
            setData=setData,
        )
        self.customColumns.append(cc)

        # fixme: to sort on this column, will need to write to a temp table
        # then sort based on that table, like in Anki's Rust code

        def setData(c: Card, value: str):
            if not c.odid:
                # only accept to change odid if there is already one
                return False
            new_deck = c.col.decks.byName(value)
            if new_deck is None:
                if not askUser(
                        "%s does not exists, do you want to create this deck ?" % value, # Translation missing
                        parent=advBrowser,
                        defaultno=True):
                    return False
                new_id = c.col.decks.id(value)
                new_deck = c.col.decks.get(new_id)
            if new_deck["dyn"] == DECK_DYN:
                return False
            c.odid = new_deck["id"]
            c.flush()
            return True

        cc = advBrowser.newCustomColumn(
            type="odeck",
            name="Original Deck",
            onData=lambda c, n, t: advBrowser.mw.col.decks.name(c.odid),
            sortTableFunction=sortTableFunctionDeckName,
            onSort=lambda: "(select v from tmp where k = c.odid) collate nocase asc nulls last",
            setData=setData,
        )
        self.customColumns.append(cc)

    def onBuildContextMenu(self, contextMenu):
        for cc in self.customColumns:
            contextMenu.addItem(cc)


bf = BasicFields()
addHook("advBrowserLoaded", bf.onAdvBrowserLoad)
addHook("advBrowserBuildContext", bf.onBuildContextMenu)

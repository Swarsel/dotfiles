# -*- coding: utf-8 -*-
# See github page to report issues or to contribute:
# https://github.com/hssm/advanced-browser
import re
from anki.cards import Card
from anki.hooks import addHook
from anki.utils import pointVersion
from aqt import *
from aqt.utils import showWarning

from .config import getEachFieldInSingleList


class NoteFields:

    def onAdvBrowserLoad(self, advBrowser):
        # Dictionary of field names indexed by "type" name. Used to
        # figure out if the requested column is a note field.
        # {type -> name}
        self.fieldTypes = {}

        # Dictionary of dictionaries to get position for field in model.
        # We build this dictionary once to avoid needlessly finding the
        # field order for every single row when sorting. It's
        # significantly faster that way.
        # {mid -> {fldName -> pos}}
        self.modelFieldPos = {}

        # Dictionary of columns. A column can exist in multiple places, because
        # different note types may have the same field name.
        # {fld['name'] -> CustomColumn}}
        self.customColumns = {}

        self.fieldsToMidOrdPairs = {}

        self.advBrowser = advBrowser
        self.buildMappings()

    def onBuildContextMenu(self, contextMenu):
        # Models might have changed so rebuild our mappings.
        # E.g., a field or note type could have been deleted.
        self.buildMappings()

        # Create a new sub-menu for our columns
        fldGroup = contextMenu.newSubMenu(" - Fields -")
        if getEachFieldInSingleList():
            # And an option for each fields
            for model in mw.col.models.all():
                for fld in model['flds']:
                    fldGroup.addItem(self.customColumns[fld['name']])
        else:
            # And a sub-menu for each note type
            for model in mw.col.models.all():
                modelGroup = fldGroup.newSubMenu(model['name'])
                for fld in model['flds']:
                    modelGroup.addItem(self.customColumns[fld['name']])

    def buildMappings(self):
        self.fieldsToMidOrdPairs = {}
        for model in mw.col.models.all():
            # For some reason, some mids return as unicode, so convert to int
            mid = int(model['id'])
            # And some platforms get a signed 32-bit integer from SQlite, so
            # we will also provide an index to that as a workaround.
            mid32 = (mid + 2**31) % 2**32 - 2**31
            self.modelFieldPos[mid] = {}
            self.modelFieldPos[mid32] = {}
            # For each field in this model, store the ordinal of the
            # field with the field name as the key.
            for field in model['flds']:
                name = field['name']
                ord = field['ord']
                type = "_field_"+name  # prefix to avoid potential clashes
                self.modelFieldPos[mid][name] = ord
                self.modelFieldPos[mid32][name] = ord
                if type not in self.fieldTypes:  # avoid dupes
                    self.fieldTypes[type] = name
                self.fieldsToMidOrdPairs.setdefault(
                    name, []).append((mid, ord))

        def fldOnData(c, n, t):
            field = self.fieldTypes[t]
            if field in c.note().keys():
                return NoteFields.htmlToTextLine(c.note()[field])

        def setData_(name):
            def setData(c: Card, value: str):
                n = c.note()
                m = n.note_type()
                if not name in n:
                    showWarning(_("""The field "%s" does not belong to the note type "%s".""") % (
                        name, m["name"]))
                    return False
                self.advBrowser.editor.loadNote()
                n[name] = value
                return True
            return setData

        for type, name in self.fieldTypes.items():
            if name not in self.customColumns:
                def sortTableFunction(name=name):
                    col = mw.col
                    vals = []
                    col.db.execute("drop table if exists tmp")
                    col.db.execute(
                        "create temp table tmp (nid int primary key, fld text)")
                    for mid, ord in self.fieldsToMidOrdPairs.get(name):
                        notes = mw.col.db.all(
                            f"select id, field_at_index(flds, {ord}) from notes where mid = {mid}"
                        )
                        for note in notes:
                            id = note[0]
                            val = NoteFields.htmlToTextLine(note[1])
                            if not val:
                                val = None
                            vals.append([id, val])
                    mw.col.db.executemany(
                        "insert into tmp values (?,?)", vals
                    )

                select = "(select fld from tmp where nid = n.id)"
                srt = (
                    f"""
                    case when {select} glob '*[^0-9.]*' then {select} else cast({select} AS real) end
                    collate nocase asc nulls last
                    """
                )

                cc = self.advBrowser.newCustomColumn(
                    type=type,
                    name=name,
                    onData=fldOnData,
                    sortTableFunction=sortTableFunction,
                    onSort=lambda: srt,
                    setData=setData_(name),
                )
                self.customColumns[name] = cc
        self.advBrowser.setupColumns()

    def getSortClause(self, fieldName: str) -> str:
        def tuple_to_str(tup) -> str:
            (ntid, ord) = tup
            return f"when n.mid = {ntid} then field_at_index(n.flds, {ord})"

        tups = self.fieldsToMidOrdPairs.get(fieldName, [])
        if not tups:
            # no such field
            return "false"

        whenBody = " ".join(map(tuple_to_str, tups))
        return f"(case {whenBody} else null end) collate nocase asc nulls last"

    # Based on the one in utils.py, but keep media file names
    def htmlToTextLine(s):
        s = s.replace("<br>", " ")
        s = s.replace("<br />", " ")
        s = s.replace("<div>", " ")
        s = s.replace("\n", " ")
        s = reSound.sub("\\1", s)  # this line is different
        s = reType.sub("", s)
        s = anki.utils.stripHTMLMedia(s) if pointVersion() < 50 else anki.utils.strip_html_media(s)
        s = s.strip()
        return s

# Precompile some regexes for efficiency
reSound = re.compile(r"\[sound:([^]]+)\]")
reType = re.compile(r"\[\[type:[^]]+\]\]")

nf = NoteFields()
addHook("advBrowserLoaded", nf.onAdvBrowserLoad)
addHook("advBrowserBuildContext", nf.onBuildContextMenu)

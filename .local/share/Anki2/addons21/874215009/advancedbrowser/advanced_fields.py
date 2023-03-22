# -*- coding: utf-8 -*-
# See github page to report issues or to contribute:
# https://github.com/hssm/advanced-browser

import time

from anki.cards import Card
from anki.consts import *
from anki.hooks import addHook
from anki.lang import FormatTimeSpan as FormatTimeSpanContext

from aqt import *
from aqt.operations.card import set_card_flag
from aqt.utils import askUser, tr


class AdvancedFields:

    def onAdvBrowserLoad(self, advBrowser):
        """Called when the Advanced Browser add-on has finished
        loading. Create and add all custom columns owned by this
        module."""

        # Store a list of CustomColumns managed by this module. We later
        # use this to build our part of the context menu.
        self.customColumns = []

        # Convenience method to create lambdas without scope clobbering
        def getOnSort(f): return lambda: f

        # -- Columns -- #

        # First review
        def cFirstOnData(c, n, t):
            first = mw.col.db.scalar(
                "select min(id) from revlog where cid = ?", c.id)
            if first:
                return time.strftime("%Y-%m-%d", time.localtime(first / 1000))

        cc = advBrowser.newCustomColumn(
            type='cfirst',
            name='First Review',
            onData=cFirstOnData,
            onSort=lambda: "(select min(id) from revlog where cid = c.id) asc nulls last",
        )
        self.customColumns.append(cc)
        # ------------------------------- #

        # Last review
        def cLastOnData(c, n, t):
            last = mw.col.db.scalar(
                "select max(id) from revlog where cid = ?", c.id)
            if last:
                return time.strftime("%Y-%m-%d", time.localtime(last / 1000))

        cc = advBrowser.newCustomColumn(
            type='clast',
            name='Last Review',
            onData=cLastOnData,
            onSort=lambda: "(select max(id) from revlog where cid = c.id) asc nulls last"
        )
        self.customColumns.append(cc)
        # ------------------------------- #

        # Average time
        def cAvgtimeOnData(c, n, t):
            avgtime = mw.col.db.scalar(
                "select avg(time)/1000.0 from revlog where cid = ?", c.id)
            if avgtime:
                return mw.col.format_timespan(avgtime)
            return None

        cc = advBrowser.newCustomColumn(
            type='cavgtime',
            name='Time (Average)',
            onData=cAvgtimeOnData,
            onSort=lambda: "(select avg(time) from revlog where cid = c.id) asc nulls last"
        )
        self.customColumns.append(cc)
        # ------------------------------- #

        # Total time
        def cTottimeOnData(c, n, t):
            tottime = mw.col.db.scalar(
                "select sum(time)/1000.0 from revlog where cid = ?", c.id)
            if tottime:
                return mw.col.format_timespan(tottime)
            return None

        cc = advBrowser.newCustomColumn(
            type='ctottime',
            name='Time (Total)',
            onData=cTottimeOnData,
            onSort=lambda: "(select sum(time) from revlog where cid = c.id) asc nulls last"
        )
        self.customColumns.append(cc)
        # ------------------------------- #

        # Fastest time
        def cFasttimeOnData(c, n, t):
            tm = mw.col.db.scalar(
                "select time/1000.0 from revlog where cid = ? "
                "order by time asc limit 1", c.id)
            if tm:
                return mw.col.format_timespan(tm)
            return None

        # Note: capital ASC required to avoid search+replace
        srt = ("(select time/1000.0 from revlog where cid = c.id "
               "order by time ASC limit 1) asc nulls last")

        cc = advBrowser.newCustomColumn(
            type='cfasttime',
            name='Fastest Review',
            onData=cFasttimeOnData,
            onSort=getOnSort(srt)
        )
        self.customColumns.append(cc)
        # ------------------------------- #

        # Slowest time
        def cSlowtimeOnData(c, n, t):
            tm = mw.col.db.scalar(
                "select time/1000.0 from revlog where cid = ? "
                "order by time desc limit 1", c.id)
            if tm:
                return mw.col.format_timespan(tm)
            return None

        srt = ("(select time/1000.0 from revlog where cid = c.id "
               "order by time DESC limit 1) asc nulls last")

        cc = advBrowser.newCustomColumn(
            type='cslowtime',
            name='Slowest Review',
            onData=cSlowtimeOnData,
            onSort=getOnSort(srt)
        )
        self.customColumns.append(cc)
        # ------------------------------- #

        # Overdue interval
        def cOverdueIvl(c, n, t):
            val = self.valueForOverdue(c.odid, c.queue, c.type, c.due)
            if val:
                return mw.col.format_timespan(val * 24 * 60 * 60, context=FormatTimeSpanContext.INTERVALS)


        srt = (f"""
        (select
          (case
             when odid then null
             when queue = {QUEUE_TYPE_LRN} then null
             when queue = {QUEUE_TYPE_NEW} then null
             when type = {CARD_TYPE_NEW} then null
             when {mw.col.sched.today} - due <= 0 then null
             when (queue = {QUEUE_TYPE_REV} or queue = {QUEUE_TYPE_DAY_LEARN_RELEARN} or (type = {CARD_TYPE_REV} and queue < 0)) then ({mw.col.sched.today} - due)
           end
          )
        from cards where id = c.id) asc nulls last""")

        cc = advBrowser.newCustomColumn(
            type='coverdueivl',
            name="Overdue Interval",
            onData=cOverdueIvl,
            onSort=getOnSort(srt)
        )
        self.customColumns.append(cc)
        # ------------------------------- #

        # Previous interval
        def cPrevIvl(c, n, t):
            ivl = mw.col.db.scalar(
                "select ivl from revlog where cid = ? "
                "order by id desc limit 1 offset 1", c.id)
            if ivl is None:
                return
            elif ivl == 0:
                return "0 days"
            elif ivl > 0:
                return mw.col.format_timespan(ivl*86400, context=FormatTimeSpanContext.INTERVALS)
            else:
                return mw.col.format_timespan(-ivl, context=FormatTimeSpanContext.INTERVALS)

        srt = ("(select ivl from revlog where cid = c.id "
               "order by id desc limit 1 offset 1) asc nulls last")

        cc = advBrowser.newCustomColumn(
            type='cprevivl',
            name="Previous Interval",
            onData=cPrevIvl,
            onSort=getOnSort(srt)
        )
        self.customColumns.append(cc)
        # ------------------------------- #

        # Percent correct
        def cPctCorrect(c, n, t):
            if c.reps > 0:
                return "{:2.0f}%".format(
                    100 - ((c.lapses / float(c.reps)) * 100))
            return None

        cc = advBrowser.newCustomColumn(
            type='cpct',
            name='Percent Correct',
            onData=cPctCorrect,
            onSort=lambda: "cast(c.lapses as real)/c.reps asc nulls last"
        )
        self.customColumns.append(cc)
        # ------------------------------- #

        # Previous duration
        def cPrevDur(c, n, t):
            time = mw.col.db.scalar(
                "select time/1000.0 from revlog where cid = ? "
                "order by id desc limit 1", c.id)
            if time:
                return mw.col.format_timespan(time)
            return None

        srt = ("(select time/1000.0 from revlog where cid = c.id "
               "order by id desc limit 1) asc nulls last")

        cc = advBrowser.newCustomColumn(
            type='cprevdur',
            name="Previous Duration",
            onData=cPrevDur,
            onSort=getOnSort(srt)
        )
        self.customColumns.append(cc)
        # ------------------------------- #

        # Created Time (Note)
        def cDateTimeCrt(c, n, t):
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(c.note().id/1000))

        cc = advBrowser.newCustomColumn(
            type='ctimecrtn',
            name='Created Time (Note)',
            onData=cDateTimeCrt,
            onSort=lambda: "n.id asc nulls last"
        )
        self.customColumns.append(cc)
        # ------------------------------- #

        # Created Date (Card)
        def cDateTimeCrt(c, n, t):
            return time.strftime("%Y-%m-%d", time.localtime(c.id/1000))

        cc = advBrowser.newCustomColumn(
            type='cdatecrtc',
            name='Created Date (Card)',
            onData=cDateTimeCrt,
            onSort=lambda: "c.id asc nulls last"
        )
        self.customColumns.append(cc)
        # ------------------------------- #

        # Created Time (Card)
        def cDateTimeCrt(c, n, t):
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(c.id/1000))

        cc = advBrowser.newCustomColumn(
            type='ctimecrtc',
            name='Created Time (Card)',
            onData=cDateTimeCrt,
            onSort=lambda: "c.id asc nulls last"
        )
        self.customColumns.append(cc)
        # ------------------------------- #

        # Current Deck (Filtered)
        def setData(c: Card, value: str):
            old_deck = c.col.decks.get(c.did)
            new_deck = c.col.decks.byName(value)
            if new_deck is None:
                if not askUser(
                        "%s does not exists, do you want to create this deck ?" % value, # translation missing
                        parent=advBrowser,
                        defaultno=True):
                    return False
                new_id = c.col.decks.id(value)
                new_deck = c.col.decks.get(new_id)
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

        def sortTableFunction():
            col = advBrowser.mw.col
            col.db.execute("drop table if exists tmp")
            col.db.execute("create temp table tmp (k int primary key, v text)")
            for deck in col.decks.all():
                advBrowser.mw.col.db.execute(
                    "insert into tmp values (?,?)", deck['id'], deck['name']
                )
        cc = advBrowser.newCustomColumn(
            type="cdeck",
            name="Current Deck (Filtered)",
            onData=lambda c, n, t: advBrowser.mw.col.decks.name(c.did),
            sortTableFunction=sortTableFunction,
            onSort=lambda: "(select v from tmp where k = c.did) collate nocase asc",
            setData=setData,
        )
        self.customColumns.append(cc)
        # ------------------------------- #

        # Flags
        def setData(c: Card, value: str):
            try:
                value = int(value)
            except ValueError:
                value = {"":0, "no":0,"red":1, "orange":2, "green":3, "blue":4, "pink":5, "turquoise":6, "purple":7}.get(value.strip().lower())
                if value is None:
                    return False
            if not 0 <= value <= 7:
                return False
            set_card_flag(parent=advBrowser.browser, card_ids=[c.id], flag=value).run_in_background()
            return True

        cc = advBrowser.newCustomColumn(
            type="cflags",
            name="Flag",
            onData=lambda c, n, t: mw.flags.get_flag(c.flags).label if c.flags else None,
            onSort=lambda: "(case when c.flags = 0 then null else c.flags end) asc nulls last",
            setData=setData,
        )
        self.customColumns.append(cc)
        # ------------------------------- #


    def onBuildContextMenu(self, contextMenu):
        """Build our part of the browser columns context menu."""

        group = contextMenu.newSubMenu("- Advanced -")
        for column in self.customColumns:
            group.addItem(column)

    def valueForOverdue(self, odid, queue, type, due):
        if odid or queue == QUEUE_TYPE_LRN:
            return
        elif queue == QUEUE_TYPE_NEW or type == CARD_TYPE_NEW:
            return
        else:
            diff = mw.col.sched.today - due
            if diff <= 0:
                return
            if queue in (QUEUE_TYPE_REV, QUEUE_TYPE_DAY_LEARN_RELEARN) or (type == CARD_TYPE_REV and queue < 0):
                return diff
            else:
                return


af = AdvancedFields()
addHook("advBrowserLoaded", af.onAdvBrowserLoad)
addHook("advBrowserBuildContext", af.onBuildContextMenu)

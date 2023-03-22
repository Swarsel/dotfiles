# -*- coding: utf-8 -*-
# See github page to report issues or to contribute:
# https://github.com/hssm/advanced-browser


class Column:
    """A basic column. Used to represent built-in columns in some
    places.

    """

    def __init__(self, type, name):
        self.type = type
        self.name = name


class CustomColumn(Column):
    """A custom browser column."""

    def __init__(self, type, name, onData, onSort=None,
                 sortTableFunction=False, setData=None):
        """type = Internally used key to identify the column.

        name = Name of column, visible to the user.

        onData = Function that returns the value of a card for this
        column. The function must be defined with three parameters: 
        card, note, and type. These values provide the context to
        derive the value for the card passed to it.
        E.g.:
        def myColumnOnData(card, note, type):
            return mw.col.db.scalar(
                "select min(id) from revlog where cid = ?", card.id)

        onSort = Optional function that returns the ORDER BY clause
        of the query in order to correctly sort the column. The ORDER
        BY clause has access to tables "c" and "n" for cards and notes,
        respectively. See find.py::_query for reference.

        E.g.:
        def myColumnOnSort1():
            return "c.ivl" # Sort by card interval

        A nested query is also possible:

        def myColumnOnSort2():
            # Sort by first review date
            return "(select min(id) from revlog where cid = c.id)"


        """
        self.type = type
        self.name = name
        self.onData = onData
        self.onSort = onSort if onSort else lambda: None
        self.sortTableFunction = sortTableFunction
        self._setData = setData

    def setData(self, *args, **kwargs):
        if self._setData is None:
            return False
        return self._setData(*args, **kwargs)

    def __hash__(self):
        return hash(self.name)

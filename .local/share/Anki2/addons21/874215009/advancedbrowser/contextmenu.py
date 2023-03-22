# -*- coding: utf-8 -*-
# See github page to report issues or to contribute:
# https://github.com/hssm/advanced-browser


class ContextMenu:
    def __init__(self, subGroupName=None):
        self._items = []
        self.name = subGroupName

    def addItem(self, item):
        """Add a Column for a menu item or ContextMenu for a sub-menu."""
        self._items.append(item)

    def newSubMenu(self, name):
        """Create and add a new sub-menu."""
        cm = ContextMenu(subGroupName=name)
        self.addItem(cm)
        return cm

    def items(self):
        """Return a list of all items sorted by name."""
        self._items = list(sorted(set(self._items), key=lambda x: x.name))
        return self._items

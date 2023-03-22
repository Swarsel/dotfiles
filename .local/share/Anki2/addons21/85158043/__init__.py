# -*- coding: utf-8 -*-
# Copyright: Simone Gaiarin <simgunz@gmail.com>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# Name: Minimize to Tray 2
# Version: 0.2
# Description: Minimize anki to tray when the X button is pressed (Anki 2 version)
# Homepage: https://github.com/simgunz/anki-plugins
# Report any problem in the github issues section
import sys
from types import MethodType

import sip
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from aqt import gui_hooks, mw  # mw is the INSTANCE of the main window
from aqt.main import AnkiQt


class AnkiSystemTray:
    def __init__(self, mw):
        """Create a system tray with the Anki icon."""
        self.mw = mw
        self.isAnkiFocused = True
        self.isMinimizedToTray = False
        self.lastFocusedWidget = mw
        self.explicitlyHiddenWindows = []
        self.trayIcon = self._createTrayIcon()
        QApplication.setQuitOnLastWindowClosed(False)
        self._configureMw()
        self.trayIcon.show()
        config = self.mw.addonManager.getConfig(__name__)
        if config["hide_on_startup"]:
            self.hideAll()

    def onActivated(self, reason):
        """Show/hide all Anki windows when the tray icon is clicked.

        The windows are shown if:
        - anki window is not in focus
        - any window is minimized
        - anki is minimize to tray
        The windows are hidden otherwise.

        The focus cannot be detected given that the main window focus is lost before this
        slot is activated. For this reason and to prevent that anki is minimized when not
        focused, on Windows are the windows are never hidden.
        """
        if reason == QSystemTrayIcon.Trigger:
            if (
                not self.isAnkiFocused
                or self._anyWindowMinimized()
                or self.isMinimizedToTray
            ):
                self.showAll()
            else:
                if not sys.platform.startswith("win32"):
                    self.hideAll()

    def onFocusChanged(self, old, now):
        """Keep track of the focused window in order to refocus it on showAll."""
        self.isAnkiFocused = now is not None
        if self.isAnkiFocused:
            self.lastFocusedWidget = now

    def onExit(self):
        self.mw.closeEventFromAction = True
        self.mw.close()

    def showAll(self):
        """Show all windows."""
        if self.isMinimizedToTray:
            self._showWindows(self.explicitlyHiddenWindows)
        else:
            self._showWindows(self._visibleWindows())
        if not sip.isdeleted(self.lastFocusedWidget):
            self.lastFocusedWidget.raise_()
            self.lastFocusedWidget.activateWindow()
        self.isMinimizedToTray = False

    def hideAll(self):
        """Hide all windows."""
        self.explicitlyHiddenWindows = self._visibleWindows()
        for w in self.explicitlyHiddenWindows:
            w.hide()
        self.isMinimizedToTray = True

    def _showWindows(self, windows):
        for w in windows:
            if w.isMinimized() == Qt.WindowMinimized:
                # Windows that were maximized are not restored maximied unfortunately
                w.showNormal()
            else:
                # hide(): hack that solves two problems:
                # 1. focus the windows after TWO other non-Anki windows
                # gained focus (Qt bug?). Causes a minor flicker when the
                # Anki windows are already visible.
                # 2. allows avoiding to call activateWindow() on each
                # windows in order to raise them above non-Anki windows
                # and thus avoid breaking the restore-last-focus mechanism
                w.hide()
                w.show()
            w.raise_()

    def _visibleWindows(self):
        """Return the windows actually visible Anki windows.

        Anki has some hidden windows and menus that we should ignore.
        """
        windows = []
        for w in QApplication.topLevelWidgets():
            if w.isWindow() and not w.isHidden():
                if not w.children():
                    continue
                windows.append(w)
        return windows

    def _anyWindowMinimized(self):
        return any(
            w.windowState() == Qt.WindowMinimized for w in self._visibleWindows()
        )

    def _createTrayIcon(self):
        trayIcon = QSystemTrayIcon(self.mw)
        ankiLogo = QIcon()
        ankiLogo.addPixmap(QPixmap("icons:anki.png"), QIcon.Normal, QIcon.Off)
        trayIcon.setIcon(QIcon.fromTheme("anki", ankiLogo))
        trayMenu = QMenu(self.mw)
        trayIcon.setContextMenu(trayMenu)
        showAction = trayMenu.addAction("Show all windows")
        showAction.triggered.connect(self.showAll)
        trayMenu.addAction(self.mw.form.actionExit)
        trayIcon.activated.connect(self.onActivated)
        return trayIcon

    def _configureMw(self):
        self.mw.closeEventFromAction = False
        self.mw.app.focusChanged.connect(self.onFocusChanged)
        # Disconnecting from close may have some side effects
        # (e.g. QApplication::lastWindowClosed() signal not emitted)
        self.mw.form.actionExit.triggered.disconnect(self.mw.close)
        self.mw.form.actionExit.triggered.connect(self.onExit)
        self.mw.closeEvent = self._wrapCloseCloseEvent()

    def _wrapCloseCloseEvent(self):
        """Override the close method of the mw instance."""

        def repl(self, event):
            if self.closeEventFromAction:
                # The 'Exit' action in the sys tray context menu was activated
                AnkiQt.closeEvent(self, event)
            else:
                # The main window X button was pressed
                # self.col.save()
                self.systemTray.hideAll()
                event.ignore()

        return MethodType(repl, self.mw)


def minimizeToTrayInit():
    if hasattr(mw, "trayIcon"):
        return
    mw.systemTray = AnkiSystemTray(mw)


gui_hooks.main_window_did_init.append(minimizeToTrayInit)

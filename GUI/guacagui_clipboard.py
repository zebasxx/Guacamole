#!/usr/bin/env python3
"""
guacagui_clipboard.py

This module provides an enhanced version of the Guacagui browser used to
connect to an Apache Guacamole server.  It is based on the previous
versions of Guacagui which include a tabbed Chromium‑based browser, a
configurable set of macro text boxes for frequently used commands,
navigation controls, and a Sidebar button which toggles the Guacamole
sidebar via xdotool.  The key enhancement in this file is enabling
full clipboard read/write access for the embedded web pages.  By
setting the appropriate `QWebEngineSettings` attributes and
automatically granting clipboard permission, the Guacamole web
application can synchronise the remote SSH console’s clipboard with the
host operating system, similar to behaviour observed in Microsoft
Edge.

Usage:

    python3 guacagui_clipboard.py

The configuration file `config.json` in the same directory controls
the home URL and the macro definitions.  See the `read_config`
function for details on its structure.

"""

import json
import os
import sys
import subprocess
from functools import partial

from PyQt5.QtCore import QUrl, pyqtSlot, Qt, QEvent
from PyQt5.QtGui import QIcon, QGuiApplication, QClipboard
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QStatusBar,
    QTabWidget,
    QToolBar,
    QAction,
    QLineEdit,
    QLabel,
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings, QWebEnginePage


# Name of the JSON configuration file expected to reside alongside this script.
CONFIG_FILE = "config.json"


def read_config() -> dict:
    """Read and validate the configuration from CONFIG_FILE.

    Returns a dictionary with two keys:

    - ``home_url``: The URL to load when the application starts.  A
      default of ``https://www.google.com`` is used if this value is
      missing or invalid.  If the URL string does not specify a
      protocol, ``https://`` is prefixed automatically.

    - ``macros``: A list of dictionaries defining the macro text
      boxes.  Each entry must contain ``name`` and ``text``
      strings.  The ``name`` is used as a label and the ``text`` is
      placed into the associated QLineEdit.  Entries with missing or
      invalid fields are skipped.
    """
    cfg = {
        "home_url": "https://www.google.com",
        "macros": [],
    }
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), CONFIG_FILE)
    if not os.path.exists(config_path):
        return cfg
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Parse home_url
        url = data.get("home_url", cfg["home_url"])
        if isinstance(url, str):
            url = url.strip()
            if not url.startswith(("http://", "https://")):
                # Default to https for unspecified schemes
                url = "https://" + url
            cfg["home_url"] = url
        # Parse macros list
        macros = data.get("macros", [])
        if isinstance(macros, list):
            cleaned = []
            for entry in macros:
                if not isinstance(entry, dict):
                    continue
                # Accept alternate key names for convenience
                name = entry.get("name") or entry.get("label") or entry.get("button")
                text = entry.get("text") or entry.get("macro")
                if isinstance(name, str) and isinstance(text, str):
                    cleaned.append({"name": name, "text": text})
            cfg["macros"] = cleaned
        return cfg
    except Exception:
        return cfg


def read_home_url() -> str:
    """Return the configured home URL with scheme, falling back to the default."""
    return read_config().get("home_url", "https://www.google.com")


def read_macros() -> list:
    """Return the list of macro definitions from the configuration file."""
    return read_config().get("macros", [])


class BrowserTab(QWebEngineView):
    """A QWebEngineView subclass that sets clipboard permissions on creation.

    Each tab represents one web page.  When created, it sets the
    appropriate QWebEngineSettings attributes to allow JavaScript to
    access the system clipboard.  If both ``JavascriptCanAccessClipboard``
    and ``JavascriptCanPaste`` are enabled, the page’s feature
    permission for clipboard read/write is automatically granted by
    Qt’s WebEngine, obviating the need for manual permission requests.
    A slot is also provided to handle feature permission requests as
    an additional safety net: if the clipboard permission is ever
    requested explicitly by the page, it is granted automatically.
    """

    def __init__(self, main_window: "BrowserMainWindow", url: str | None = None) -> None:
        super().__init__()
        self.main_window = main_window

        # Enable JavaScript clipboard access for this page.  See Qt
        # documentation: enabling both of these attributes grants the
        # ClipboardReadWrite feature automatically【148405230257740†L172-L255】【975455813317479†L873-L877】.
        settings = self.page().settings()
        settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanPaste, True)

        # Also connect featurePermissionRequested as a fallback.  This
        # handler will grant the clipboard permission if it is
        # requested explicitly.  The signal provides the URL and the
        # feature being requested.
        self.page().featurePermissionRequested.connect(self.on_feature_permission_requested)

        # Set the initial URL
        initial_url = url or read_home_url()
        self.setUrl(QUrl(initial_url))

        # Connect signals to update the UI
        self.urlChanged.connect(self.on_url_changed)
        self.loadFinished.connect(self.on_load_finished)
        self.titleChanged.connect(self.on_title_changed)

    def createWindow(self, _type):  # type: ignore[override]
        """Override createWindow to open new tabs instead of windows."""
        new_tab = BrowserTab(self.main_window)
        self.main_window.add_browser_tab(new_tab, "New Tab")
        return new_tab

    @pyqtSlot(QUrl)
    def on_url_changed(self, url: QUrl) -> None:
        """Update the tab text when the URL changes."""
        if self is self.main_window.current_browser():
            self.main_window.update_urlbar(url)
        idx = self.main_window.tabs.indexOf(self)
        if idx != -1:
            self.main_window.tabs.setTabText(idx, url.toString())

    @pyqtSlot(bool)
    def on_load_finished(self, _success: bool) -> None:
        """Update tab and window titles when a page finishes loading."""
        title = self.page().title() or self.url().toString() or "Untitled"
        idx = self.main_window.tabs.indexOf(self)
        if idx != -1:
            self.main_window.tabs.setTabText(idx, title)
        if self is self.main_window.current_browser():
            self.main_window.update_title(title)

    @pyqtSlot(str)
    def on_title_changed(self, title: str) -> None:
        """Update tab and window titles when the page title changes."""
        idx = self.main_window.tabs.indexOf(self)
        if idx != -1:
            tab_text = title.strip() if title.strip() else self.url().toString()
            self.main_window.tabs.setTabText(idx, tab_text)
        if self is self.main_window.current_browser():
            self.main_window.update_title(title.strip() if title.strip() else "Untitled")

    @pyqtSlot(QUrl, QWebEnginePage.Feature)
    def on_feature_permission_requested(self, security_origin: QUrl, feature: QWebEnginePage.Feature) -> None:
        """Automatically grant clipboard permissions when requested.

        Some versions of Qt may still emit a feature permission request
        even when both JavaScript clipboard attributes are enabled.  If
        the feature requested is ClipboardReadWrite, grant the
        permission.  Otherwise, leave it as Denied by default.
        """
        if feature == QWebEnginePage.Feature.ClipboardReadWrite:
            self.page().setFeaturePermission(
                security_origin, feature, QWebEnginePage.PermissionGrantedByUser
            )


class MacroLineEdit(QLineEdit):
    """A QLineEdit that automatically copies its contents to the clipboard on click.

    When the user presses the mouse inside the line edit, the text is
    copied to the standard clipboard and the primary selection (if
    available).  This supports fast copy/paste for frequently used
    commands.  The text remains editable but changes made by the user
    are not saved back to the configuration file.
    """

    def mousePressEvent(self, event):  # type: ignore[override]
        # Call base implementation to allow normal cursor movement
        super().mousePressEvent(event)
        text = self.text()
        if not text:
            return
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(text, QClipboard.Clipboard)
        clipboard.setText(text, QClipboard.Selection)


class BrowserMainWindow(QMainWindow):
    """Main window containing the tabbed browser and controls."""

    def __init__(self) -> None:
        super().__init__()
        # Tab widget configuration
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.setCentralWidget(self.tabs)

        # Status bar for page status
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        # Set window icon to the guacamole icon if available
        try:
            icon_path = "/usr/share/icons/hicolor/scalable/apps/guacagui.svg"
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
            else:
                self.setWindowIcon(QIcon.fromTheme("guacagui"))
        except Exception:
            pass

        # Navigation toolbar
        navtb = QToolBar("Navigation")
        navtb.setMovable(False)
        self.addToolBar(navtb)

        # Back button
        back_btn = QAction("Back", self)
        back_btn.setStatusTip("Back to previous page")
        back_btn.triggered.connect(lambda: self.current_browser().back())
        navtb.addAction(back_btn)

        # Forward button
        next_btn = QAction("Forward", self)
        next_btn.setStatusTip("Forward to next page")
        next_btn.triggered.connect(lambda: self.current_browser().forward())
        navtb.addAction(next_btn)

        # Reload button
        reload_btn = QAction("Reload", self)
        reload_btn.setStatusTip("Reload current page")
        reload_btn.triggered.connect(lambda: self.current_browser().reload())
        navtb.addAction(reload_btn)

        # Home button
        home_btn = QAction("Home", self)
        home_btn.setStatusTip("Go to home page")
        home_btn.triggered.connect(self.navigate_home)
        navtb.addAction(home_btn)

        # Stop button
        stop_btn = QAction("Stop", self)
        stop_btn.setStatusTip("Stop loading current page")
        stop_btn.triggered.connect(lambda: self.current_browser().stop())
        navtb.addAction(stop_btn)

        # Sidebar toggle button
        sidebar_btn = QAction("Sidebar", self)
        sidebar_btn.setStatusTip("Toggle Guacamole sidebar (Ctrl+Alt+Shift)")
        sidebar_btn.triggered.connect(self.toggle_sidebar)
        navtb.addAction(sidebar_btn)

        # Macro text boxes from configuration
        self.macros = read_macros()
        if self.macros:
            navtb.addSeparator()
            for macro in self.macros:
                name = macro.get("name", "")
                text = macro.get("text", "")
                if name:
                    lbl = QLabel(name + ":")
                    navtb.addWidget(lbl)
                box = MacroLineEdit()
                box.setText(text)
                box.setFixedWidth(200)
                box.setReadOnly(False)
                navtb.addWidget(box)

        # Create the initial tab
        home_url = read_home_url()
        first_tab = BrowserTab(self, url=home_url)
        self.add_browser_tab(first_tab, "Home")

        self.setWindowTitle("Guacagui")
        self.show()

    # Helper to return the current BrowserTab
    def current_browser(self) -> BrowserTab:
        return self.tabs.currentWidget()  # type: ignore[return-value]

    # Add a BrowserTab to the tab widget
    def add_browser_tab(self, browser: BrowserTab, label: str = "New Tab") -> int:
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
        return i

    # Open a blank tab when the tab bar is double clicked in empty space
    @pyqtSlot(int)
    def tab_open_doubleclick(self, index: int) -> None:
        if index == -1:
            new_tab = BrowserTab(self)
            self.add_browser_tab(new_tab, "New Tab")

    # Update UI when the current tab changes
    @pyqtSlot(int)
    def current_tab_changed(self, index: int) -> None:
        browser = self.current_browser()
        if not isinstance(browser, BrowserTab):
            return
        url = browser.url()
        self.update_urlbar(url)
        title = browser.page().title() or "Untitled"
        self.update_title(title)

    # Close the specified tab if more than one tab is open
    @pyqtSlot(int)
    def close_current_tab(self, index: int) -> None:
        if self.tabs.count() < 2:
            return
        self.tabs.removeTab(index)

    # Update the window title
    def update_title(self, title: str) -> None:
        self.setWindowTitle(title)

    # Update the URL bar if present (retained for compatibility; our UI has no URL bar)
    def update_urlbar(self, qurl: QUrl) -> None:
        urlbar = getattr(self, "urlbar", None)
        if isinstance(urlbar, QLineEdit):
            urlbar.setText(qurl.toString())
            urlbar.setCursorPosition(0)

    # Navigate to the home URL in the current tab
    def navigate_home(self) -> None:
        self.current_browser().setUrl(QUrl(read_home_url()))

    # Navigate to the URL typed in the URL bar (if present)
    def navigate_to_url(self) -> None:
        urlbar = getattr(self, "urlbar", None)
        if not isinstance(urlbar, QLineEdit):
            return
        url_text = urlbar.text().strip()
        if url_text and not url_text.startswith(("http://", "https://")):
            url_text = "http://" + url_text
        self.current_browser().setUrl(QUrl(url_text))

    # Toggle the Guacamole sidebar by sending Ctrl+Alt+Shift via xdotool
    def toggle_sidebar(self) -> None:
        view = self.current_browser()
        if not isinstance(view, QWebEngineView):
            return
        view.setFocus()
        try:
            subprocess.run(["xdotool", "key", "ctrl+alt+shift"], check=True)
        except Exception:
            # Fall back to synthesising key events via Qt.  This may not
            # work with Guacamole, but is retained as a best effort.
            from PyQt5.QtGui import QKeyEvent
            from PyQt5.QtCore import QEvent
            modifiers = [Qt.Key_Control, Qt.Key_Alt, Qt.Key_Shift]
            for key in modifiers:
                event_press = QKeyEvent(QEvent.KeyPress, key, Qt.NoModifier, "")
                QApplication.postEvent(view, event_press)
            for key in reversed(modifiers):
                event_release = QKeyEvent(QEvent.KeyRelease, key, Qt.NoModifier, "")
                QApplication.postEvent(view, event_release)


def main() -> None:
    app = QApplication(sys.argv)
    window = BrowserMainWindow()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
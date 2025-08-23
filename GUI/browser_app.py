#!/usr/bin/env python3
"""
browser_app.py

A minimal cross‑platform tabbed web browser implemented with PyQt5. On
startup, the application reads a configuration file (`config.json`) from
the same directory to determine the URL to load in the initial tab. New
tabs can be opened by double‑clicking the tab bar or by clicking links
that request a new window (e.g. `target="_blank"`). Each tab is a
`QWebEngineView` with navigation controls (back, forward, reload, stop
and a URL bar) common to all tabs.

Usage:

    # install dependencies first
    pip install PyQt5 PyQtWebEngine
    
    # ensure config.json exists in the same directory as this script
    # and contains a JSON object with a "home_url" field, for example:
    # {"home_url": "https://www.example.com"}

    python3 browser_app.py

The application is designed to run on Windows, macOS and Linux, provided
PyQt5 and its WebEngine modules are available. QtWebEngine may require
additional system packages on some distributions.
"""

import json
import os
import sys
from functools import partial

from PyQt5.QtCore import QUrl, pyqtSlot
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QStatusBar,
    QTabWidget,
    QToolBar,
    QAction,
    QLineEdit,
)
from PyQt5.QtWebEngineWidgets import QWebEngineView


CONFIG_FILE = "config.json"


def read_config() -> str:
    """Read the home URL from the local configuration file.

    Returns a default URL if the configuration file is missing or invalid.

    The configuration file must be a JSON document with a top‑level
    `home_url` property. For example:

        {"home_url": "https://www.python.org"}

    The returned URL always includes a scheme (defaults to http).
    """
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), CONFIG_FILE)
    default_url = "https://www.google.com"
    if not os.path.exists(config_path):
        return default_url
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        url = data.get("home_url", default_url)
        # ensure the URL has a scheme; QUrl will infer one if missing
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        return url
    except Exception:
        return default_url


class BrowserTab(QWebEngineView):
    """A single browser tab which knows how to spawn new tabs when needed."""

    def __init__(self, main_window: "BrowserMainWindow", url: str | None = None) -> None:
        super().__init__()
        self.main_window = main_window
        # Initialise with provided URL or the home URL
        initial_url = url or read_config()
        self.setUrl(QUrl(initial_url))
        # When the URL changes or a page finishes loading, update the UI
        self.urlChanged.connect(self.on_url_changed)
        self.loadFinished.connect(self.on_load_finished)

    def createWindow(self, _type):  # type: ignore[override]
        """Overrides QWebEngineView.createWindow to open links in a new tab.

        When a link requests a new window (for example, via target="_blank"),
        Qt calls this method to provide a new view. Here we delegate to the
        main window to create a new tab and return the associated view.
        """
        new_tab = BrowserTab(self.main_window)
        self.main_window.add_browser_tab(new_tab, "New Tab")
        return new_tab

    @pyqtSlot(QUrl)
    def on_url_changed(self, url: QUrl) -> None:
        """Synchronise the URL bar when this tab's URL changes."""
        if self is self.main_window.current_browser():
            self.main_window.update_urlbar(url)

    @pyqtSlot(bool)
    def on_load_finished(self, _success: bool) -> None:
        """Update the window title when the page finishes loading."""
        if self is self.main_window.current_browser():
            title = self.page().title() or "Untitled"
            self.main_window.update_title(title)


class BrowserMainWindow(QMainWindow):
    """Main application window hosting a tabbed browser."""

    def __init__(self) -> None:
        super().__init__()
        # Set up the tab widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        # Connect tab interactions
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.setCentralWidget(self.tabs)

        # Status bar to show page status (optional, can be extended)
        self.status = QStatusBar()
        self.setStatusBar(self.status)

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

        # Separator before the URL bar
        navtb.addSeparator()

        # URL input bar
        self.urlbar = QLineEdit()
        self.urlbar.setClearButtonEnabled(True)
        # When user presses return, navigate to the typed URL
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        navtb.addWidget(self.urlbar)

        # Stop button
        stop_btn = QAction("Stop", self)
        stop_btn.setStatusTip("Stop loading current page")
        stop_btn.triggered.connect(lambda: self.current_browser().stop())
        navtb.addAction(stop_btn)

        # Create the first tab with the home URL
        home_url = read_config()
        first_tab = BrowserTab(self, url=home_url)
        self.add_browser_tab(first_tab, "Home")

        # Set the initial window title
        self.setWindowTitle("Simple Tabbed Browser")
        self.show()

    def current_browser(self) -> BrowserTab:
        """Return the currently active browser tab."""
        return self.tabs.currentWidget()  # type: ignore[return-value]

    def add_browser_tab(self, browser: BrowserTab, label: str = "New Tab") -> int:
        """Add a new browser tab and return its index."""
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
        return i

    # Slot: double clicking empty space on tab bar opens a new blank tab
    @pyqtSlot(int)
    def tab_open_doubleclick(self, index: int) -> None:
        if index == -1:
            new_tab = BrowserTab(self)
            self.add_browser_tab(new_tab, "New Tab")

    # Slot: update UI when the current tab changes
    @pyqtSlot(int)
    def current_tab_changed(self, index: int) -> None:
        browser = self.current_browser()
        if not isinstance(browser, BrowserTab):
            return
        url = browser.url()
        self.update_urlbar(url)
        title = browser.page().title() or "Untitled"
        self.update_title(title)

    # Slot: close the selected tab
    @pyqtSlot(int)
    def close_current_tab(self, index: int) -> None:
        if self.tabs.count() < 2:
            return
        self.tabs.removeTab(index)

    def update_title(self, title: str) -> None:
        """Set the window title to reflect the current page title."""
        self.setWindowTitle(title)

    def update_urlbar(self, qurl: QUrl) -> None:
        """Update the URL bar with the given URL."""
        # We show only the URL string here; for readability reset cursor
        self.urlbar.setText(qurl.toString())
        self.urlbar.setCursorPosition(0)

    # Navigation actions
    def navigate_home(self) -> None:
        """Navigate the current tab to the configured home URL."""
        url = read_config()
        self.current_browser().setUrl(QUrl(url))

    def navigate_to_url(self) -> None:
        """Navigate the current tab to the URL entered in the URL bar."""
        url_text = self.urlbar.text().strip()
        # Provide a default scheme if missing
        if url_text and not url_text.startswith(("http://", "https://")):
            url_text = "http://" + url_text
        self.current_browser().setUrl(QUrl(url_text))


def main() -> None:
    """Entry point: create the application and run the main loop."""
    app = QApplication(sys.argv)
    window = BrowserMainWindow()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
# -*- coding: utf-8 -*-
# vim: set et sw=4 ts=4 :

from PyQt5.QtWidgets import (
        QSystemTrayIcon,
        QMenu,
        QAction,
)

from PyQt5.QtCore import (
        pyqtSignal,
)

from txt import txt

class SysTrayIcon(QSystemTrayIcon):

    clicked = pyqtSignal()  # single click

    def __init__(self, parent, icon, title, msgDur, invertcolors, memurl, mempos, memcss, *args, **kwargs):
        super().__init__(parent, *args, toolTip=title, **kwargs)

        if invertcolors is None:  invertcolors = False
        if memurl is None:  memurl = False
        if mempos is None:  mempos = False
        if memcss is None:  memcss = False

        self.msgDur = msgDur
        self.activated.connect(lambda reason: self.clicked.emit() if reason == QSystemTrayIcon.Trigger else None)

        trayMenu = QMenu()

        # TODO: make showHide and toggleMute also checkable?

        def act(action, string):
            x = QAction(string, self)
            x.triggered.connect(action)
            trayMenu.addAction(x)

        act(parent.showHide, txt.showHide)
        # act(parent.reload, txt.reload)
        # act(parent.toggleMute, txt.toggleMute)

        if invertcolors is None:  invertcolors = False
        invertcolors = QAction(txt.invertcolors, self, checkable=True, checked=invertcolors)
        invertcolors.changed.connect(lambda: parent.invertcolors(invertcolors.isChecked()))
        trayMenu.addAction(invertcolors)

        self.memurl = QAction(txt.memurl, self, checkable=True, checked=memurl)
        self.memurl.changed.connect(lambda: parent.memurl(self.memurl.isChecked()))
        trayMenu.addAction(self.memurl)

        self.mempos = QAction(txt.mempos, self, checkable=True, checked=mempos)
        self.mempos.changed.connect(lambda: parent.mempos(self.mempos.isChecked()))
        trayMenu.addAction(self.mempos)

        self.memcss = QAction(txt.memcss, self, checkable=True, checked=memcss)
        self.memcss.changed.connect(lambda: parent.memcss(self.memcss.isChecked()))
        trayMenu.addAction(self.memcss)

        act(parent.toggleMemAll, txt.toggleMemAll)
        act(parent.incognitoQuit, txt.incognitoQuit)
        act(parent.quit, txt.quit)

        self.setContextMenu(trayMenu)
        self.setIcon(icon)
        self.show()

        def windowCloseEvent(win, event):
            event.ignore()
            win.hide()
            self.showMessage(
                    title,
                    txt.minimized,
                    QSystemTrayIcon.Information,
                    self.msgDur
            )

        parent.closeEvent = lambda event: windowCloseEvent(parent, event)

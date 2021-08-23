# -*- coding: utf-8 -*-
# vim: set et sw=4 ts=4 :

from PyQt5.QtWidgets import (
        QMainWindow,
)

from PyQt5.QtGui import (
        QCursor,
)

from PyQt5.QtCore import (
        Qt,
)

from view import View
from systray import SysTrayIcon


class SingleMainWindow(QMainWindow):

    def __init__(self, prof, storage, quit, icon, *args, **kwargs):
        super().__init__(*args,**kwargs)
        title = f"{prof['title']} - ePread"
        self.setWindowTitle(title)
        self.setWindowState(Qt.WindowMaximized)

        # general setup
        self.view = View(prof, self)
        self.setCentralWidget(self.view)

        # actions
        self.quit = quit
        self.showHide = lambda: self.show() if self.isHidden() else self.hide()
        self.reload = self.view.reload  # for systrayicon
        def _invertcolors(newval): prof['invertcolors'] = newval; self.view.inverted = not newval; self.view.toggleInvertColors()
        def _memurl(newval): prof['memurl'] = newval
        def _mempos(newval): prof['mempos'] = newval
        def _memcss(newval): prof['memcss'] = newval
        self.invertcolors = _invertcolors  # for systrayicon
        self.memurl = _memurl  # for systrayicon
        self.mempos = _mempos  # for systrayicon
        self.memcss = _memcss  # for systrayicon

        def _incognitoQuit():
            self.memurl(False)
            self.mempos(False)
            self.memcss(False)
            quit()
        self.incognitoQuit = _incognitoQuit

        self.getOptions = lambda: (self.view.inverted, prof['memurl'], prof['mempos'], prof['memcss'])

        def _memall():
            if any([prof['memurl'], prof['mempos'], prof['memcss']]):
                self.memurl(False); self.ico.memurl.setChecked(False)
                self.mempos(False); self.ico.mempos.setChecked(False)
                self.memcss(False); self.ico.memcss.setChecked(False)
            else:
                self.memurl(True); self.ico.memurl.setChecked(True)
                self.mempos(True); self.ico.mempos.setChecked(True)
                self.memcss(True); self.ico.memcss.setChecked(True)
        self.toggleMemAll = _memall

        # systrayicon
        conf = storage.getConfig()
        if conf['usetray']:
            self.ico = SysTrayIcon(
                    self,
                    icon=icon,
                    title=title,
                    msgDur=conf['traymsgdur'],
                    invertcolors=prof['invertcolors'],
                    memurl=prof['memurl'],
                    mempos=prof['mempos'],
                    memcss=prof['memcss'],
            )
            # self.ico.clicked.connect(self.showHide)
            self.ico.clicked.connect(lambda: self.ico.contextMenu().popup(QCursor.pos()))
        else:
            self.showHide = self.quit  # for shortcuts below
            self.close    = self.quit  # to trigger memurl and mempos if true
            def ce(ev):
                ev.ignore()    # so that quit() is called (?)
                self.deleteLater()  # https://forum.qt.io/topic/110568
                self.quit()
            self.closeEvent = ce

        # shortcuts
        storage.bindShortcutsToWindow(self, {
                'reload':      self.view.reload,
                'stop':        self.view.stop,
                'homePage':    self.view.homePage,
                'endPage':     self.view.endPage,
                'back':        self.view.back,
                'forward':     self.view.forward,
                'zoomIn':      self.view.zoomIn,
                'zoomOut':     self.view.zoomOut,
                'zoomReset':   self.view.zoomReset,
                'invert':      self.view.toggleInvertColors,
                'styleDialog': self.view.cssDialog,
                'findDialog':  self.view.findDialog,
                'findNext':    self.view.findNext,
                'findPrev':    self.view.findPrev,
                'findClear':   self.view.findClear,
                # 'copyUrl':     self.view.copyUrl,
                # 'pasteUrl':    self.view.pasteUrl,
                'saveAsPdf':   self.view.saveAsPdf,
                'quit':        self.quit,
                'showHide':    self.showHide,
                'closeToTray': self.close,
                'toggleMute':  self.toggleMute,
        })

    def toggleMute(self):
        # mute and disable notifications
        # but there is no notifications in the first place
        self.view.setMuted(not self.view.isMuted())



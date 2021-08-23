# -*- coding: utf-8 -*-
# vim: set et sw=4 ts=4 :

from PyQt5.QtWebEngineWidgets import (
        QWebEngineView,
        QWebEnginePage,
        QWebEngineProfile,
)

from PyQt5.QtCore import (
        QUrl,
        QObject,
)

from PyQt5.QtWidgets import (
        QFileDialog,
)

from find import FindDialog
from customcss import CustomCssDialog
from txt import txt

class View(QWebEngineView):

    def __init__(self, prof, *args, **kwargs):
        super().__init__(*args,**kwargs)
        # general setup
        # see: https://stackoverflow.com/a/48142651
        self.profile = QWebEngineProfile(None)  # incognito
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        #DEBUG: python3 -c 'from PyQt5.QtWebEngineWidgets import QWebEngineProfile; print("\n".join(dir(QWebEngineProfile)))' | grep -i cook
        self.Page = QWebEnginePage(self.profile, self)
        self.setPage(self.Page)
        #
        self.darkcss = prof['dark']
        self.inverted = prof['invertcolors']
        self.Page.loadFinished.connect(self.updateInvertColors)
        self.customCss = None
        self.Page.loadFinished.connect(self.applyCustomCss)
        #
        if prof['css']:
            self.assignCustomCss(prof['css'])
        self.ccssdialog = CustomCssDialog(prof['css'])
        self.ccssdialog.submit.connect(self.assignCustomCss)
        #
        if type(prof['url']) is not list:
            self.setUrl(QUrl(prof['url']))
            self.homePage = lambda: self.setUrl(self.setUrl(QUrl(prof['url'])))
            self.endPage = lambda: None
        else:  # multiple urls
            self._urls = prof['url']
            self.homePage = lambda: self.setUrl(QUrl(self._urls[0]))
            self.endPage = lambda: self.setUrl(QUrl(self._urls[-1]))
            # TODO: auto-detect `i` from the current url
            self.getCurrentPageIndex = lambda: \
                self._urls.index( self.url().toString().split('#')[0] )  # remove from `#` to the end, if found
            def _setpageindex(n, scrollToEnd=False):
                if 0 <= n < len(self._urls):
                    self.setUrl(QUrl(self._urls[n]))
                    if scrollToEnd:
                        self.Page.loadFinished.connect(lambda: self.Page.runJavaScript('window.scrollTo(0, document.body.scrollHeight)'))
                        # https://stackoverflow.com/a/11715670
            self.setCurrentPageIndex = _setpageindex
            self.setCurrentPageIndex(prof.get('startidx', 0))
            def _next():
                i = self.getCurrentPageIndex()
                self.setCurrentPageIndex(i+1)
            def _prev(scrollToEnd=False):
                i = self.getCurrentPageIndex()
                self.setCurrentPageIndex(i-1, scrollToEnd)
            self.nextPage = _next
            self.prevPage = _prev
        #
        self.fdialog = FindDialog(self.Page)
        #
        self.urlChanged.connect(self.fdialog.clear)
        # # connecting signals
        # self.profile.downloadRequested.connect(self.download)
        self.Page.featurePermissionRequested.connect(lambda orig, ft: self.Page.setFeaturePermission(orig, ft, 0))  # 0 means denied
        #
        # javascript custom code
        if prof['js']:
                self.Page.runJavaScript(prof['js'])
        if prof['jsready']:
            def jsready():
                if self._urls:
                    i = self.getCurrentPageIndex()
                    nexturl = self._urls[i+1]  if      i + 1 < len(self._urls) else ''
                    prevurl = self._urls[i-1]  if 0 <= i - 1                   else ''
                    # print('next', nexturl)
                    # print('prev', prevurl)
                urls = f"const epread_next_url = '{nexturl}'; const epread_prev_url = '{prevurl}';\n"
                self.Page.runJavaScript(urls+prof['jsready'])
            self.Page.loadFinished.connect(jsready)
        #
        if prof['mempos']:
            conn = None
            def _s():
                self.setPageViewPort(prof['posx'], prof['posy'], prof['zoom'])
                QObject.disconnect(conn)
            conn = self.Page.loadFinished.connect(_s)


    def cssDialog(self):
        self.ccssdialog.show()

    def assignCustomCss(self, css):
        self.customCss = css.replace('\n', ' ')
        self.applyCustomCss()

    def getCustomCss(self):
        return self.customCss

    def applyCustomCss(self):
        if self.customCss is not None:
            self.Page.runJavaScript('''{
                    let css
                    if (css = document.getElementById("addedByEpreadToAllowUsersToApplyCustomCssStyles")) {
                        css.innerHTML = "'''+self.customCss+'''"
                    }
                    else {
                        css = document.createElement("style")
                        css.type = "text/css"
                        css.id = "addedByEpreadToAllowUsersToApplyCustomCssStyles"
                        css.innerHTML = "'''+self.customCss+'''"
                        document.body.appendChild(css)
                    }
                }''')

    def clearInvertColors(self):
        self.Page.runJavaScript('''{
                let e = document.getElementById("addedByEpreadForInvertingColors")
                if (e) { e.innerHTML = "" }
            }''')

    def makeInvertColors(self):
        self.Page.runJavaScript('''{
                let css
                if (css = document.getElementById("addedByEpreadForInvertingColors")) {
                    css.innerHTML = "'''+self.darkcss+'''"
                }
                else {
                    css = document.createElement("style")
                    css.type = "text/css"
                    css.id = "addedByEpreadForInvertingColors"
                    css.innerHTML = "'''+self.darkcss+'''"
                    document.body.appendChild(css)
                }
            }''')

    # connect to page.loadFinished
    def updateInvertColors(self):
        if self.inverted:
            self.makeInvertColors()
        else:
            self.clearInvertColors()

    def toggleInvertColors(self):
        if self.inverted:
            self.clearInvertColors()
            self.inverted = False
        else:
            self.makeInvertColors()
            self.inverted = True

    def getPageViewPort(self):
        p = self.Page.scrollPosition()
        zf = self.Page.zoomFactor()
        return (p.x(), p.y(), zf)

    def setPageViewPort(self, px, py, zf):
        self.Page.setZoomFactor(zf if zf is not None else 1)
        self.Page.runJavaScript(f'window.scrollTo({px}, {py});')


    def download(self, d):
        print(txt.downloadPath.format(d.path()))
        d.accept()

    def saveAsPdf(self):
        filename = QFileDialog.getSaveFileName(self, txt.savepdfTitle, filter='*.pdf')[0]
        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'
        self.Page.printToPdf(filename)

    def isMuted(self): self.Page.isAudioMuted()
    def setMuted(self, new): self.Page.setAudioMuted(new)

    def zoomIn(self):  self.setZoomFactor(self.zoomFactor() * 1.10)
    def zoomOut(self): self.setZoomFactor(self.zoomFactor() * 0.90)
    def zoomReset(self): self.setZoomFactor(1.00)
    def findDialog(self): self.fdialog.show()
    def findNext(self): self.fdialog.next()
    def findPrev(self): self.fdialog.prev()
    def findClear(self): self.fdialog.clear()
    # def copyUrl(self): QGuiApplication.clipboard().setText(self.url().toString())
    # def pasteUrl(self): self.setUrl(QUrl( QGuiApplication.clipboard().text() ))

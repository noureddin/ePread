# -*- coding: utf-8 -*-
# vim: set et sw=4 ts=4 :

from configparser import ConfigParser

# for keys
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QKeySequence

DEFAULT_CONFIG = '''[DEFAULT]
trayMsgDuration: 1000
useTray: True
'''

DEFAULT_HOTKEYS = '''[DEFAULT]
; "keys" are case-insensitive, but "values" are not
; f5 is F5, Ctrl+R is ctrl+r
; but Reload instead of reload is ERROR
; TODO: surf-like shortcuts too? and shorcut profiles?
; TODO: https://support.mozilla.org/en-US/kb/keyboard-shortcuts-perform-firefox-tasks-quickly
Ctrl+R: reload
F5: reload
Escape: stop
Alt+Home: homePage
Alt+End: endPage
Alt+Left: back
Ctrl+H: back
Alt+Right: forward
Ctrl+L: forward
Ctrl++: zoomIn
Ctrl+-: zoomOut
Ctrl+0: zoomReset
Shift+Ctrl+i: invert
Shift+Ctrl+S: styleDialog
Ctrl+F: findDialog
/: findDialog
F3: findNext
Ctrl+G: findNext
Shift+F3: findPrev
Shift+Ctrl+G: findPrev
Shift+Ctrl+H: findClear
Shift+Ctrl+M: showHide
Ctrl+P: saveAsPdf
F1: toggleMute
Ctrl+Q: quit
Shift+Ctrl+Q: quit
Ctrl+W:  quit  ; or closeToTray
Ctrl+F4: quit  ; or closeToTray
'''

EPUB_JSREADY = '''{
const body = document.getElementsByTagName('body')[0];
// word count
const words = body.innerHTML.replace(/<br>/gi, ' ').replace(/<[^>]+>/g, '').split(/\s+/).length;
const WPM = 265;
const mins = Math.round(words/WPM);
const wpm_content = words > WPM? `${words} words = ${mins} minutes` : '';
// next & prev btns
const prevbtn = !epread_prev_url? '' : '<a href="'+epread_prev_url+'">Prev</a>'
const nextbtn = !epread_next_url? '' : '<a href="'+epread_next_url+'">Next</a>'
// all put together
const css = `<style>
    #EpreadBars:nth-child(2) { margin-bottom: 1em } /* because <style> is first */
    #EpreadBars:last-child   { margin-top:    1em }
    #EpreadBars { /* table */
        width: 100%;
        border: none;
        background: linear-gradient(0deg, blue -400%, lightblue) !important;
    }
    #EpreadBars * {
        background: none !important;
    }
    #EpreadBars .btn {
        padding: 0.5em;
    }
    #EpreadBars .btn a {
        color: hotpink !important;
        text-shadow: 0 0 0.2em white;
    }
    #EpreadBars .btn a:hover,
    #EpreadBars .btn a:focus {
        color: fuchsia !important;
    }
    #EpreadBars .btn a:active {
        color: pink !important;
        text-shadow: 0 0 0.1em magenta;
    }
    #EpreadBars prev { text-align: left  }
    #EpreadBars next { text-align: right }
    #EpreadBars td:nth-child(2) {  /* wpm */
        font-size: 0.75em;
        padding: 1em;
        text-align: center;
        color: magenta !important;
        width: 100%;
    }
</style>`
const prevbtn_td = `<td class="btn prev">${prevbtn}</td>`
const nextbtn_td = `<td class="btn next">${nextbtn}</td>`
const wpm_td = `<td>${wpm_content}</td>`
const emp_td = `<td></td>`
const head_bar = `<table id="EpreadBars"><tr>${prevbtn_td}${wpm_td}${nextbtn_td}</tr></table>`
const foot_bar = `<table id="EpreadBars"><tr>${prevbtn_td}${emp_td}${nextbtn_td}</tr></table>`
body.innerHTML = css + head_bar + body.innerHTML + foot_bar
}'''


class Storage:

    def __init__(self, name):
        import os
        # (XDG_DATA_HOME || ~/.local/share) + ./NAME
        self.DATA_DIR = os.path.join(os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share")), name)
        self.HIST_INI = os.path.join(self.DATA_DIR, 'history')
        self.CONF_INI = os.path.join(self.DATA_DIR, 'config')
        self.KEYS_INI = os.path.join(self.DATA_DIR, 'keys')

        if not os.path.exists(self.DATA_DIR):
            os.mkdir(self.DATA_DIR)

        if not os.path.exists(self.KEYS_INI):
            with open(self.KEYS_INI, 'w') as f:
                print(DEFAULT_HOTKEYS, file=f)

        if not os.path.exists(self.CONF_INI):
            with open(self.CONF_INI, 'w') as f:
                print(DEFAULT_CONFIG, file=f)


    def __read(self, file, section='DEFAULT', **kw):
        cnf = ConfigParser(**kw); cnf.read(file)
        if section is None:
            return cnf
        else:
            return cnf[section] if section in cnf else None


    def getAllHistory(self):
        return self.__read(self.HIST_INI, section=None, interpolation=None)
        # no interpolation, so we can use '%' in urls


    def getConfig(self):
        c = self.__read(self.CONF_INI)
        return {
                'traymsgdur': c.getint('trayMsgDuration', 1000),
                'usetray': c.getboolean('useTray', True),
        }


    def bindShortcutsToWindow(self, win, keyAction):

        def bindShortcut(key, act):
            QShortcut(QKeySequence(key), win).activated.connect(act)
        
        for key, act in self.__read(self.KEYS_INI).items():
            bindShortcut(key, keyAction[act])

        try:  # they are not defined if a single url is given
            # these two are currently non-overridable
            # bindShortcut('Space', win.view.scrollUp)
            # bindShortcut('Shift+Space', win.view.scrollDown)
            bindShortcut('Left', win.view.prevPage)
            bindShortcut('Right', win.view.nextPage)
            # TODO: defaults that are overridable without having them in the ini-file?
        except:
            pass


    def getHistory(self, name):
        c = self.getAllHistory()
        h = c[name] if name in c else None

        ret = {
                'startidx': 0,
                'js': None,
                'jsready': EPUB_JSREADY,
                'title': '',
                'css': None,
                # 'css': 'html { margin: 1em; } img { max-width: 100%; height: auto !important; } * { line-height: 1.5; }',
                'dark': '* { color: white !important; background-color: #111; } a { color: lightblue !important; } img { filter: invert(1); } #EpreadBars { background: linear-gradient(0deg, midnightblue, navy) !important }',
                # 'dark': '* { color: white; background-color: #111; } a { color: blue; } img { filter: invert(1); }'),
                # 'dark': '* { color: #eee; background-color: #000; } img { filter: invert(100%); }'),
                'posx': 0,
                'posy': 0,
                'zoom': 1.0,
                'mempos': True, # on quit, update the posx/posy fields with the current ones
                'memurl': True, # on quit, update the url field with the current one
                'memcss': True, # on quit, update the css field with the current one
                'invertcolors': False, # is the darkmode applied?
            }

        def __get(key, fn, name):
            val = fn(name, None)
            if val is not None:
                ret[key] = val

        if h is not None:
            __get('startidx',      h.getint,      'StartingIndex')
            __get('js',            h.get,         'JS')
            __get('jsready',       h.get,         'JSReady')
            __get('css',           h.get,         'CSS')
            __get('dark',          h.get,         'DarkMode')
            __get('posx',          h.getint,      'HorizontalScrollPosition')
            __get('posy',          h.getint,      'VerticalScrollPosition')
            __get('zoom',          h.getfloat,    'ZoomFactor')
            __get('mempos',        h.getboolean,  'RememberScrollPosition')
            __get('memurl',        h.getboolean,  'RememberURL')
            __get('memcss',        h.getboolean,  'RememberCSS')
            __get('invertcolors',  h.getboolean,  'InvertColors')

        return ret


    def updateProfile(self, profileId, **kw):
        # read
        prof = self.getAllHistory()
        if profileId not in prof:
            prof[profileId] = {}
        # modify
        if kw.get('startidx')      is not None:  prof[profileId]['StartingIndex']            =          kw.get('startidx')
        if kw.get('posx')          is not None:  prof[profileId]['HorizontalScrollPosition'] = str(int( kw.get('posx') ))
        if kw.get('posy')          is not None:  prof[profileId]['VerticalScrollPosition']   = str(int( kw.get('posy') ))
        if kw.get('zoom')          is not None:  prof[profileId]['ZoomFactor']               = str(     kw.get('zoom') )
        if kw.get('invertcolors')  is not None:  prof[profileId]['InvertColors']             =          kw.get('invertcolors')
        if kw.get('mempos')        is not None:  prof[profileId]['RememberScrollPosition']   =          kw.get('mempos')
        if kw.get('memurl')        is not None:  prof[profileId]['RememberURL']              =          kw.get('memurl')
        if kw.get('memcss')        is not None:  prof[profileId]['RememberCSS']              =          kw.get('memcss')
        if kw.get('memcss')        is not None and \
           kw.get('css')           is not None:  prof[profileId]['CSS']                      =          kw.get('css')
        # write
        with open(self.HIST_INI, 'w') as profilesfile:
            prof.write(profilesfile)


    def deleteProfile(self, profileId):
        # read
        prof = self.getAllHistory()
        if profileId not in prof: return
        # modify
        del prof[profileId]
        # write
        with open(self.HIST_INI, 'w') as profilesfile:
            prof.write(profilesfile)

# -*- coding: utf-8 -*-
# vim: set sw=2 ts=2 noet:

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from txt import txt

class CustomCssDialog(QDialog):

    submit = pyqtSignal(str)

    def __init__(self, text=None, *args, **kwargs):
        super().__init__(*args, sizeGripEnabled=True, **kwargs)
        txtopts = { 'placeholderText':txt.ccssPlaceholder }
        self.setWindowTitle(txt.ccssTitle)
        self.vb    = QVBoxLayout();             self.setLayout(self.vb)
        self.text  = QPlainTextEdit(**txtopts); self.vb.addWidget(self.text)
        self.hb    = QHBoxLayout();             self.vb.addLayout(self.hb)
        self.okbtn = QPushButton(txt.ccssOk);   self.hb.addWidget(self.okbtn)
        self.nobtn = QPushButton(txt.ccssNo);   self.hb.addWidget(self.nobtn)
        if text is not None:
            self.text.setPlainText(text)
        def ok():
            self.submit.emit(self.text.toPlainText())
            self.accept()
        self.okbtn.clicked.connect(ok)
        self.nobtn.clicked.connect(self.rejected.emit)
        self.rejected.connect(self.hide)




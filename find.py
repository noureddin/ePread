# -*- coding: utf-8 -*-
# vim: set et sw=4 ts=4 :

from PyQt5.QtWidgets import (
        QDialog,
        QHBoxLayout,
        QCheckBox,
        QLineEdit,
)

from txt import txt

class FindDialog(QDialog):

    def __init__(self, page, *args, **kwargs):
        super(FindDialog, self).__init__(*args, sizeGripEnabled=True, **kwargs)
        self.page = page
        self.text = QLineEdit(placeholderText=txt.findPlaceholder)
        self.case = QCheckBox(text=txt.findMatchCase)
        self.hb = QHBoxLayout()
        self.hb.addWidget(self.text)
        self.hb.addWidget(self.case)
        self.setLayout(self.hb)
        self.setWindowTitle(txt.findTitle)
        #
        self.text.textChanged.connect(self.next)
        self.case.stateChanged.connect(self.next)

    def next(self):
        if self.case.checkState():
            self.page.findText(self.text.text(), self.page.FindCaseSensitively)
        else:
            self.page.findText(self.text.text())

    def prev(self):
        if self.case.checkState():
            self.page.findText(self.text.text(), self.page.FindCaseSensitively | self.page.FindBackward)
        else:
            self.page.findText(self.text.text(), self.page.FindBackward)

    def clear(self): self.page.findText('')



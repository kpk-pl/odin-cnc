#!/usr/bin/env python

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt

class QHistoryLineEdit(QtGui.QLineEdit):
    def __init__(self, depth = 50, parent=None):
        super(QHistoryLineEdit, self).__init__(parent)
        self.returnPressed.connect(self.saveLine)
        self.history = []
        self.iterator = 0
        self.depth = depth
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            if self.iterator != 0:
                self.iterator -= 1
            if self.iterator < len(self.history):
                self.setText(self.history[self.iterator])
        elif event.key() == Qt.Key_Down:
            if self.iterator < len(self.history)-1:
                self.iterator += 1
            if self.iterator < len(self.history):
                self.setText(self.history[self.iterator])
        else:
            super(QHistoryLineEdit, self).keyPressEvent(event)

    @QtCore.pyqtSlot()
    def saveLine(self):
        txt = self.text()
        if txt != "":
            if len(self.history) > 0 and self.history[-1] == txt:
                return
            self.history.append(txt)
            if len(self.history) > self.depth:
                self.history.pop(0)
            self.iterator = len(self.history)
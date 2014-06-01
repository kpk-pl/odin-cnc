#!/usr/bin/env python

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt

import Logger

class TrajectoryTab(QtGui.QWidget):
    trajectoryFileChosen = QtCore.pyqtSignal(str)
    
    def __init__(self, parent=None):
        super(TrajectoryTab, self).__init__(parent)
        
        layout = QtGui.QVBoxLayout()
        layout.setMargin(10)
        self.setLayout(layout)
        
        self.trajectoryPathFileLabel = QtGui.QLabel()
        self.trajectoryPathFileChoose = QtGui.QPushButton("Choose")
        layout.addWidget(self.trajectoryPathFileLabel)
        layout.addWidget(self.trajectoryPathFileChoose)
        
        self.trajectoryPathFileChoose.clicked.connect(self.trajectoryPathFileClicked)
        
        
    def trajectoryPathFileClicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self, "Choose trajectory file", '')
        if fileName:
            self.trajectoryPathFileLabel.setText(fileName)
            self.trajectoryFileChosen.emit(fileName)
            Logger.getInstance.debug("Trajectory file chosen: " + fileName)
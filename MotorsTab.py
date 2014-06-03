#!/usr/bin/env python

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
import numpy as np
import pyqtgraph as pg
import math
from datetime import datetime

from Logger import Logger
from QLevelBar import QLevelBar

class MotorsTab(QtGui.QWidget):
    
    def __init__(self, parent=None):
        super(MotorsTab, self).__init__(parent)
        
        self.setupGUI()
        
    def resetDefault(self):
        for bar in [self.LSpeedActBar, self.RSpeedActBar, self.LSpeedSetBar, self.RSpeedSetBar]:
            bar.setValue(0.0)
        
    def setupGUI(self):
        # main layout
        layout = QtGui.QHBoxLayout()
        layout.setMargin(10)
        self.setLayout(layout)
        leftSideWdgt = QtGui.QWidget()
        leftSideWdgt.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
        leftSideWdgt.setFixedWidth(160);
        rightSideWdgt = QtGui.QTabWidget()
        layout.addWidget(leftSideWdgt)
        layout.addWidget(rightSideWdgt)
        
        # tabs for right panel
        self.telemetryTab = QtGui.QWidget()
        self.settingsTab = QtGui.QWidget()
        rightSideWdgt.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        rightSideWdgt.addTab(self.telemetryTab, "Telemetry")
        rightSideWdgt.addTab(self.settingsTab, "Settings")   
        
        # left layout
        leftLayout = QtGui.QVBoxLayout()
        leftLayout.setMargin(0)
        leftSideWdgt.setLayout(leftLayout)
        
        # speed bars
        self.LSpeedActBar = QLevelBar(-8, 8, 0)
        self.RSpeedActBar = QLevelBar(-8, 8, 0)
        self.LSpeedSetBar = QLevelBar(-8, 8, 0)
        self.LSpeedSetBar.setColor(QtGui.QColor(255,0,0,200))
        self.RSpeedSetBar = QLevelBar(-8, 8, 0)
        self.RSpeedSetBar.setColor(QtGui.QColor(255,0,0,200))
        for bar in [self.LSpeedActBar, self.RSpeedActBar, self.LSpeedSetBar, self.RSpeedSetBar]:
            bar.setOrientation(Qt.Vertical)
            bar.setMinimumHeight(120)
        speedLayout = QtGui.QGridLayout()
        speedLayout.setMargin(0)
        llabel = QtGui.QLabel("Left\n[rad/s]")
        rlabel = QtGui.QLabel("Right\n[rad/s]")
        llabel.setAlignment(Qt.AlignCenter)
        rlabel.setAlignment(Qt.AlignCenter)
        speedLayout.addWidget(llabel, 0, 0, 1, 2)
        speedLayout.addWidget(rlabel, 0, 2, 1, 2)
        speedLayout.addWidget(self.LSpeedActBar, 1, 0, 1, 1)
        speedLayout.addWidget(self.LSpeedSetBar, 1, 1, 1, 1)
        speedLayout.addWidget(self.RSpeedActBar, 1, 2, 1, 1)
        speedLayout.addWidget(self.RSpeedSetBar, 1, 3, 1, 1)
        leftLayout.addLayout(speedLayout)
        
        # end
        leftLayout.addStretch(1)
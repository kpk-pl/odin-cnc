#!/usr/bin/env python

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
import numpy as np
import pyqtgraph as pg
import math
from datetime import datetime

from Logger import Logger

class MotorsTab(QtGui.QWidget):
    
    def __init__(self, parent=None):
        super(MotorsTab, self).__init__(parent)
        
        self.setupGUI()
        
    def setupGUI(self):
        # main layout
        layout = QtGui.QHBoxLayout()
        layout.setMargin(10)
        self.setLayout(layout)
        leftSideWdgt = QtGui.QWidget()
        leftSideWdgt.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
        leftSideWdgt.setFixedWidth(250);
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
        
        # end
        leftLayout.addStretch()
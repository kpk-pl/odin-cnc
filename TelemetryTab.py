#!/usr/bin/env python

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
import math

import Logger

class TelemetryTab(QtGui.QWidget):
    telemetryRefreshChanged = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super(TelemetryTab, self).__init__(parent)
        
        self.setupGUI()
        
        @QtCore.pyqtSlot() 
        def statsRequests():
            self.sendComm(["system cpu", "system memory", "system battery"])
        self.statsRefreshTimer = QtCore.QTimer()
        self.statsRefreshTimer.timeout.connect(statsRequests)
        
        self.plotRefreshMode.currentIndexChanged['QString'].connect(self.plotModeChanged)
        self.plotRefreshTime.returnPressed.connect(self.plotRefreshTimeChanged)
        self.plotLimitTime.returnPressed.connect(self.plotLimitTimeChanged)
        
    @QtCore.pyqtSlot(QtCore.QString)    
    def plotModeChanged(self, choice):   
        if str(choice) == "Time":
            self.plotRefreshTime.setEnabled(True)
            val = self.plotRefreshTime.text()
            if self.plotRefreshTime.validator().validate(val, 0):
                self.telemetryRefreshChanged.emit(int(str(val)))
        else:
            self.plotRefreshTime.setEnabled(False)
            if str(choice) == "On change":
                self.telemetryRefreshChanged.emit(-2)
            else:
                self.telemetryRefreshChanged.emit(-1)
            
    @QtCore.pyqtSlot()
    def plotRefreshTimeChanged(self):
        val = self.plotRefreshTime.text()
        if self.plotRefreshTime.validator().validate(val, 0):
            self.telemetryRefreshChanged.emit(int(str(val)))
        
    @QtCore.pyqtSlot()
    def plotLimitTimeChanged(self):
        val = self.plotLimitTime.text()
        # TODO
        
    @QtCore.pyqtSlot(tuple)
    def updateTelemetry(self, update):
        self.statsXEdit.setText(str(update[0]))
        self.statsYEdit.setText(str(update[1]))
        self.statsORawDegEdit.setText(str(update[2]))
        self.statsORawRadEdit.setText("%.3f" % (update[2]*math.pi/180.0))
        t = int((update[2]+180.0)/360.0)
        v = update[2]-360.0*t
        self.statsONormDegEdit.setText(str(v))
        self.statsONormRadEdit.setText("%.3f" % (v*math.pi/180.0))
        self.statsTimestampEdit.setText(str(update[3]))
        
    def resetDefault(self):
        self.statsXEdit.setText("?")
        self.statsYEdit.setText("?")
        self.statsORawDegEdit.setText("?")
        self.statsONormDegEdit.setText("?")
        self.statsORawRadEdit.setText("?")
        self.statsONormRadEdit.setText("?")
        self.statsTimestampEdit.setText("?")
        self.plotRefreshMode.setCurrentIndex(0)
        self.plotRefreshTime.setEnabled(False)
        self.plotRefreshTime.setText("1000")
        self.plotLimitTime.setText("60")
        self.trajectoryAutoloadCheck.setChecked(False)
        self.trajectoryDrivingCommandsCheck.setChecked(False)
        self.trajectoryHistoryEdit.setText("1")

    def setupGUI(self):
        # main layout
        layout = QtGui.QHBoxLayout()
        layout.setMargin(10)
        self.setLayout(layout)
        leftSideWdgt = QtGui.QWidget()
        leftSideWdgt.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
        leftSideWdgt.setFixedWidth(250);
        plotWdgt = QtGui.QWidget()
        layout.addWidget(leftSideWdgt)
        layout.addWidget(plotWdgt)
        
        # left layout
        leftLayout = QtGui.QVBoxLayout()
        layout.setMargin(0)
        leftSideWdgt.setLayout(leftLayout)
        
        # stats
        self.statsXEdit = QtGui.QLineEdit()
        self.statsYEdit = QtGui.QLineEdit()
        self.statsORawDegEdit = QtGui.QLineEdit()
        self.statsONormDegEdit = QtGui.QLineEdit()
        self.statsORawRadEdit = QtGui.QLineEdit()
        self.statsONormRadEdit = QtGui.QLineEdit()
        self.statsTimestampEdit = QtGui.QLineEdit()
        self.statsXEdit.setReadOnly(True)
        self.statsYEdit.setReadOnly(True)
        self.statsORawDegEdit.setReadOnly(True)
        self.statsONormDegEdit.setReadOnly(True)
        self.statsORawRadEdit.setReadOnly(True)
        self.statsONormRadEdit.setReadOnly(True)
        self.statsTimestampEdit.setReadOnly(True)
        
        statsBox = QtGui.QGroupBox("Stats")
        statsLayout = QtGui.QGridLayout()
        statsLayout.setSpacing(3)
        statsLayout.setMargin(5)
        statsLayout.addWidget(QtGui.QLabel(" X "), 0, 0, 1, 1)
        statsLayout.addWidget(self.statsXEdit, 0, 1, 1, 5)
        statsLayout.addWidget(QtGui.QLabel("[mm]"), 0, 6, 1, 1)
        
        statsLayout.addWidget(QtGui.QLabel(" Y "), 1, 0, 1, 1)
        statsLayout.addWidget(self.statsYEdit, 1, 1, 1, 5)
        statsLayout.addWidget(QtGui.QLabel("[mm]"), 1, 6, 1, 1)
        
        statsLayout.addWidget(QtGui.QLabel(" O "), 2, 0, 2, 1)
        statsLayout.addWidget(self.statsONormDegEdit, 2, 1, 1, 2)
        statsLayout.addWidget(self.statsORawDegEdit, 3, 1, 1, 2)
        statsLayout.addWidget(QtGui.QLabel("[deg]"), 2, 3, 2, 1)
        statsLayout.addWidget(self.statsONormRadEdit, 2, 4, 1, 2)
        statsLayout.addWidget(self.statsORawRadEdit, 3, 4, 1, 2)
        statsLayout.addWidget(QtGui.QLabel("[rad]"), 2, 6, 2, 1)
        
        statsLayout.addWidget(QtGui.QLabel("Timestamp"), 4, 0, 1, 2)
        statsLayout.addWidget(self.statsTimestampEdit, 4, 2, 1, 5)
        statsBox.setLayout(statsLayout)
        leftLayout.addWidget(statsBox)
        
        # plot left
        self.plotRefreshMode = QtGui.QComboBox()
        self.plotRefreshMode.addItems(["Disable", "On change", "Time"])
        self.plotRefreshTime = QtGui.QLineEdit()
        self.plotRefreshTime.setValidator(QtGui.QIntValidator(10, 600000))
        self.plotLimitTime = QtGui.QLineEdit()
        self.plotLimitTime.setValidator(QtGui.QIntValidator(1, 600))
        
        plotBox = QtGui.QGroupBox("Plot")
        plotLayout = QtGui.QGridLayout()
        plotLayout.setSpacing(3)
        plotLayout.setMargin(5)
        plotLayout.addWidget(QtGui.QLabel("Refresh mode"), 0, 0, 1, 1)
        plotLayout.addWidget(self.plotRefreshMode, 0, 1, 1, 2)
        plotLayout.addWidget(QtGui.QLabel("Refresh time"), 1, 0, 1, 1)
        plotLayout.addWidget(self.plotRefreshTime, 1, 1, 1, 1)
        plotLayout.addWidget(QtGui.QLabel("[ms]"), 1, 2, 1, 1)
        plotLayout.addWidget(QtGui.QLabel("Time history"), 2, 0, 1, 1)
        plotLayout.addWidget(self.plotLimitTime, 2, 1, 1, 1)
        plotLayout.addWidget(QtGui.QLabel("[s]"), 2, 2, 1, 1)
        plotBox.setLayout(plotLayout)
        leftLayout.addWidget(plotBox)
        
        # trajectory
        self.trajectoryDrivingCommandsCheck = QtGui.QCheckBox("Plot driving commands")
        self.trajectoryLoadTrajectoryButton = QtGui.QPushButton("Load trajectory")
        self.trajectoryAutoloadCheck = QtGui.QCheckBox("Autoload")
        self.trajectoryHistoryEdit = QtGui.QLineEdit()
        self.trajectoryHistoryEdit.setValidator(QtGui.QIntValidator(1, 100))
        self.trajectoryLoadFromFileButton = QtGui.QPushButton("Load from csv")
        self.trajectoryCleanButton = QtGui.QPushButton("Clean all")
        
        trajectoryBox = QtGui.QGroupBox("Trajectory")
        trajectoryLayout = QtGui.QGridLayout()
        trajectoryLayout.setSpacing(3)
        trajectoryLayout.setMargin(5)
        trajectoryLayout.setColumnStretch(0, 1)
        trajectoryLayout.setColumnStretch(1, 1)
        trajectoryLayout.addWidget(self.trajectoryLoadTrajectoryButton, 0, 0, 1, 1)
        trajectoryLayout.addWidget(self.trajectoryAutoloadCheck, 0, 1, 1, 1)
        trajectoryLayout.addWidget(QtGui.QLabel("History"), 1, 0, 1, 1)
        trajectoryLayout.addWidget(self.trajectoryHistoryEdit, 1, 1, 1, 1)
        trajectoryLayout.addWidget(self.trajectoryDrivingCommandsCheck, 2, 0, 1, 2)
        trajectoryLayout.addWidget(self.trajectoryLoadFromFileButton, 3, 0, 1, 1)
        trajectoryLayout.addWidget(self.trajectoryCleanButton, 3, 1, 1, 1)
        trajectoryBox.setLayout(trajectoryLayout)
        leftLayout.addWidget(trajectoryBox)
        
        # end
        leftLayout.addStretch()
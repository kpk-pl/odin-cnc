#!/usr/bin/env python

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
import numpy as np
import pyqtgraph as pg
import math
from datetime import datetime

from Logger import Logger

class TelemetryTab(QtGui.QWidget):
    telemetryRefreshChanged = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super(TelemetryTab, self).__init__(parent)
        
        self.plotting = False
        self.telemetryPlotData = []
        self.plotHistoryS = 60
        
        self.setupGUI()
        
        @QtCore.pyqtSlot() 
        def statsRequests():
            self.sendComm(["system cpu", "system memory", "system battery"])
        self.statsRefreshTimer = QtCore.QTimer()
        self.statsRefreshTimer.timeout.connect(statsRequests)
        
        self.plotRefreshMode.currentIndexChanged['QString'].connect(self.plotModeChanged)
        self.plotRefreshTime.sigValueChanged.connect(self.plotRefreshTimeChanged)
        self.plotLimitTime.sigValueChanged.connect(self.plotLimitTimeChanged)
        
    @QtCore.pyqtSlot(QtCore.QString)    
    def plotModeChanged(self, choice):   
        if str(choice) == "Time":
            self.plotRefreshTime.setEnabled(True)
            self.telemetryRefreshChanged.emit(int(self.plotRefreshTime.value()*1000))
        else:
            self.plotRefreshTime.setEnabled(False)
            if str(choice) == "On change":
                self.telemetryRefreshChanged.emit(-2)
            else:
                self.telemetryRefreshChanged.emit(-1)
                
        if str(choice) == "Disable":
            self.plotting = False
        else:
            if not self.plotting:
                self.plotting = True
                self.telemetryPlot.clear()
            
    @QtCore.pyqtSlot()
    def plotRefreshTimeChanged(self):
        if self.plotRefreshMode.currentText() == "Time":
            val = self.plotRefreshTime.value()
            self.telemetryRefreshChanged.emit(int(val*1000))
        
    @QtCore.pyqtSlot()
    def plotLimitTimeChanged(self):
        self.plotHistoryS = self.plotLimitTime.value()
        
    @QtCore.pyqtSlot(tuple)
    def updateTelemetry(self, update):
        self.statsXEdit.setText(str(update[0]))
        self.statsYEdit.setText(str(update[1]))
        self.statsORawDegEdit.setText(str(update[2]))
        r = math.radians(update[2])
        self.statsORawRadEdit.setText("%.3f" % (r))
        t = int((update[2]+180.0)/360.0)
        v = update[2]-360.0*t
        self.statsONormDegEdit.setText(str(v))
        self.statsONormRadEdit.setText("%.3f" % (math.radians(v)))
        self.statsTimestampEdit.setText(str(update[3]))
        
        #update plot
        if self.plotting:
            x = update[0]/1000.0
            y = update[1]/1000.0
            self.telemetryPlotData.append((x, y, update[3]))
            now = datetime.now()
            while len(self.telemetryPlotData) > 0 and \
                        (now - self.telemetryPlotData[0][2]).total_seconds() > self.plotHistoryS:
                self.telemetryPlotData.pop(0)
            self.telemetryPlot.setData([d[0] for d in self.telemetryPlotData], [d[1] for d in self.telemetryPlotData])
            
            self.orientationPlot.clear()
            self.orientationPlot.setData([x,x+0.1*math.cos(r)],[y,y+0.1*math.sin(r)])
        
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
        self.plotRefreshTime.setValue(0.1)
        self.trajectoryAutoloadCheck.setChecked(False)
        self.trajectoryDrivingCommandsCheck.setChecked(False)
        self.trajectoryHistoryEdit.setValue(1)
        self.telemetryPlot.clear()
        self.orientationPlot.clear()
        self.plotting = False
        self.telemetryPlotData = []
        self.plotHistoryS = 60
        self.plotLimitTime.setValue(self.plotHistoryS)

    def setupGUI(self):
        # main layout
        layout = QtGui.QHBoxLayout()
        layout.setMargin(10)
        self.setLayout(layout)
        leftSideWdgt = QtGui.QWidget()
        leftSideWdgt.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
        leftSideWdgt.setFixedWidth(250);
        plotWdgt = pg.PlotWidget()
        layout.addWidget(leftSideWdgt)
        layout.addWidget(plotWdgt)
        
        # plot customization
        plotWdgt.setRange(xRange=(-1,1), yRange=(-1,1), padding=0.02, disableAutoRange=True)
        plotWdgt.setAspectLocked(lock=True, ratio=1)
        plotWdgt.showGrid(x=True, y=True)
        plotWdgt.setLabel('left', 'Y', units='m')
        plotWdgt.setLabel('bottom', 'X', units='m')
        self.telemetryPlot = plotWdgt.plot()
        self.telemetryPlot.setPen((0, 0, 255))
        self.orientationPlot = plotWdgt.plot()
        self.orientationPlot.setPen((255,0,0))
        
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
        self.plotRefreshTime = pg.SpinBox(bounds=[0.01,None], dec=True, minStep=0.01, step=0.01, suffix='s', siPrefix=True)
        self.plotLimitTime = pg.SpinBox(bounds=[1,None], int=True, dec=True, minStep=1, step=1, suffix='s', siPrefix=True)
        
        plotBox = QtGui.QGroupBox("Plot")
        plotLayout = QtGui.QGridLayout()
        plotLayout.setSpacing(3)
        plotLayout.setMargin(5)
        plotLayout.addWidget(QtGui.QLabel("Refresh mode"), 0, 0, 1, 1)
        plotLayout.addWidget(self.plotRefreshMode, 0, 1, 1, 1)
        plotLayout.addWidget(QtGui.QLabel("Refresh time"), 1, 0, 1, 1)
        plotLayout.addWidget(self.plotRefreshTime, 1, 1, 1, 1)
        plotLayout.addWidget(QtGui.QLabel("Time history"), 2, 0, 1, 1)
        plotLayout.addWidget(self.plotLimitTime, 2, 1, 1, 1)
        plotBox.setLayout(plotLayout)
        leftLayout.addWidget(plotBox)
        
        # trajectory
        self.trajectoryDrivingCommandsCheck = QtGui.QCheckBox("Plot driving commands")
        self.trajectoryLoadTrajectoryButton = QtGui.QPushButton("Load trajectory")
        self.trajectoryAutoloadCheck = QtGui.QCheckBox("Autoload")
        self.trajectoryHistoryEdit = pg.SpinBox(bounds=[1,100], int=True, dec=True, minStep=1, step=1)
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
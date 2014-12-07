#!/usr/bin/env python

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt

from COMMngr import COMMngr
from Logger import Logger
import QLevelBar

class LeftPanel(QtGui.QWidget):
    connectRequested = QtCore.pyqtSignal(tuple)
    statsRefreshChanged = QtCore.pyqtSignal(int)
    telemetryRefreshChanged = QtCore.pyqtSignal(int)
    
    def __init__(self):
        super(LeftPanel, self).__init__()
       
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
        self.setFixedWidth(250);
        layout = QtGui.QVBoxLayout()
        layout.setMargin(0)
        self.setLayout(layout)
        
        self.connMode = "WiFi"
        
        ### CONNECTION FRAME
        self.wifiRadio = QtGui.QRadioButton("WiFi")
        self.usbRadio = QtGui.QRadioButton("COM")
        self.wifiRadio.setChecked(True)
        self.ipLabel = QtGui.QLabel("IP")
        self.portLabel = QtGui.QLabel("Port")
        self.ipEdit = QtGui.QLineEdit()
        self.ipEdit.setText("192.168.50.2")
        self.portEdit = QtGui.QLineEdit()
        self.portEdit.setText("4000")
        self.portEdit.setValidator(QtGui.QIntValidator(0, 65535))
        self.comLabel = QtGui.QLabel("COM port")
        self.comSelect = QtGui.QComboBox()
        self.comSpeedLabel = QtGui.QLabel("Baudrate")
        self.comSpeedEdit = QtGui.QLineEdit()
        self.comSpeedEdit.setText("460800")
        self.comSpeedEdit.setValidator(QtGui.QIntValidator(0, 10000000))
        self.connectionLabel = QtGui.QLabel("Connected")
        self.connectionLabel.hide()
        self.connectButton = QtGui.QPushButton("Connect")
        
        connectionFrame = QtGui.QGroupBox("Connection")
        connectionFrameLayout = QtGui.QGridLayout()
        connectionFrameLayout.setSpacing(3)
        connectionFrameLayout.setMargin(5)
        connectionFrameLayout.setColumnStretch(0, 2)
        connectionFrameLayout.setColumnStretch(1, 1)
        connectionFrameLayout.addWidget(self.wifiRadio, 0, 0, 1, 1)
        connectionFrameLayout.addWidget(self.usbRadio, 0, 1, 1, 1)
        connectionFrameLayout.addWidget(self.ipLabel, 1, 0, 1, 1)
        connectionFrameLayout.addWidget(self.portLabel, 1, 1, 1, 1)
        connectionFrameLayout.addWidget(self.ipEdit, 2, 0, 1, 1)
        connectionFrameLayout.addWidget(self.portEdit, 2, 1, 1, 1)
        connectionFrameLayout.addWidget(self.comLabel, 3, 0, 1, 1)
        connectionFrameLayout.addWidget(self.comSpeedLabel, 3, 1, 1, 1)
        connectionFrameLayout.addWidget(self.comSelect, 4, 0, 1, 1)
        connectionFrameLayout.addWidget(self.comSpeedEdit, 4, 1, 1, 1)
        connectionFrameLayout.addWidget(self.connectionLabel, 5, 0, 1, 1)
        connectionFrameLayout.addWidget(self.connectButton, 5, 1, 1, 1)
        connectionFrame.setLayout(connectionFrameLayout)
        layout.addWidget(connectionFrame)
        
        ### STATS FRAME
        self.cpuUsageBar = QLevelBar.QLevelBar(0,100)
        self.cpuUsageBar.setFormat("%.1f")
        self.memoryBar = QLevelBar.QLevelBar(40000, 0)
        self.memoryBar.setFormat("%d")
        self.batteryBar = QLevelBar.QLevelBar(6.3, 8.45)
        
        self.statsFrame = QtGui.QGroupBox("Stats")
        self.statsFrame.setContextMenuPolicy(Qt.CustomContextMenu)
        statsFrameLayout = QtGui.QGridLayout()
        statsFrameLayout.setSpacing(3)
        statsFrameLayout.setMargin(5)
        statsFrameLayout.addWidget(QtGui.QLabel("Battery Voltage [V]"), 0, 0, 1, 1)
        statsFrameLayout.addWidget(self.batteryBar, 0, 1, 1, 1)
        statsFrameLayout.addWidget(QtGui.QLabel("CPU usage [%]"), 1, 0, 1, 1)
        statsFrameLayout.addWidget(self.cpuUsageBar, 1, 1, 1, 1)
        statsFrameLayout.addWidget(QtGui.QLabel("Free memory [kB]"), 2, 0, 1, 1)
        statsFrameLayout.addWidget(self.memoryBar, 2, 1, 1, 1)
        self.statsFrame.setLayout(statsFrameLayout)
        layout.addWidget(self.statsFrame)
        
        ### Telemetry FRAME
        self.posXEdit = QtGui.QLineEdit()
        self.posXEdit.setReadOnly(True)
        self.posYEdit = QtGui.QLineEdit()
        self.posYEdit.setReadOnly(True)
        self.posOrientEdit = QtGui.QLineEdit()
        self.posOrientEdit.setReadOnly(True)
        self.posXEdit.setText("?")
        self.posYEdit.setText("?")
        self.posOrientEdit.setText("?")
        self.leftSpeedBar = QLevelBar.QLevelBar(-8, 8, 0)
        self.rightSpeedBar = QLevelBar.QLevelBar(-8, 8, 0)
        
        self.telemetryFrame = QtGui.QGroupBox("Telemetry")
        self.telemetryFrame.setContextMenuPolicy(Qt.CustomContextMenu)
        telemetryFrameLayout = QtGui.QGridLayout()
        telemetryFrameLayout.setSpacing(3)
        telemetryFrameLayout.setMargin(5)
        telemetryFrameLayout.addWidget(QtGui.QLabel("Position X [mm]"), 0, 0, 1, 1)
        telemetryFrameLayout.addWidget(self.posXEdit, 0, 1, 1, 1)
        telemetryFrameLayout.addWidget(QtGui.QLabel("Position Y [mm]"), 1, 0, 1, 1)
        telemetryFrameLayout.addWidget(self.posYEdit, 1, 1, 1, 1)
        telemetryFrameLayout.addWidget(QtGui.QLabel("Orientation [deg]"), 2, 0, 1, 1)
        telemetryFrameLayout.addWidget(self.posOrientEdit, 2, 1, 1, 1)
        telemetryFrameLayout.addWidget(QtGui.QLabel("Left speed [rad/s]"), 3, 0, 1, 1)
        telemetryFrameLayout.addWidget(self.leftSpeedBar, 3, 1, 1, 1)
        telemetryFrameLayout.addWidget(QtGui.QLabel("Right speed [rad/s]"), 4, 0, 1, 1)
        telemetryFrameLayout.addWidget(self.rightSpeedBar, 4, 1, 1, 1)
        self.telemetryFrame.setLayout(telemetryFrameLayout)
        layout.addWidget(self.telemetryFrame)
        
        ### STRETCH
        layout.addStretch()
        
        ### BOTTOM BUTTONS
        self.resetAllButton = QtGui.QPushButton("Reset application")
        layout.addWidget(self.resetAllButton)
        
        self.createConnections()
        self.resetDefaultValues()
        self.setWiFi()
       
    def createConnections(self):
        self.wifiRadio.clicked.connect(self.setWiFi)
        self.usbRadio.clicked.connect(self.setUSB)
        self.connectButton.clicked.connect(self.connectToTarget)
        self.ipEdit.returnPressed.connect(self.connectToTarget)
        self.portEdit.returnPressed.connect(self.connectToTarget)
        self.comSpeedEdit.returnPressed.connect(self.connectToTarget)
        self.statsFrame.customContextMenuRequested.connect(self.showContextMenuStats)
        self.telemetryFrame.customContextMenuRequested.connect(self.showContextMenuTelemetry)
        
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Shift+C"), self, self.connectToTarget, None)
        
    @QtCore.pyqtSlot(tuple)
    def updateTelemetry(self, telemetry):
        self.posXEdit.setText(str(telemetry[0]))
        self.posYEdit.setText(str(telemetry[1]))
        self.posOrientEdit.setText(str(telemetry[2]))
        
    @QtCore.pyqtSlot(tuple)
    def updateCurrentSpeed(self, speed):
        self.leftSpeedBar.setValue(speed[0])
        self.rightSpeedBar.setValue(speed[1])
        
    @QtCore.pyqtSlot()    
    def setWiFi(self):
        self.ipLabel.show()
        self.portLabel.show()
        self.ipEdit.show()
        self.portEdit.show()
        self.comLabel.hide()
        self.comSpeedLabel.hide()
        self.comSelect.hide()
        self.comSpeedEdit.hide()
        Logger.getInstance().debug("WiFi connection chosen")
        self.connMode = "WiFi"
     
    @QtCore.pyqtSlot() 
    def setUSB(self):
        self.ipLabel.hide()
        self.portLabel.hide()
        self.ipEdit.hide()
        self.portEdit.hide()
        self.comLabel.show()
        self.comSpeedLabel.show()
        current = self.comSelect.currentText()
        self.comSelect.clear()
        self.comSelect.addItems(list(COMMngr().getAllPorts()))
        findpos = self.comSelect.findText(current)
        self.comSelect.setCurrentIndex(findpos if findpos > 0 else 0)
        self.comSelect.show()
        self.comSpeedEdit.show()
        Logger.getInstance().debug("COM connection chosen")
        self.connMode = "COM"
        
    @QtCore.pyqtSlot() 
    def connectToTarget(self):
        if self.connMode == "WiFi":
            ip = self.ipEdit.text()
            port = self.portEdit.text()
            Logger.getInstance().info("Request connection to %s:%s" % (ip, port))
            self.connectRequested.emit(("WiFi", ip, port))
        else: # COM
            com = self.comSelect.currentText()
            speed = self.comSpeedEdit.text()
            Logger.getInstance().info("Request connection to %s @%s" % (com, speed))
            self.connectRequested.emit(("COM", com, speed))
            
    @QtCore.pyqtSlot()
    def disconnectTarget(self):
        Logger.getInstance().info("Requested disconnect from target")
        self.connectRequested.emit(("HANG", 0, 0))
            
    @QtCore.pyqtSlot(QtCore.QPoint)
    def showContextMenuStats(self, point):
        globalPos = self.statsFrame.mapToGlobal(point)
        menu = QtGui.QMenu()
        refreshMenu = QtGui.QMenu("Refreshing")
        refreshNone = refreshMenu.addAction("Disable")
        refresh1s = refreshMenu.addAction("1s")
        refresh10s = refreshMenu.addAction("10s")
        menu.addMenu(refreshMenu)
        
        selectedItem = menu.exec_(globalPos)
        
        if selectedItem:
            if selectedItem == refreshNone:
                self.statsRefreshChanged.emit(-1)
            elif selectedItem == refresh1s:
                self.statsRefreshChanged.emit(1000)
            elif selectedItem == refresh10s:
                self.statsRefreshChanged.emit(10000)
               
    @QtCore.pyqtSlot(QtCore.QPoint)
    def showContextMenuTelemetry(self, point):
        globalPos = self.telemetryFrame.mapToGlobal(point)
        menu = QtGui.QMenu()
        refreshMenu = QtGui.QMenu("Refreshing")
        refreshNone = refreshMenu.addAction("Disable")
        refreshOnChange = refreshMenu.addAction("On change")
        refresh100ms = refreshMenu.addAction("100ms")
        refresh500ms = refreshMenu.addAction("500ms")
        refresh1s = refreshMenu.addAction("1s")
        refresh10s = refreshMenu.addAction("10s")
        menu.addMenu(refreshMenu)
        
        selectedItem = menu.exec_(globalPos)
        
        if selectedItem:
            if selectedItem == refreshNone:
                self.telemetryRefreshChanged.emit(-1)
            elif selectedItem == refreshOnChange:
                self.telemetryRefreshChanged.emit(-2)  
            elif selectedItem == refresh100ms:
                self.telemetryRefreshChanged.emit(100)  
            elif selectedItem == refresh500ms:
                self.telemetryRefreshChanged.emit(500)  
            elif selectedItem == refresh1s:
                self.telemetryRefreshChanged.emit(1000)
            elif selectedItem == refresh10s:
                self.telemetryRefreshChanged.emit(10000)   
        
    def connectDone(self, status):
        if status:
            self.connectionLabel.show()
        else:
            self.telemetryRefreshChanged.emit(-1)
            self.connectionLabel.hide()
            self.resetDefaultValues()
    
    def applicationResetRequested(self):
        return self.resetAllButton.clicked
            
    def resetDefault(self):
        self.disconnectTarget()
        
    def resetDefaultValues(self):
        self.posXEdit.setText("?")
        self.posYEdit.setText("?")
        self.posOrientEdit.setText("?")
        self.leftSpeedBar.reset()
        self.rightSpeedBar.reset()
        self.cpuUsageBar.reset()
        self.memoryBar.reset()
        self.batteryBar.reset()
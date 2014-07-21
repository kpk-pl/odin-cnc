#!/usr/bin/env python

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt

from LeftPanel import LeftPanel
from Logger import Logger
from IncommingMessageHandler import IncommingMessageHandler
from TrajectoryTab import TrajectoryTab
from TelemetryTab import TelemetryTab
from CameraTab import CameraTab
from MotorsTab import MotorsTab
from QHistoryLineEdit import QHistoryLineEdit

# Shortcuts
# Ctrl+Shift+C - Connect button click
# Alt+F - menu File
# Alt+H - menu help
# Alt+T - Telemetry tab
# Alt+M - Motots tab
# Alt+R - Trajectory tba
# Alt+S - SD card tab
# Alt+C - Camera tab

class MainWindow(QtGui.QMainWindow):
    def __init__(self, incomming_queue, outgoing_queue):
        super(MainWindow, self).__init__()

        self.incomming_queue = incomming_queue
        self.outgoing_queue = outgoing_queue
        
        self.setUpGUI()     
        self.createActions()
        self.createMenus()
        self.createConnections()
        self.statusBar()
        self.configureTimers()
        
        self.setWindowTitle("Odin Command and Control")
        self.setMinimumSize(800,600)
        self.resize(1024,768)
        
        Logger.getInstance().update.connect(self.logConsole.appendPlainText)
        Logger.getInstance().info("Main window is up")
        
        self.connectDone(False)
        
        self.dispatcher = IncommingMessageHandler(self.incomming_queue)
        self.dispatcherThread = QtCore.QThread()
        self.dispatcher.moveToThread(self.dispatcherThread)
        self.dispatcherThread.started.connect(self.dispatcher.loop)
        self.dispatcherThread.start()
        
        self.dispatcher.incomming.connect(self.commConsole.appendPlainText)
        self.dispatcher.updBatteryVoltage.connect(self.leftPanel.batteryBar.setValue)
        self.dispatcher.updCpuUsage.connect(self.leftPanel.cpuUsageBar.setValue)
        self.dispatcher.updMemUsage.connect(self.leftPanel.memoryBar.setValue)
        self.dispatcher.updTelemetry.connect(self.leftPanel.updateTelemetry)
        self.dispatcher.updTelemetry.connect(self.telemetryPanel.updateTelemetry)
        self.dispatcher.updCurrentSpeed.connect(self.leftPanel.updateCurrentSpeed)
        self.dispatcher.reset.connect(self.resetDefault)
        
    def about(self):
        QtGui.QMessageBox.about(self, "About Menu",
                "The <b>Menu</b> example shows how to create menu-bar menus "
                "and context menus.")

    def closeEvent(self, event):
        self.dispatcher.stop()
        self.dispatcherThread.quit()
        self.dispatcherThread.wait()
        QtGui.qApp.quit()
        event.ignore()
        #exit()
        
    @QtCore.pyqtSlot(int)
    def handleSpeedRefreshChange(self, t):
        if t >= 0:
            self.speedRefreshTimer.start(t)
        else:
            self.speedRefreshTimer.stop()
        if t == -2:
            self.sendComm("log speed")
        else:
            self.sendComm("log speed off")
            
    @QtCore.pyqtSlot(int)
    def handleTelemetryRefreshChange(self, t):
        if t >= 0:
            self.telemetryRefreshTimer.start(t)
        else:
            self.telemetryRefreshTimer.stop()
        if t == -2:
            self.sendComm("log telemetry")
        else:
            self.sendComm("log telemetry off")
            
    @QtCore.pyqtSlot()
    def commSendBtnClicked(self):
        self.sendComm(self.commInput.text())
        self.commInput.clear()
        
    @QtCore.pyqtSlot(bool)    
    def connectDone(self, status):
        self.connected = status
        self.commSendBtn.setEnabled(status)
        self.leftPanel.connectDone(status)
        if not status:
            self.resetDefault()
        
    @QtCore.pyqtSlot()
    def resetDefault(self):
        self.leftPanel.resetDefault()
        self.telemetryPanel.resetDefault()
        self.cameraPanel.resetDefault()
        self.motorsPanel.resetDefault()
        
    def sendComm(self, msg_list):
        if self.connected:
            if not isinstance(msg_list, list):
                msg_list = [msg_list]
            for msg in msg_list:
                if not isinstance(msg, str):
                    msg = str(msg)
                self.outgoing_queue.put(msg + "\n", True)
                self.commConsole.appendPlainText(msg)            
        
    def connectRequested(self):
        return self.leftPanel.connectRequested
        
    def createActions(self):
        self.exitAct = QtGui.QAction("E&xit", self, shortcut="Ctrl+Q",
                statusTip="Exit the application", triggered=self.close)
        self.aboutAct = QtGui.QAction("&About", self,
                statusTip="Show the application's About box",
                triggered=self.about)
        self.aboutQtAct = QtGui.QAction("About &Qt", self,
                statusTip="Show the Qt library's About box",
                triggered=QtGui.qApp.aboutQt)
                
    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)
        
    def createConnections(self):
        self.commSendBtn.clicked.connect(self.commInput.saveLine)
        self.commSendBtn.clicked.connect(self.commSendBtnClicked)
        self.commInput.returnPressed.connect(self.commSendBtnClicked)
        self.leftPanel.statsRefreshChanged.connect(lambda t: self.statsRefreshTimer.start(t) if t > 0 else self.statsRefreshTimer.stop())
        self.leftPanel.telemetryRefreshChanged.connect(self.handleTelemetryRefreshChange)
        self.leftPanel.telemetryRefreshChanged.connect(self.handleSpeedRefreshChange)
        self.telemetryPanel.telemetryRefreshChanged.connect(self.handleTelemetryRefreshChange)
        
    def configureTimers(self):
        @QtCore.pyqtSlot() 
        def statsRequests():
            self.sendComm(["system cpu", "system memory", "system battery"])
        self.statsRefreshTimer = QtCore.QTimer()
        self.statsRefreshTimer.timeout.connect(statsRequests)
        @QtCore.pyqtSlot()
        def telemetryRequest():
            self.sendComm("telemetry raw")
        self.telemetryRefreshTimer = QtCore.QTimer()
        self.telemetryRefreshTimer.timeout.connect(telemetryRequest)
        @QtCore.pyqtSlot()
        def speedRequest():
            self.sendComm("motor speed")
        self.speedRefreshTimer = QtCore.QTimer()
        self.speedRefreshTimer.timeout.connect(speedRequest)
        
    def setUpGUI(self):
        widget = QtGui.QWidget()
        self.setCentralWidget(widget)
        
        ### LEFT PANEL
        self.leftPanel = LeftPanel()
        
        ### COMMUNICATION CONSOLE
        self.commConsole = QtGui.QPlainTextEdit()
        self.commConsole.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.commConsole.setReadOnly(True)
        self.commConsole.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.commConsole.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.commConsole.setMaximumBlockCount(500)
        
        self.commInput = QHistoryLineEdit()
        self.commSendBtn = QtGui.QPushButton("->")
        self.commSendBtn.setStatusTip("Send command to robot")
        self.commSendBtn.setMaximumWidth(30)
        
        commWidget = QtGui.QWidget()
        commLayout = QtGui.QGridLayout()
        commLayout.setMargin(0)
        commLayout.addWidget(self.commConsole, 0, 0, 1, 2)
        commLayout.addWidget(self.commInput, 1, 0, 1, 1)
        commLayout.addWidget(self.commSendBtn, 1, 1, 1, 1)
        commWidget.setLayout(commLayout)
        
        ### LOG CONSOLE
        self.logConsole = QtGui.QPlainTextEdit()
        self.logConsole.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.logConsole.setReadOnly(True)
        self.logConsole.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.logConsole.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.logConsole.setMaximumBlockCount(500)

        ### BOTH CONSOLES
        consoles = QtGui.QWidget()
        consoles.setMinimumHeight(100)
        consoleLayout = QtGui.QHBoxLayout()
        consoleLayout.setMargin(0)
        consoleLayout.addWidget(commWidget)
        consoleLayout.addWidget(self.logConsole)
        consoles.setLayout(consoleLayout)
        
        ### CENTER PANEL
        self.telemetryPanel = TelemetryTab()
        self.motorsPanel = MotorsTab()
        self.trajectoryPanel = TrajectoryTab()
        self.sdPanel = QtGui.QWidget()
        self.cameraPanel = CameraTab()
        
        self.centerPanel = QtGui.QTabWidget()
        self.centerPanel.setMinimumHeight(400)
        self.centerPanel.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.centerPanel.addTab(self.telemetryPanel, "&Telemetry")
        self.centerPanel.addTab(self.motorsPanel, "&Motors")
        self.centerPanel.addTab(self.trajectoryPanel, "T&rajectory")
        self.centerPanel.addTab(self.sdPanel, "&SD card")
        self.centerPanel.addTab(self.cameraPanel, "&Camera")        
        
        ### SPLITTER
        splitter = QtGui.QSplitter()
        splitter.setChildrenCollapsible(False)
        splitter.setOrientation(Qt.Vertical)
        splitter.addWidget(self.centerPanel)
        splitter.addWidget(consoles)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        
        layout = QtGui.QHBoxLayout()
        layout.setMargin(5)
        layout.addWidget(self.leftPanel)
        layout.addWidget(splitter)
        widget.setLayout(layout)
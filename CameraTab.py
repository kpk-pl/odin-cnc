#!/usr/bin/env python

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
import pyqtgraph as pg
import math

from Logger import Logger
from CameraThread import CameraThread
        
class CameraTab(QtGui.QWidget):
    telemetrySend = QtCore.pyqtSignal(tuple)

    def __init__(self, parent=None):
        super(CameraTab, self).__init__(parent)
        
        self.cameraThreadObject = CameraThread()
        self.cameraThread = QtCore.QThread()
        self.cameraThreadObject.moveToThread(self.cameraThread)
        
        self.setupGUI()
        
        self.settingsStartStopBtn.clicked.connect(self.connectButtonClicked)
        self.cameraThreadObject.frameCaptured.connect(self.updateFrame)
        self.cameraThread.started.connect(self.cameraThreadObject.setup)
        self.cameraThreadObject.message.connect(self.settingsStatusLabel.setText)
        self.cameraThreadObject.connected.connect(self.connected)
        self.cameraThreadObject.disconnected.connect(self.disconected)
        self.cameraThreadObject.fpsUpdated.connect(lambda x: self.settingsFPSCurrent.setText("%.1f" % (x)))
        self.cameraThreadObject.telemetry.connect(self.telemetryFromCamera)
        
        self.cameraThread.start()
        
    def __del__(self):
        self.cameraThread.quit()
        self.cameraThread.wait()
       
    @QtCore.pyqtSlot()
    def connectButtonClicked(self):
        if self.settingsStartStopBtn.text() == "Start":
            fps = float(self.settingsFPSSelection.value())
            QtCore.QMetaObject.invokeMethod(self.cameraThreadObject, 'connect', Qt.QueuedConnection, 
                QtCore.Q_ARG(float, fps))
            Logger.getInstance().info("Trying to start camera at %.2f fps" % (fps))
        else:
            QtCore.QMetaObject.invokeMethod(self.cameraThreadObject, 'disconnect', Qt.QueuedConnection)
            Logger.getInstance().info("Trying to stop camera")
           
    @QtCore.pyqtSlot(tuple)
    def telemetryFromCamera(self, telemetry):
        if self.settingsSendUpdates.isChecked():
            self.telemetrySend.emit(telemetry)
        self.telemetryX.setText("%.2f" % (telemetry[0]))
        self.telemetryY.setText("%.2f" % (telemetry[1]))
        self.telemetryODeg.setText("%.2f" % (telemetry[2]))
        self.telemetryORad.setText("%.2f" % (telemetry[2]))
      
    @QtCore.pyqtSlot()
    def connected(self):
        self.settingsStartStopBtn.setText("Stop")
        Logger.getInstance().info("Camera started")
        
    @QtCore.pyqtSlot()
    def disconected(self):
        self.settingsStartStopBtn.setText("Start")
        Logger.getInstance().info("Camera stopped")
           
    @QtCore.pyqtSlot(QtGui.QImage)
    def updateFrame(self, image):
        if self.settingsShowCapture.isChecked():
            pixmap = QtGui.QPixmap.fromImage(image)
            scaledPixMap = pixmap.scaled(self.frameLabel.size(), Qt.KeepAspectRatio)
            self.frameLabel.setPixmap(scaledPixMap)
       
    def resetDefault(self):
        self.settingsStartStopBtn.setText("Start")
        self.settingsFPSCurrent.setText("?")
        self.settingsShowCapture.setChecked(False)
        self.settingsSendUpdates.setChecked(False)
        self.settingsStatusLabel.setText("OK")
        
        self.telemetryX.setText("?")
        self.telemetryY.setText("?")
        self.telemetryODeg.setText("?")
        self.telemetryORad.setText("?")

    def setupGUI(self):
        # main layout
        layout = QtGui.QHBoxLayout()
        layout.setMargin(10)
        self.setLayout(layout)
        leftSideWdgt = QtGui.QWidget()
        leftSideWdgt.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
        leftSideWdgt.setFixedWidth(250);
        self.frameLabel = QtGui.QLabel();
        layout.addWidget(leftSideWdgt)
        layout.addWidget(self.frameLabel)
        
        # left layout
        leftLayout = QtGui.QVBoxLayout()
        layout.setMargin(0)
        leftSideWdgt.setLayout(leftLayout)
        
        # settings
        self.settingsStartStopBtn = QtGui.QPushButton("Start")
        self.settingsFPSSelection = pg.SpinBox(bounds=[1,188], int=True, dec=False, minStep=1, step=10, suffix="fps")
        self.settingsFPSSelection.setValue(30)
        self.settingsFPSCurrent = QtGui.QLineEdit()
        self.settingsFPSCurrent.setReadOnly(True)
        self.settingsShowCapture = QtGui.QCheckBox("Show live capture")
        self.settingsSendUpdates = QtGui.QCheckBox("Send updates to robot")
        self.settingsStatusLabel = QtGui.QLabel("OK")
        
        settingsBox = QtGui.QGroupBox("Settings")
        settingsLayout = QtGui.QGridLayout()
        settingsLayout.setSpacing(3)
        settingsLayout.setMargin(5)
        settingsLayout.addWidget(self.settingsStartStopBtn, 0, 0, 1, 1)
        settingsLayout.addWidget(self.settingsFPSSelection, 0, 1, 1, 1)
        settingsLayout.addWidget(QtGui.QLabel("Current FPS"), 1, 0, 1, 1)
        settingsLayout.addWidget(self.settingsFPSCurrent, 1, 1, 1, 1)
        settingsLayout.addWidget(self.settingsShowCapture, 2, 0, 1, 2)
        settingsLayout.addWidget(self.settingsSendUpdates, 3, 0, 1, 2)
        settingsLayout.addWidget(self.settingsStatusLabel, 4, 0, 1, 2)
        settingsBox.setLayout(settingsLayout)
        leftLayout.addWidget(settingsBox)
        
        # telemetry
        self.telemetryX = QtGui.QLineEdit()
        self.telemetryY = QtGui.QLineEdit()
        self.telemetryORad = QtGui.QLineEdit()
        self.telemetryODeg = QtGui.QLineEdit()
        self.telemetryX.setReadOnly(True)
        self.telemetryY.setReadOnly(True)
        self.telemetryORad.setReadOnly(True)
        self.telemetryODeg.setReadOnly(True)
        
        telemetryBox = QtGui.QGroupBox("Telemetry")
        telemetryLayout = QtGui.QGridLayout()
        telemetryLayout.setSpacing(3)
        telemetryLayout.setMargin(5)
        telemetryLayout.addWidget(QtGui.QLabel("X"), 0, 0, 1, 1)
        telemetryLayout.addWidget(self.telemetryX, 0, 1, 1, 3)
        telemetryLayout.addWidget(QtGui.QLabel("[mm]"), 0, 4, 1, 1)
        telemetryLayout.addWidget(QtGui.QLabel("Y"), 1, 0, 1, 1)
        telemetryLayout.addWidget(self.telemetryY, 1, 1, 1, 3)
        telemetryLayout.addWidget(QtGui.QLabel("[mm]"), 1, 4, 1, 1)
        telemetryLayout.addWidget(QtGui.QLabel("O"), 2, 0, 1, 1)
        telemetryLayout.addWidget(self.telemetryODeg, 2, 1, 1, 1)
        telemetryLayout.addWidget(QtGui.QLabel("[deg]"), 2, 2, 1, 1)
        telemetryLayout.addWidget(self.telemetryORad, 2, 3, 1, 1)
        telemetryLayout.addWidget(QtGui.QLabel("[rad]"), 2, 4, 1, 1)
        telemetryBox.setLayout(telemetryLayout)
        leftLayout.addWidget(telemetryBox)
        
        # end
        leftLayout.addStretch()
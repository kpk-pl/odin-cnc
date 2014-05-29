#!/usr/bin/env python

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
import numpy as np
import pyqtgraph as pg
from datetime import datetime

from Logger import Logger
from Camera import CLEyeCamera as CL
import time

class CameraThread(QtCore.QObject):
    frameCaptured = QtCore.pyqtSignal(QtGui.QImage)
    connected = QtCore.pyqtSignal()
    disconnected = QtCore.pyqtSignal()
    
    def __init__(self, parent=None):
        super(CameraThread, self).__init__(parent)
        
        self.colorTable = []
        for i in range(256): 
            self.colorTable.append(QtGui.qRgb(i,i,i))
        
    def __del__(self):
        self.disconnect()
    
    def setup(self):
        self.runTimer = QtCore.QTimer()
        self.runTimer.timeout.connect(self.mainLoop)
    
    @QtCore.pyqtSlot(float)
    def connect(self, frameRate):
        self.cam = CL.CLEyeCamera(0, mode=CL.CLEYE_MONO_RAW, resolution=CL.CLEYE_VGA, frameRate=frameRate)
        self.cam.setParam(CL.CLEYE_AUTO_GAIN, False)
        self.cam.setParam(CL.CLEYE_AUTO_EXPOSURE, False)
        self.cam.setParam(CL.CLEYE_AUTO_WHITEBALANCE, True)
        self.cam.setParam(CL.CLEYE_GAIN, 30)
        self.cam.setParam(CL.CLEYE_EXPOSURE, 400)
        
        self.frame = None
        
        self.runTimer.start(0)
        self.connected.emit()
        Logger.getInstance().put(Logger.INFO, "Camera thread connected camera")
        
    @QtCore.pyqtSlot()
    def disconnect(self):  
        self.runTimer.stop()
        del self.cam
        self.disconnected.emit()
        Logger.getInstance().put(Logger.INFO, "Camera thread disconnected camera")
        
    def mainLoop(self):
        if self.frame is None:
            self.frame = self.cam.getFrame()
            self.height, self.width, self.layers = self.frame.shape
        else:
            self.cam.getFrameX(self.frame)
        
        if self.layers == 1:
            qimg = QtGui.QImage(self.frame.tostring(), self.width, self.height, QtGui.QImage.Format_Indexed8)
            qimg.setColorTable(self.colorTable)
        else:
            qimg = QtGui.QImage(self.frame.tostring(), self.width, self.height, QtGui.QImage.Format_RGB32).rgbSwapped()
        self.frameCaptured.emit(qimg)

        
        
class CameraTab(QtGui.QWidget):
    def __init__(self, parent=None):
        super(CameraTab, self).__init__(parent)
        
        self.cameraThreadObject = CameraThread()
        self.cameraThread = QtCore.QThread()
        self.cameraThreadObject.moveToThread(self.cameraThread)
        
        self.fpsTimer = QtCore.QTimer()
        self.fpsTimer.timeout.connect(self.fpsTimerHandle)
        
        self.setupGUI()
        
        self.settingsStartStopBtn.clicked.connect(self.connectButtonClicked)
        self.cameraThreadObject.frameCaptured.connect(self.updateFrame)
        self.cameraThread.started.connect(self.cameraThreadObject.setup)
        
        self.cameraThread.start()
        
    def __del__(self):
        self.cameraThread.quit()
        self.cameraThread.wait()
       
    @QtCore.pyqtSlot()
    def fpsTimerHandle(self):
        ctime = time.clock()
        fps = float(self.fpsFrameCounter) / (ctime-self.fpsSTime);
        self.fpsFrameCounter = 0
        self.fpsSTime = ctime
        self.settingsFPSCurrent.setText("%.1f" % (fps))
       
    @QtCore.pyqtSlot()
    def connectButtonClicked(self):
        if self.settingsStartStopBtn.text() == "Start":
            fps = float(self.settingsFPSSelection.value())
            QtCore.QMetaObject.invokeMethod(self.cameraThreadObject, 'connect', Qt.QueuedConnection, 
                QtCore.Q_ARG(float, fps))
            self.settingsStartStopBtn.setText("Stop")
            Logger.getInstance().put(Logger.INFO, "Started camera at %.2f fps" % (fps))
            self.fpsSTime = time.clock()
            self.fpsFrameCounter = 0
            self.fpsTimer.start(1000)
        else:
            QtCore.QMetaObject.invokeMethod(self.cameraThreadObject, 'disconnect', Qt.QueuedConnection)
            self.settingsStartStopBtn.setText("Start")
            Logger.getInstance().put(Logger.INFO, "Stopped camera")
            self.fpsTimer.stop()
       
    @QtCore.pyqtSlot(QtGui.QImage)
    def updateFrame(self, image):
        self.fpsFrameCounter += 1
        pixmap = QtGui.QPixmap.fromImage(image)
        scaledPixMap = pixmap.scaled(self.frameLabel.size(), Qt.KeepAspectRatio)
        self.frameLabel.setPixmap(scaledPixMap)
       
    def resetDefault(self):
        self.settingsStartStopBtn.setText("Start")
        self.settingsFPSCurrent.setText("?")
        self.settingsShowCapture.setChecked(False)
        self.settingsStatusLabel.setText("OK")

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
        self.settingsFPSSelection = pg.SpinBox(bounds=[30,188], int=True, dec=False, minStep=1, step=10, suffix="fps")
        self.settingsFPSCurrent = QtGui.QLineEdit()
        self.settingsFPSCurrent.setReadOnly(True)
        self.settingsShowCapture = QtGui.QCheckBox("Show live capture")
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
        settingsLayout.addWidget(self.settingsStatusLabel, 3, 0, 1, 2)
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
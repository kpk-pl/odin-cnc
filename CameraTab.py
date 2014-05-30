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
    message = QtCore.pyqtSignal(str)
    fpsUpdated = QtCore.pyqtSignal(float)
    telemetry = QtCore.pyqtSignal(tuple)
    
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
        self.fpsTimer = QtCore.QTimer()
        self.fpsTimer.timeout.connect(self.calcFPS)
        self.fpsSTime = time.clock()
        self.fpsCounter = 0
        
    @QtCore.pyqtSlot()
    def calcFPS(self):
        etime = time.clock()
        fps = float(self.fpsCounter)/(etime-self.fpsSTime)
        self.fpsSTime = etime
        self.fpsCounter = 0
        self.fpsUpdated.emit(fps)
    
    @QtCore.pyqtSlot(float)
    def connect(self, frameRate):
        try:
            self.cam = CL.CLEyeCamera(0, mode=CL.CLEYE_MONO_RAW, resolution=CL.CLEYE_VGA, frameRate=frameRate)
        except CL.CLEyeException as e:
            self.message.emit("Cannot initialize camera")
            Logger.getInstance().put(Logger.ERROR, "Cannot initialize camera: " + str(e))
            return
        
        self.cam.setParam(CL.CLEYE_AUTO_GAIN, False)
        self.cam.setParam(CL.CLEYE_AUTO_EXPOSURE, False)
        self.cam.setParam(CL.CLEYE_AUTO_WHITEBALANCE, True)
        self.cam.setParam(CL.CLEYE_GAIN, 30)
        self.cam.setParam(CL.CLEYE_EXPOSURE, 400)
        
        self.frame = None
        self.updateDiv = int(ceil(float(frameRate)/10.0))
        self.updateCounter = 0
        
        self.runTimer.start(0)
        self.fpsCounter = 0
        self.fpsSTime = time.clock()
        self.fpsTimer.start(1000)
        self.connected.emit()
        Logger.getInstance().put(Logger.INFO, "Camera thread connected camera")
        
    @QtCore.pyqtSlot()
    def disconnect(self):  
        self.runTimer.stop()
        self.fpsTimer.stop()
        del self.cam
        self.disconnected.emit()
        Logger.getInstance().put(Logger.INFO, "Camera thread disconnected camera")
        
    def mainLoop(self):
        if self.frame is None:
            self.frame = self.cam.getFrame()
            self.height, self.width, self.layers = self.frame.shape
        else:
            self.cam.getFrameX(self.frame)
        
        self.fpsCounter += 1
        self.updCounter += 1
        
        if self.updCounter >= self.updateDiv:
            if self.layers == 1:
                qimg = QtGui.QImage(self.frame.tostring(), self.width, self.height, QtGui.QImage.Format_Indexed8)
                qimg.setColorTable(self.colorTable)
            else:
                qimg = QtGui.QImage(self.frame.tostring(), self.width, self.height, QtGui.QImage.Format_RGB32).rgbSwapped()
            self.frameCaptured.emit(qimg)
            
            self.updCounter = 0

        
        
class CameraTab(QtGui.QWidget):
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
            Logger.getInstance().put(Logger.INFO, "Trying to start camera at %.2f fps" % (fps))
        else:
            QtCore.QMetaObject.invokeMethod(self.cameraThreadObject, 'disconnect', Qt.QueuedConnection)
            Logger.getInstance().put(Logger.INFO, "Trying to stop camera")
       
    @QtCore.pyqtSlot()
    def connected(self):
        self.settingsStartStopBtn.setText("Stop")
        Logger.getInstance().put(Logger.INFO, "Camera started")
        
    @QtCore.pyqtSlot()
    def disconected(self):
        self.settingsStartStopBtn.setText("Start")
        Logger.getInstance().put(Logger.INFO, "Camera stopped")
           
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
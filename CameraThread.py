#!/usr/bin/env python

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt

import time, math

from Logger import Logger
from Camera import CLEyeCamera as CL

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
            Logger.getInstance().error("Cannot initialize camera: " + str(e))
            return
        
        self.cam.setParam(CL.CLEYE_AUTO_GAIN, False)
        self.cam.setParam(CL.CLEYE_AUTO_EXPOSURE, False)
        self.cam.setParam(CL.CLEYE_AUTO_WHITEBALANCE, True)
        self.cam.setParam(CL.CLEYE_GAIN, 30)
        self.cam.setParam(CL.CLEYE_EXPOSURE, 400)
        
        self.frame = None
        self.updateDiv = int(math.ceil(float(frameRate)/10.0))
        self.updateCounter = 0
        
        self.runTimer.start(0)
        self.fpsCounter = 0
        self.fpsSTime = time.clock()
        self.fpsTimer.start(1000)
        self.connected.emit()
        self.message.emit('Connected')
        Logger.getInstance().info("Camera thread connected camera")
        
    @QtCore.pyqtSlot()
    def disconnect(self):  
        self.runTimer.stop()
        self.fpsTimer.stop()
        del self.cam
        self.disconnected.emit()
        self.message.emit('Disconnected')
        Logger.getInstance().debug("Camera thread disconnected camera")
        
    def mainLoop(self):
        if self.frame is None:
            self.frame = self.cam.getFrame()
            self.height, self.width, self.layers = self.frame.shape
        else:
            self.cam.getFrameX(self.frame)
        
        self.fpsCounter += 1
        self.updateCounter += 1
        
        self.telemetry.emit((2.0, 2.0, 2.0))
        
        if self.updateCounter >= self.updateDiv:
            if self.layers == 1:
                qimg = QtGui.QImage(self.frame.tostring(), self.width, self.height, QtGui.QImage.Format_Indexed8)
                qimg.setColorTable(self.colorTable)
            else:
                qimg = QtGui.QImage(self.frame.tostring(), self.width, self.height, QtGui.QImage.Format_RGB32).rgbSwapped()
            self.frameCaptured.emit(qimg)
            
            self.updateCounter = 0
#!/usr/bin/env python

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
import numpy as np

import time, math

from Logger import Logger
from Camera import CLEyeCamera as CL
from Camera import DotFinder, PatternMatcher, PositionTracker, TelemetryCalculator

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
          
        # TODO: These should be kept in settings file and loaded at start
        self.dotFinder = DotFinder.DotFinder(16, [np.array([50]), np.array([255])])

        #              4
        #        3           5
        #    2         15        6
        #   
        #  1     14    0          7
        # 
        #    12        13       8
        #        11          9
        #              10
        self.pattern = [[170,100],
                   [115,100],
                   [122.37,72.5],
                   [142.5,52.33],
                   [170,45],
                   [197.5,52.33],
                   [217.63,72.5],
                   [225,100],
                   [217.63,127.5],
                   [197.5,147.67],
                   [170,155],
                   [142.5,147.67],
                   [122.37,127.5],
                   [170, 127.5],
                   [142.5, 100],
                   [170, 72.5]]
        self.pattern = np.float32(self.pattern)
        self.pattern = np.float32(np.inner(self.pattern, [[1, 0],[0, -1]])) # change sign on Y
        self.pattern = np.float32(self.pattern  - self.pattern[0]) # center everything 
        self.pattern = np.float32(np.inner(self.pattern, [[0, 1],[-1, 0]])) # rotate left to match robots coordinates
        
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
    
    # TODO pass parameters to all algorithms
    @QtCore.pyqtSlot(float, dict)
    def connect(self, frameRate, options):
        try:
            self.cam = CL.CLEyeCamera(0, mode=CL.CLEYE_MONO_RAW, resolution=CL.CLEYE_VGA, frameRate=frameRate)
        except CL.CLEyeException as e:
            self.message.emit("Cannot initialize camera")
            Logger.getInstance().error("Cannot initialize camera: " + str(e))
            return
        
        # TODO: camera parameters must be run time changeable
        self.cam.setParam(CL.CLEYE_AUTO_GAIN, False)
        self.cam.setParam(CL.CLEYE_AUTO_EXPOSURE, False)
        self.cam.setParam(CL.CLEYE_AUTO_WHITEBALANCE, True)
        self.cam.setParam(CL.CLEYE_GAIN, options['gain'])
        self.cam.setParam(CL.CLEYE_EXPOSURE, options['exposure'])
        
        self.frame = None
        self.updateDiv = int(math.ceil(float(frameRate)/10.0))
        self.updateCounter = 0
        self.returnImageType = options['returnImage']
        
        # TODO: this must be parametrized in GUI!
        scaling_file = 'Camera/camcalib-PSEye-VGA-wideLens.npz'
        self.matcher = PatternMatcher.PatternMatcher(self.pattern, scaling_file)
        self.tracker = PositionTracker.PositionTracker(self.pattern, scaling_file, coord_scale=1.0)
        self.calculator = TelemetryCalculator.TelemetryCalculator(n_init=10)
        
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
        
    @QtCore.pyqtSlot(dict)
    def setParam(self, options):
        for opt in options:
            if opt == 'gain':
                self.cam.setParam(CL.CLEYE_GAIN, options[opt])
            elif opt == 'exposure':
                self.cam.setParam(CL.CLEYE_EXPOSURE, options[opt])
            elif opt == 'returnImage':
                self.returnImageType = options[opt]
        
    def mainLoop(self):
        if self.frame is None:
            self.frame = self.cam.getFrame()
            self.height, self.width, self.layers = self.frame.shape
        else:
            self.cam.getFrameX(self.frame)
        
        self.fpsCounter += 1
        self.updateCounter += 1
        
        points, _, markedimg = self.dotFinder.find(self.frame)
        try:
            match_map, _ = self.matcher.match(points)
            self.matcher.mark_map(markedimg, points, match_map)
            mapped = np.float32([points[i] for i in matchmap])
            rvec, tvec = self.tracker.getCoords(mapped, markedimg)
            coords = self.calculator(rvec, tvec)
            if coords != None:
                self.telemetry.emit((coords[1][0], coords[1][1], coords[0][2]*180.0/math.pi))
        except PatternMatcher.MatchError as e:
            print e
        
        #self.telemetry.emit((2.0, 2.0, 2.0))
        
        if self.updateCounter >= self.updateDiv:
            toshow = markedimg if self.returnImageType == 'marked' else self.frame
            if self.layers == 1:
                qimg = QtGui.QImage(toshow.tostring(), self.width, self.height, QtGui.QImage.Format_Indexed8)
                qimg.setColorTable(self.colorTable)
            else:
                qimg = QtGui.QImage(toshow.tostring(), self.width, self.height, QtGui.QImage.Format_RGB32).rgbSwapped()
            self.frameCaptured.emit(qimg)
            
            self.updateCounter = 0
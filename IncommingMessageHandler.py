#!/usr/bin/env python

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt

from MsgDispatcher import MsgDispatcher
import Queue
from datetime import datetime

class IncommingMessageHandler(QtCore.QObject):
    incomming = QtCore.pyqtSignal(str)
    updBatteryVoltage = QtCore.pyqtSignal(float)
    updCpuUsage = QtCore.pyqtSignal(float)
    updMemUsage = QtCore.pyqtSignal(int)
    updTelemetry = QtCore.pyqtSignal(tuple)
    updCurrentSpeed = QtCore.pyqtSignal(tuple)
    rc5Input = QtCore.pyqtSignal(int)
    reset = QtCore.pyqtSignal()
    
    def __init__(self, input_queue):
        super(IncommingMessageHandler, self).__init__()
        self.input_queue = input_queue
        self.dispatcher = MsgDispatcher("odin>")
        self.setupDispatcher()
       
    QtCore.pyqtSlot()    
    def loop(self):
        self._alive = True
        while self._alive:
            try:
                message = self.input_queue.get(True, 0.01)
            except Queue.Empty:
                pass
            else:
                self.dispatcher.dispatch(message)
        
    QtCore.pyqtSlot()
    def stop(self):
        self._alive = False
        
    def setupDispatcher(self):
        def p(payload):
            print "Default: " + payload.message
            
        self.dispatcher.register_all(
            lambda payload: self.incomming.emit(payload.message))
        self.dispatcher.register_default(p)
        
        self.dispatcher.register(r"^(odin>)?Battery voltage: (\d+\.\d+)V$", 
            lambda payload: self.updBatteryVoltage.emit(float(payload.match.group(2))))
        self.dispatcher.register(r"^(odin>)?CPU usage: (.*)$",
            lambda payload: self.updCpuUsage.emit(float(payload.match.group(2))))
        self.dispatcher.register(r"^(odin>)?Available memory: (\d+)kB$",
            lambda payload: self.updMemUsage.emit(int(payload.match.group(2))))
        self.dispatcher.register(r"^(odin>)?\[Tel\] X: (-?\d+.\d+) Y: (-?\d+.\d+) O: (-?\d+.\d+)$",
            lambda payload: self.updTelemetry.emit((
            float(payload.match.group(2)), 
            float(payload.match.group(3)), 
            float(payload.match.group(4)),
            datetime.now())))
        self.dispatcher.register(r"^(odin>)?\[Speed\] L: (-?\d+.\d+) R: (-?\d+.\d+)$",
            lambda payload: self.updCurrentSpeed.emit((
            float(payload.match.group(2)), 
            float(payload.match.group(3)))))
        self.dispatcher.register(r"^(odin>)?Reset!$", lambda payload: self.reset.emit())
        self.dispatcher.register(r"^(odin>)?\[RC5\] Received (\d+)$",
            lambda payload: self.rc5Input.emit(payload.match.group(2)))
            

    
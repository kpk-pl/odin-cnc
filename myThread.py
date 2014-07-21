#!/usr/bin/env python

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt

class myThread(QtCore.QObject):
    def __init__(self, parent=None):
        super(myThread, self).__init__(parent)
        self._runTimer = None
        
    def __del__(self):
        self.pause()        
                
    @QtCore.pyqtSlot()
    def pause(self):
        if self._runTimer:
            self._runTimer.stop()
            
    @QtCore.pyqtSlot()
    def start(self):
        if self._runTimer:
            self._runTimer.start(0)
            
    @QtCore.pyqtSlot()    
    def atStart(self):
        self._runTimer = QtCore.QTimer()
        self._runTimer.timeout.connect(self.loop)
        
    @QtCore.pyqtSlot()
    def loop(self):
        pass

def makeThread(worker):
    thread = QtCore.QThread()
    worker.moveToThread(thread)
    thread.started.connect(worker.atStart)
    thread.start()
    return thread
    
def startThread(worker):
    QtCore.QMetaObject.invokeMethod(worker, 'start', Qt.QueuedConnection)
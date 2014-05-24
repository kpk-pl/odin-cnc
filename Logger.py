#!/usr/bin/env python

from PyQt4 import QtCore
from PyQt4.QtCore import QMutex, QMutexLocker
from datetime import datetime

class Logger(QtCore.QObject):
    """
    Implement Pattern: SINGLETON
    """
    update = QtCore.pyqtSignal(str)
    
    __lockObj = QMutex()
    LOG, DEBUG, INFO, ERROR = ("LOG  ", "DEBUG", "INFO ", "ERROR")

    def __init__(self):
        super(Logger, self).__init__()
    
    def __call__(self):
        return self
        
    def getInstance(self):
        return self
        
    @QtCore.pyqtSlot(str,str)    
    def put(self, type, message):
        with QMutexLocker(Logger.__lockObj):
            Logger.update.emit(str(datetime.now()) + " " + type + ": " + str(message))
           
Logger = Logger()
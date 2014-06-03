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
    LOG, DEBUG, INFO, WARN, ERROR = ("LOG  ", "DEBUG", "INFO ", "WARN ", "ERROR")

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
            
    @QtCore.pyqtSlot(str)    
    def debug(self, message):
        self.put(Logger.DEBUG, message)      
    @QtCore.pyqtSlot(str)    
    def log(self, message):
        self.put(Logger.LOG, message)
    @QtCore.pyqtSlot(str)    
    def info(self, message):
        self.put(Logger.INFO, message)
    @QtCore.pyqtSlot(str)    
    def warn(self, message):
        self.put(Logger.WARN, message)        
    @QtCore.pyqtSlot(str)    
    def error(self, message):
        self.put(Logger.ERROR, message)      
           
"""
Overwrite class definition to prevent creation of new objects
SINGLETON
"""           
Logger = Logger()
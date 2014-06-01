#!/usr/bin/env python

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt

from TCPClient import TCPClient
from COMClient import COMClient
from Logger import Logger

class ConnectionManager(QtCore.QObject):
    result = QtCore.pyqtSignal(bool)
    
    def __init__(self, incomming_q, outgoing_q):
        super(ConnectionManager, self).__init__()
        
        self.in_q = incomming_q
        self.out_q = outgoing_q
        self.tcpClient = None
        self.comClient = None
        
    def __del__(self):
        if self.tcpClient is not None:
            self.tcpClient.join()
        if self.comClient is not None:
            self.comClient.join()
    
    @QtCore.pyqtSlot()
    def check(self):
        if self.tcpClient and not self.tcpClient.isAlive():
            self.tcpClient = None
            Logger.getInstance().error("WiFi connection closed unexpectedly")
            self.result.emit(False)
        if self.comClient and not self.comClient.isAlive():
            self.comClient = None
            Logger.getInstance().error("COM connection closed unexpectedly")
            self.result.emit(False)
        
    @QtCore.pyqtSlot(tuple)    
    def connect(self, parameters):
        self.stopAll()
        if parameters[0] == "WiFi":
            try:
                self.tcpClient = TCPClient((str(parameters[1]), int(parameters[2])), self.out_q, self.in_q)
            except Exception as e:
                self.tcpClient = None
                Logger.getInstance().error("Cannot start WiFi connection: " + str(e))
            else:
                self.tcpClient.start()
                Logger.getInstance().info("Connected to WiFi server")
        elif parameters[0] == "COM":
            try:
                self.comClient = COMClient(str(parameters[1]), int(parameters[2]), self.out_q, self.in_q)
            except Exception as e:
                self.comClient = None
                Logger.getInstance().error("Cannot start serial connection: " + str(e))
            else:
                self.comClient.start()
                Logger.getInstance().info("Connected to COM server")
        if self.comClient or self.tcpClient:
            self.result.emit(True)
        else:
            self.result.emit(False)
        
    def stopAll(self):
        if self.tcpClient is not None:
            self.tcpClient.join()
            self.tcpClient = None
            Logger.getInstance().info("Stopping TCP Client")
        if self.comClient is not None:
            self.comClient.join()
            self.comClient = None
            Logger.getInstance().info("Stopping COM Client")
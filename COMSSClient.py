#!/usr/bin/env python

import serial
import select
from Logger import Logger
from datetime import datetime
import Queue

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt

import myThread

class COMMarkedMessage(object):
    def __init__(self, payload, timestamp=None):
        self.payload = payload
        self.timestamp = timestamp

class COMSSClient(myThread.myThread):
    arrived = QtCore.pyqtSignal(COMMarkedMessage)

    def __init__(self, port, baudrate, parent=None):
        super(COMSSClient, self).__init__(parent)
       
        self._outgoing = Queue.Queue()
        self._outbuffer = ''
        self._inbuffer = ''
       
        # throwing instruction (throws IOError)
        self._socket = serial.Serial(port=port, baudrate=baudrate, 
            bytesize=serial.EIGHTBITS, stopbits=serial.STOPBITS_ONE, 
            parity=serial.PARITY_NONE, timeout=0.001, writeTimeout=0.001)
            
    def __del__(self):
        self.pause()
        try:
            self._socket.close()
        except AttributeError:
            pass
        
    @QtCore.pyqtSlot()
    def loop(self):
        timestamp = datetime.now()
        try:
            text = self._socket.read(1)
        except serial.SerialException as e:
            Logger.getInstance().error("Error in reading from COM port: " + str(e))
            return
        if text:
            self._inbuffer += text
            n = self._socket.inWaiting()
            if n:
                self._inbuffer += self._socket.read(n)
            splitted = self._inbuffer.splitlines()
            if self._inbuffer.endswith('\n') or len(splitted) == 0:
                self._inbuffer = ''
            else:
                self._inbuffer = splitted.pop()
            for line in splitted:
                if len(line):
                    self.arrived.emit(COMMarkedMessage(line, timestamp))
        elif len(self._outbuffer) > 0:
            try:
                send = self._socket.write(self._outbuffer)
            except Exception as e:
                Logger.getInstance().error("Error in sending via COM port: " + str(e))
                self.__del__()
            else:
                self._outbuffer = self._outbuffer[send:]
        elif not self._outgoing.empty():
            self._outbuffer += self._outgoing.get()
            
    @QtCore.pyqtSlot(str)
    def send(self, message):
        self._outgoing.put(message)
            
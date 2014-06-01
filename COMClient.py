#!/usr/bin/env python

import serial
import threading
import select
from Logger import Logger
from datetime import datetime

class COMMarkedMessage:
    def __init__(self, payload, timestamp=None):
        self.payload = payload
        self.timestamp = timestamp

class COMClient(threading.Thread):
###
# outgoing means going from PC to robot
# incomming means going from robot to PC
# log goes FROM this class
###
    def __init__(self, port, baudrate, outgoing_q, incomming_q):
        super(COMClient, self).__init__()
    
        self._alive = threading.Event()
        self._alive.set()
        
        self.outgoing = outgoing_q
        self.incomming = incomming_q
       
        self._outbuffer = ''
        self._inbuffer = ''
       
        # throwing instruction (throws IOError)
        self._socket = serial.Serial(port=port, baudrate=baudrate, 
            bytesize=serial.EIGHTBITS, stopbits=serial.STOPBITS_ONE, 
            parity=serial.PARITY_NONE, timeout=0.001, writeTimeout=0.001)
        
    def run(self, timeout=None):
        while self._alive.isSet():
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
                        self.incomming.put(COMMarkedMessage(line, timestamp))
            elif len(self._outbuffer) > 0:
                try:
                    send = self._socket.write(self._outbuffer)
                except Exception as e:
                    Logger.getInstance().error("Error in sending via COM port: " + str(e))
                    break
                else:
                    self._outbuffer = self._outbuffer[send:]
            elif not self.outgoing.empty():
                self._outbuffer += self.outgoing.get() 
        self._alive.set()

    def join(self, timeout=None):
        self._alive.clear()
        threading.Thread.join(self, timeout)
        self._socket.close()

if __name__ == '__main__':   
    import Queue
    out_q = Queue.Queue()
    in_q = Queue.Queue()
    client = TCPClient(('192.168.50.2', 4000), out_q, in_q)
    client.start()
    
    while True:
        msg = in_q.get(True)
        print msg
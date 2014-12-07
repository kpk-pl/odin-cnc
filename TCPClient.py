#!/usr/bin/env python

import socket
import threading
import select
from Logger import Logger
from datetime import datetime

class TCPMarkedMessage:
    def __init__(self, payload, timestamp=None):
        self.payload = payload
        self.timestamp = timestamp

class TCPClient(threading.Thread):
###
# outgoing means going from PC to robot
# incomming means going from robot to PC
# log goes FROM this class
###
    def __init__(self, address, outgoing_q, incomming_q):
        super(TCPClient, self).__init__()
    
        self._alive = threading.Event()
        self._alive.set()
        
        self.outgoing = outgoing_q
        self.incomming = incomming_q
       
        self._outbuffer = ''
        self._inbuffer = ''
       
        # throwing instruction (throws IOError)
        self._socket = socket.create_connection(address, 5.0)
        self._socket.setblocking(0)
        
    def run(self, timeout=None):
        while self._alive.isSet():
            try:
                readable, _, exceptional = select.select([self._socket], [], [self._socket], 0.0001) # very short time, 0.1ms to provide the smallest possible delays in network synchronization
            except Exception as e:
                Logger.getInstance().error("TCP connection select exception " + str(e))
            else:
                timestamp = datetime.now()
                if readable:
                    try:
                        self._inbuffer += self._socket.recv(1024)
                    except Exception as e:
                        Logger.getInstance().error("TCP error while receiving: " + str(e))
                    else:
                        splitted = self._inbuffer.splitlines()
                        if self._inbuffer.endswith('\n') or len(splitted) == 0:
                            self._inbuffer = ''
                        else:
                            self._inbuffer = splitted.pop()
                        for line in splitted:
                            self.incomming.put(TCPMarkedMessage(line, timestamp))
                elif len(self._outbuffer) > 0:
                    try:
                        send = self._socket.send(self._outbuffer)
                    except Exception as e:
                        Logger.getInstance().error("TCP error while sending: " + str(e))
                    else:
                        self._outbuffer = self._outbuffer[send:]
                elif not self.outgoing.empty():
                    self._outbuffer += self.outgoing.get()
                elif exceptional:
                    Logger.getInstance().error("Error in TCP communication")
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
#!/usr/bin/env python

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
import pyqtgraph as pg

from MainWindow import MainWindow
from ConnectionManager import ConnectionManager
import Queue

outgoing_queue = Queue.Queue()
incomming_queue = Queue.Queue()     
   
if __name__ == '__main__':
    import sys

    # setup pyqtgraph
    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k')
    pg.setConfigOption('antialias', True)
    
    app = QtGui.QApplication(sys.argv)
    window = MainWindow(incomming_queue, outgoing_queue)
    app.setActiveWindow(window)
       
    connMngrThread = QtCore.QThread()   
    connMngr = ConnectionManager(incomming_queue, outgoing_queue)
    connMngr.moveToThread(connMngrThread)
    connMngr.result.connect(window.connectDone)
    def startConnection(parameters):
        QtCore.QMetaObject.invokeMethod(connMngr, 'connect', Qt.QueuedConnection, 
            QtCore.Q_ARG(tuple, parameters))
    window.connectRequested().connect(startConnection)
    connMngrThread.started.connect(connMngr.setup)
    connMngrThread.start()
       
    window.show()
    
    retval = app.exec_()
    connMngrThread.quit()
    connMngrThread.wait()

    sys.exit(retval)

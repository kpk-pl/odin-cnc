#!/usr/bin/env python

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
import pyqtgraph as pg
import math, struct

from Logger import Logger
from CameraThread import CameraThread
from COMMngr import COMMngr
from COMSSClient import COMSSClient
import myThread
        
class CameraTab(QtGui.QWidget):
    def __init__(self, parent=None):
        super(CameraTab, self).__init__(parent)
        
        self.cameraThreadObject = CameraThread()
        self.cameraThread = QtCore.QThread()
        self.cameraThreadObject.moveToThread(self.cameraThread)
        
        self.setupGUI()
        
        self.settingsShowCapture.stateChanged.connect(self.settingsCaptureRadioMarked.setEnabled)
        self.settingsShowCapture.stateChanged.connect(self.settingsCaptureRadioUnfiltered.setEnabled)
        self.settingsShowCapture.stateChanged.connect(self.settingsCaptureRadioMask.setEnabled)
        self.settingsGainSelection.sigValueChanged.connect(self.settingsGainChanged)
        self.settingsExposureSelection.sigValueChanged.connect(self.settingsExposureChanged)
        self.settingsCaptureRadioUnfiltered.clicked.connect(self.settingsCaptureChanged)
        self.settingsCaptureRadioMarked.clicked.connect(self.settingsCaptureChanged)
        self.settingsCaptureRadioMask.clicked.connect(self.settingsCaptureChanged)
        
        self.settingsStartStopBtn.clicked.connect(self.connectButtonClicked)
        self.radioCOMRefreshButton.clicked.connect(self.refreshCOMPorts)
        self.radioConnectButton.clicked.connect(self.connectRadio)
        
        self.cameraThreadObject.frameCaptured.connect(self.updateFrame)
        self.cameraThread.started.connect(self.cameraThreadObject.setup)
        self.cameraThreadObject.message.connect(self.settingsStatusLabel.setText)
        self.cameraThreadObject.connected.connect(self.connected)
        self.cameraThreadObject.disconnected.connect(self.disconected)
        self.cameraThreadObject.fpsUpdated.connect(lambda x: self.settingsFPSCurrent.setText("%.1f" % (x)))
        self.cameraThreadObject.telemetry.connect(self.telemetryFromCamera)
        
        self.cameraThread.start()
        
    def __del__(self):
        self.cameraThread.quit()
        self.cameraThread.wait()
        
        if self.radioThread:
            self.radioThread.quit()
            self.radioThread.wait()
            
    def _cameraIsConnected(self):
        return self.settingsStartStopBtn.text() == "Stop"
            
    def tryDisconnectRadio(self):
        if self.radioConnectButton.text() == "Disconnect":
            self.radioThread.quit()
            self.radioThread.wait()
            del self.radioThread
            del self.radioThreadObject
            self.radioConnectButton.setText("Connect")
            self.radioStatusLabel.hide()
            Logger.getInstance().log("Radio connection closed")
            return True
        return False
        
    def tryStartCamera(self):
        if not self._cameraIsConnected():
            fps = float(self.settingsFPSSelection.value())
            options = {'gain': self.settingsGainSelection.value(), 
                'exposure': self.settingsExposureSelection.value(),
                'returnImage': 'marked' if self.settingsCaptureRadioMarked.isChecked() else 'unfiltered'}
            QtCore.QMetaObject.invokeMethod(self.cameraThreadObject, 'connect', Qt.QueuedConnection, 
                QtCore.Q_ARG(float, fps), QtCore.Q_ARG(dict, options))
            Logger.getInstance().info("Trying to start camera at %.2f fps" % (fps))
            return True
        return False
       
    def tryStopCamera(self):
        if self._cameraIsConnected():
            QtCore.QMetaObject.invokeMethod(self.cameraThreadObject, 'disconnect', Qt.QueuedConnection)
            Logger.getInstance().info("Trying to stop camera")
            return True
        return False
       
    @QtCore.pyqtSlot()
    def connectRadio(self):
        if self.tryDisconnectRadio():
            return

        com = str(self.radioCOMSelect.currentText())
        br = str(self.radioBaudrateEdit.text())
       
        try:
            self.radioThreadObject = COMSSClient(com, br)
        except Exception as e:
            Logger.getInstance().error("Cannot establish radio connection: " + str(e))
        else:
            self.radioThread = myThread.makeThread(self.radioThreadObject)
            self.radioThreadObject.arrived.connect(lambda x: Logger.getInstance().debug(x.payload))
            myThread.startThread(self.radioThreadObject)
            self.radioStatusLabel.show()
            Logger.getInstance().log("Radio connection established on " + com + " @" + br)
            self.radioConnectButton.setText("Disconnect")
       
    @QtCore.pyqtSlot()
    def connectButtonClicked(self):
        self.tryStartCamera() or self.tryStopCamera()
           
    @QtCore.pyqtSlot(tuple)
    def telemetryFromCamera(self, telemetry):
        if self.radioSendUpdates.isChecked():
            try:
                data = struct.pack('<3f', *telemetry)
                #QtCore.QMetaObject.invokeMethod(self.radioThreadObject, 'send', Qt.QueuedConnection, QtCore.Q_ARG(str, data))
                self.radioThreadObject._outgoing.put("<U"+data+"\n>")
            except (NameError, AttributeError):
                pass
            
        self.telemetryX.setText("%.2f" % (telemetry[0]))
        self.telemetryY.setText("%.2f" % (telemetry[1]))
        self.telemetryODeg.setText("%.2f" % (telemetry[2]))
        self.telemetryORad.setText("%.2f" % (telemetry[2]))
      
    @QtCore.pyqtSlot()
    def connected(self):
        self.settingsStartStopBtn.setText("Stop")
        Logger.getInstance().info("Camera started")
        
    @QtCore.pyqtSlot()
    def disconected(self):
        self.telemetryX.setText("?")
        self.telemetryY.setText("?")
        self.telemetryODeg.setText("?")
        self.telemetryORad.setText("?")
        self.settingsFPSCurrent.setText("?")
        self.settingsStartStopBtn.setText("Start")
        Logger.getInstance().info("Camera stopped")
           
    @QtCore.pyqtSlot(QtGui.QImage)
    def updateFrame(self, image):
        if self.settingsShowCapture.isChecked():
            pixmap = QtGui.QPixmap.fromImage(image)
            scaledPixMap = pixmap.scaled(self.frameLabel.size(), Qt.KeepAspectRatio)
            self.frameLabel.setPixmap(scaledPixMap)
       
    @QtCore.pyqtSlot()
    def refreshCOMPorts(self):
        current = self.radioCOMSelect.currentText()
        self.radioCOMSelect.clear()
        self.radioCOMSelect.addItems(list(COMMngr().getAllPorts()))
        self.radioCOMSelect.setCurrentIndex(self.radioCOMSelect.findText(current))
       
    @QtCore.pyqtSlot()
    def settingsGainChanged(self):
        if self._cameraIsConnected():
            QtCore.QMetaObject.invokeMethod(self.cameraThreadObject, 'setParam', Qt.QueuedConnection, 
                QtCore.Q_ARG(dict, {'gain': self.settingsGainSelection.value()} ))
            Logger.getInstance().info("Changing gain of working camera")
        
    @QtCore.pyqtSlot()
    def settingsExposureChanged(self):    
        if self._cameraIsConnected():
            QtCore.QMetaObject.invokeMethod(self.cameraThreadObject, 'setParam', Qt.QueuedConnection, 
                QtCore.Q_ARG(dict, {'exposure': self.settingsExposureSelection.value()} ))
            Logger.getInstance().info("Changing exposure of working camera")
       
    @QtCore.pyqtSlot()
    def settingsCaptureChanged(self):
        if self._cameraIsConnected():
            if self.settingsCaptureRadioMarked.isChecked():
                option = 'marked'
            elif self.settingsCaptureRadioMask.isChecked():
                option = 'mask'
            else:
                option = 'unfiltered'
            QtCore.QMetaObject.invokeMethod(self.cameraThreadObject, 'setParam', Qt.QueuedConnection, 
                QtCore.Q_ARG(dict, {'returnImage': option} ))
            Logger.getInstance().info("Changing return image type of working camera to " + option)
    
    def resetDefault(self):
        self.tryStopCamera()
        self.tryDisconnectRadio()

    def setupGUI(self):
        # main layout
        layout = QtGui.QHBoxLayout()
        layout.setMargin(10)
        self.setLayout(layout)
        leftSideWdgt = QtGui.QWidget()
        leftSideWdgt.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
        leftSideWdgt.setFixedWidth(250);
        self.frameLabel = QtGui.QLabel();
        layout.addWidget(leftSideWdgt)
        layout.addWidget(self.frameLabel)
        
        # left layout
        leftLayout = QtGui.QVBoxLayout()
        layout.setMargin(0)
        leftSideWdgt.setLayout(leftLayout)
        
        # settings
        self.settingsStartStopBtn = QtGui.QPushButton("Start")
        self.settingsFPSSelection = pg.SpinBox(bounds=[1,188], int=True, dec=False, minStep=1, step=10, suffix="fps")
        self.settingsFPSSelection.setValue(10)
        self.settingsFPSCurrent = QtGui.QLineEdit()
        self.settingsFPSCurrent.setReadOnly(True)
        self.settingsFPSCurrent.setText("?")
        self.settingsShowCapture = QtGui.QCheckBox("Show capture")
        self.settingsStatusLabel = QtGui.QLabel("Disconnected")
        self.settingsGainSelection = pg.SpinBox(bounds=[0,79], int=True, dec=False, minStep=1, step=5)
        self.settingsGainSelection.setValue(30)
        self.settingsExposureSelection = pg.SpinBox(bounds=[0,511], int=True, dec=False, minStep=1, step=10)
        self.settingsExposureSelection.setValue(400)
        self.settingsCaptureRadioUnfiltered = QtGui.QRadioButton("Unfiltered")
        self.settingsCaptureRadioUnfiltered.setDisabled(True)
        self.settingsCaptureRadioMask = QtGui.QRadioButton("Mask")
        self.settingsCaptureRadioMask.setDisabled(True)
        self.settingsCaptureRadioMarked = QtGui.QRadioButton("Marked")
        self.settingsCaptureRadioMarked.setDisabled(True)
        self.settingsCaptureRadioMarked.setChecked(True)
        
        settingsBox = QtGui.QGroupBox("Settings")
        settingsLayout = QtGui.QGridLayout()
        settingsLayout.setSpacing(3)
        settingsLayout.setMargin(5)
        settingsLayout.addWidget(self.settingsStartStopBtn, 0, 0, 1, 1)
        settingsLayout.addWidget(self.settingsFPSSelection, 0, 1, 1, 1)
        settingsLayout.addWidget(QtGui.QLabel("Current FPS"), 1, 0, 1, 1)
        settingsLayout.addWidget(self.settingsFPSCurrent, 1, 1, 1, 1)
        settingsLayout.addWidget(QtGui.QLabel("Gain"), 2, 0, 1, 1)
        settingsLayout.addWidget(self.settingsGainSelection, 2, 1, 1, 1)
        settingsLayout.addWidget(QtGui.QLabel("Exposure"), 3, 0, 1, 1)
        settingsLayout.addWidget(self.settingsExposureSelection, 3, 1, 1, 1)
        settingsLayout.addWidget(self.settingsShowCapture, 4, 0, 1, 1)
        settingsLayout.addWidget(self.settingsCaptureRadioUnfiltered, 4, 1, 1, 1)
        settingsLayout.addWidget(self.settingsCaptureRadioMask, 5, 1, 1, 1)
        settingsLayout.addWidget(self.settingsCaptureRadioMarked, 6, 1, 1, 1)
        settingsLayout.addWidget(self.settingsStatusLabel, 7, 0, 1, 2)
        settingsBox.setLayout(settingsLayout)
        leftLayout.addWidget(settingsBox)
        
        # radio
        self.radioCOMSelect = QtGui.QComboBox()
        self.radioCOMSelect.addItems(list(COMMngr().getAllPorts()))
        self.radioBaudrateEdit = QtGui.QLineEdit("500000")
        self.radioBaudrateEdit.setValidator(QtGui.QIntValidator(0, 10000000))
        self.radioConnectButton = QtGui.QPushButton("Connect")
        self.radioStatusLabel = QtGui.QLabel("Connected")
        self.radioStatusLabel.hide()
        self.radioCOMRefreshButton = QtGui.QPushButton("R")
        self.radioCOMRefreshButton.setMaximumWidth(25)
        self.radioSendUpdates = QtGui.QCheckBox("Enable radio transmission")
        self.radioSendUpdates.setChecked(True)
        
        radioBox = QtGui.QGroupBox("Radio transmitter")
        radioLayout = QtGui.QGridLayout()
        radioLayout.setSpacing(3)
        radioLayout.setMargin(5)
        radioLayout.addWidget(QtGui.QLabel("COM Port"), 0, 0, 1, 1)
        radioLayout.addWidget(QtGui.QLabel("Baudrate"), 0, 2, 1, 1)
        radioLayout.addWidget(self.radioCOMSelect, 1, 0, 1, 1)
        radioLayout.addWidget(self.radioCOMRefreshButton, 1, 1, 1, 1)
        radioLayout.addWidget(self.radioBaudrateEdit, 1, 2, 1, 1)
        radioLayout.addWidget(self.radioStatusLabel, 2, 0, 1, 2)
        radioLayout.addWidget(self.radioConnectButton, 2, 2, 1, 1)
        radioLayout.addWidget(self.radioSendUpdates, 3, 0, 1, 3)
        radioLayout.setColumnStretch(0, 1)
        radioLayout.setColumnStretch(1, 1)
        radioLayout.setColumnStretch(2, 1)
        radioBox.setLayout(radioLayout)
        leftLayout.addWidget(radioBox)
        
        # telemetry
        self.telemetryX = QtGui.QLineEdit("?")
        self.telemetryY = QtGui.QLineEdit("?")
        self.telemetryORad = QtGui.QLineEdit("?")
        self.telemetryODeg = QtGui.QLineEdit("?")
        self.telemetryX.setReadOnly(True)
        self.telemetryY.setReadOnly(True)
        self.telemetryORad.setReadOnly(True)
        self.telemetryODeg.setReadOnly(True)
        
        telemetryBox = QtGui.QGroupBox("Telemetry")
        telemetryLayout = QtGui.QGridLayout()
        telemetryLayout.setSpacing(3)
        telemetryLayout.setMargin(5)
        telemetryLayout.addWidget(QtGui.QLabel("X"), 0, 0, 1, 1)
        telemetryLayout.addWidget(self.telemetryX, 0, 1, 1, 3)
        telemetryLayout.addWidget(QtGui.QLabel("[mm]"), 0, 4, 1, 1)
        telemetryLayout.addWidget(QtGui.QLabel("Y"), 1, 0, 1, 1)
        telemetryLayout.addWidget(self.telemetryY, 1, 1, 1, 3)
        telemetryLayout.addWidget(QtGui.QLabel("[mm]"), 1, 4, 1, 1)
        telemetryLayout.addWidget(QtGui.QLabel("O"), 2, 0, 1, 1)
        telemetryLayout.addWidget(self.telemetryODeg, 2, 1, 1, 1)
        telemetryLayout.addWidget(QtGui.QLabel("[deg]"), 2, 2, 1, 1)
        telemetryLayout.addWidget(self.telemetryORad, 2, 3, 1, 1)
        telemetryLayout.addWidget(QtGui.QLabel("[rad]"), 2, 4, 1, 1)
        telemetryBox.setLayout(telemetryLayout)
        leftLayout.addWidget(telemetryBox)
        
        # end
        leftLayout.addStretch()
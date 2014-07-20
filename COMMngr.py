#!/usr/bin/env python

import itertools
import serial, os, re
from serial.tools import list_ports
import _winreg as winreg

from Logger import Logger

class COMMngr():
    def __init__(self):
        self._windowsRegistry = 'HARDWARE\\DEVICEMAP\\SERIALCOMM'
        
    def getAllPorts(self):
        ports = []
        if os.name == 'nt': # windows
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, self._windowsRegistry)
            except WindowsError as e:
                Logger.getInstance().warn("Serial ports scanner: Cannot open Windows registry key: " + str(e))
            else:
                for i in itertools.count():
                    try:
                        val = winreg.EnumValue(key, i)
                        m = re.match('^COM(\d+)$', str(val[1]))
                        if m:
                            ports.append("COM"+m.group(1))
                    except EnvironmentError:
                        break
        else: # unix
            for port in list_ports.comports():
                ports.append(port[0])
        return sorted(ports)
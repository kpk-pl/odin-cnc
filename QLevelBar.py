#!/usr/bin/env python

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt

class QLevelBar(QtGui.QWidget):
    def __init__(self, minimum=0, maximum=100.0, zero=None, parent=None):
        super(QLevelBar, self).__init__(parent)
        
        self.minimum = float(minimum)
        self.maximum = float(maximum)
        self.zero = float(zero) if zero is not None else min(self.minimum, self.maximum)
        self.value = self.zero
        self.textVisible = True
        self.orientation = Qt.Horizontal
        self.format = "%.2f"
        self.fontPen = QtGui.QPen(QtCore.Qt.black)
        self.pen = QtGui.QPen(QtGui.QColor(0,0,255,200))
        self.brush = QtGui.QBrush(QtGui.QColor(0,0,255,170))
        self.font = QtGui.QFont()
        self.font.setStyleHint(QtGui.QFont.Times, QtGui.QFont.PreferAntialias)
        self.font.setPointSize(11)
        
        self.setBackgroundRole(QtGui.QPalette.Base)
        self.setAutoFillBackground(True)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        
    def minimumSizeHint(self):
        return QtCore.QSize(2, 2)

    def sizeHint(self):
        return QtCore.QSize(100, 20)
        
    def setTextVisible(self, visible):
        self.textVisible = visible
        
    def setFormat(self, format):
        self.format = format
       
    @QtCore.pyqtSlot(float)
    @QtCore.pyqtSlot(int)   
    def setMinimum(self, minimum):
        self.minimum = float(minimum)
        self.update()
        
    @QtCore.pyqtSlot(float)
    @QtCore.pyqtSlot(int)
    def setMaximum(self, maximum):
        self.maximum = float(maximum)
        self.update()

    @QtCore.pyqtSlot(float)
    @QtCore.pyqtSlot(int)        
    def setRange(self, minimum, maximum):
        self.minimum = float(minimum)
        self.maximum = float(maximum)
        self.update()
        
    @QtCore.pyqtSlot(float)
    @QtCore.pyqtSlot(int) 
    def setZero(self, zero):
        if zero >= self.minimum and zero <= self.maximum:
            self.zero = float(zero) 
        self.update()
        
    @QtCore.pyqtSlot(QtGui.QColor)    
    def setColor(self, color):
        self.brush.setColor(color)
        self.pen.setColor(color)
        self.update()
        
    @QtCore.pyqtSlot(QtGui.QColor)      
    def setFontColor(self, color):
        self.fontPen.setColor(color)
        self.update()
        
    @QtCore.pyqtSlot(bool)    
    def setOrientation(self, orientation):
        self.orientation = orientation
        if orientation == Qt.Horizontal:
            self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        else:
            self.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        self.update()
        
    @QtCore.pyqtSlot()    
    def reset(self):
        self.setValue(self.zero)
        
    @QtCore.pyqtSlot(float)
    @QtCore.pyqtSlot(int)
    def setValue(self, value):
        self.value = float(value)
        self.update()
        
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(self.pen)
        painter.setBrush(self.brush)
        painter.setFont(self.font)
        
        size = self.size()
        right = float(self.value-min(self.minimum, self.maximum))/abs(self.maximum-self.minimum)
        left = float(self.zero-min(self.minimum, self.maximum))/abs(self.maximum-self.minimum)
        if left > right:
            left, right = right, left

        if self.orientation == Qt.Horizontal:
            topLeft = QtCore.QPointF(size.width()*left, 0)
            bottomRight = QtCore.QPointF(size.width()*right, size.height())
        else:
            topLeft = QtCore.QPointF(0, size.height()*left)
            bottomRight = QtCore.QPointF(size.width(), size.height()*right)
        
        painter.drawRect(QtCore.QRectF(topLeft, bottomRight))    
            
        if self.textVisible:
            val = (self.format % self.value)
            fm = QtGui.QFontMetrics(self.font)
            rect = fm.boundingRect(val)
            painter.setPen(self.fontPen)
            painter.drawText((size.width()-rect.width())/2-1, (size.height()+rect.height())/2-4, val)  
         
        painter.setBrush(QtGui.QBrush()) 
        painter.drawRect(0,0,size.width(), size.height());
    
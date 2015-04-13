#-*- encoding: utf-8 -*-
'''
Created on Apr 5, 2015
This is the Log file
@author: jiang
'''

from PyQt4 import QtGui,QtCore
from datetime import datetime

class LogMgr(QtGui.QDialog):
    def __init__(self,parent = None):
        '''
        initialize
        '''
        QtGui.QDialog.__init__(self,parent)
        self.textEdit = QtGui.QTextEdit()
        btn = QtGui.QPushButton('OK')
        
        btn.clicked.connect(self.hide)
        
        ly = QtGui.QVBoxLayout()
        ly.addWidget(self.textEdit)
        ly.addWidget(btn)
        
        self.setLayout(ly)
        self.resize(288, 320)
        self.setWindowTitle('Logs')
        
        today = datetime.now().strftime('%Y-%m-%d')
        self.textEdit.append('='*10 + today +'='*10)

        
    def writeLog(self,message):
        time = datetime.now().strftime('[%H:%M:%S] ')
        self.textEdit.append(time + message)
        
    
    def showLogs(self):
        # Scroll to end of the last message
        cursor = QtGui.QTextCursor(self.textEdit.textCursor())
        cursor.movePosition(QtGui.QTextCursor.End)
        self.textEdit.setTextCursor(cursor)
        QtGui.QApplication.processEvents()
        
        self.show()
        
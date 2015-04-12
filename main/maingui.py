#-*- encoding: utf-8 -*-
'''
Created on Apr 4, 2015
THis is the Main Window file
@author: jiang
'''
__author__ = 'Jiang Yunfei'
__version__ = '0.2.0'
__date__ = '2015.04'

import sys
import platform
from PyQt4 import QtCore,QtGui
from ui.ui_mainwindow import Ui_MainGUI

from main.tess import TessMgr
from main.file import FileMgr
from main.log import LogMgr
from main.roiview import ROIView
from main.param import Param 


class Michelangelo(QtGui.QMainWindow, Ui_MainGUI):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setupUi(self)
        self.initUi()
        
        self.initTools()
        
        self.initConnection()
        
        self.__isOpen = False
        self.__isROI = False
        self.__isOCR = False
        self.__isClear = False
        
        self.resize(1000, 650)
        self.setWindowTitle('Michelangelo')
        
    #initialize
    def initUi(self):
        self.roiview = ROIView()
        self.param = Param()
        self.info = QtGui.QMessageBox(self)
        
        rvWidght = self.roiview.getROIView()
        paWidght = self.param.getParamTree()
        self.centerLayout.addWidget(rvWidght)
        self.centerLayout.addWidget(paWidght)

    def initTools(self):
        self.log = LogMgr()
        self.file = FileMgr(self)
        self.tess = TessMgr()
            
    def initConnection(self):
        self.actionOpen.triggered.connect(self.openFile)
        self.actionAnalyze.triggered.connect(self.analyze)
        self.actionAddROI.triggered.connect(self.addROI)
        self.actionOCR.triggered.connect(self.ocr)
        self.actionClear.triggered.connect(self.clear)
        self.actionAbout.triggered.connect(self.about)
        self.actionSave.triggered.connect(self.save)
        self.actionExit.triggered.connect(self.exit)
        self.actionHelp.triggered.connect(self.help)
        
        self.connect(self.param, QtCore.SIGNAL('SaveClicked'),self.save)
        #请使用修正后的ViewBox.py文件
        self.connect(self.param, QtCore.SIGNAL('ROIHighlight'),self.roiview.highlightROI)
        '''
        MultiThread
        '''
        self.connect(self.tess, QtCore.SIGNAL('UpdateROI'), self.updateROI)
        
        self.connect(self.tess, QtCore.SIGNAL('UpdateOCR'), self.updateOCR)
        self.connect(self.tess, QtCore.SIGNAL('UpdateOCR'), self.info.close)
    
    
    def wirteLog(self,str):
        if str:
            self.log.writeMsg(str)
    
    def updateUi(self):
        if self.__isClear:
            self.__isClear = False
            self.__isROI = False
            self.__isOCR = False
            self.actionClear.setEnabled(False)
            self.actionOCR.setEnabled(False)
            self.actionSave.setEnabled(False)
        
        if self.__isOpen:
            self.actionAnalyze.setEnabled(True)
            self.actionAddROI.setEnabled(True)
            
        if self.__isROI:
            self.actionOCR.setEnabled(True)
            self.actionClear.setEnabled(True)
            
        if self.__isOCR:
            self.actionAnalyze.setEnabled(False)
            self.actionAddROI.setEnabled(False)
            self.actionClear.setEnabled(True)
            self.actionSave.setEnabled(True)
            
    #Actions
    def openFile(self):
        
        
        imgDir = self.file.openFile(type='image')
        if imgDir:
            self.clear()
            roi_image = self.file.getImage(imgDir,type='ROI')
            pix_image = self.file.getImage(imgDir,type='PIX')
            
            #set image            
            self.roiview.setIamge(roi_image)
            self.tess.setOCRImageSource(pix_image)
            
            self.setWindowTitle('Michelangelo - '+imgDir)
            self.__isOpen=True
            self.updateUi()
    
    def setupOCR(self):
        '''
        check the parameter if it is need to reflesh the options
        [1] check the param to get the OCR Options
        [2] set Options to the OCR
        '''
        ops= self.param.getParamOptions()
        self.tess.initTess(ops)
        
    
    def analyze(self):
        '''
        分析Rectangle区域
        '''        
        self.setupOCR()
        self.tess.startROIThread()
        
    
    def updateROI(self,boxa):
        if boxa:
            self.rect = self.file.boxa2rect(boxa)
            self.roiview.setROIs(self.rect)
            
            self.__isROI = True
            self.updateUi()
            
        else:
            print('ROI -> NULL')
        
    
    def addROI(self):
        '''
        增加ROI区域
        '''
        newArea = [40,40,100,100]
        self.roiview.addROI(newArea)

        self.__isROI = True
        self.updateUi()
        
    def ocr(self):
        '''
        文本识别并返回数据
        '''
        rdict = self.roiview.getPosDict()
        index= sorted(rdict)

        rlist = []
        for i in range(len(index)):
            key = index[i]
            value = rdict[key]
            iRect = [int(float(x)+0.5) for x in value] #truncate the numbers:FLoat to Int
            rlist.append(iRect)
        
        self.index = index
        self.setupOCR()
        self.tess.startOCRThread(rlist)
        
        #show Dialog
        self.showInfo('Tesseract OCR is working ...        ')
        
    def updateOCR(self,text):
        if text:
            self.param.setResult(text, self.index)
                        
            self.__isOCR = True
            self.updateUi()
        else:
            print('OCR -> NULL')
            
    def save(self):
        '''
        保存导出数据
        [1] get the final data from Param, ROI:
            'TAG':{
                'pos':xxx
                'text':xxx
                }
        [2] save data to file 
        '''
        if not self.__isOCR:
            print('SAVE ->OCR first!')
            return
        
        #Get text data
        text = self.param.getOutputText()
        
        #Get position data
        pos = self.roiview.getPosDict()
        
        if not (len(self.index) == len(text) and len(text)==len(pos)):
            print('[ERROR] The length of Index and Data is not equal')
            return
        
        outputData = {}
        for i in range(len(self.index)):
            info={}
            info['pos']=pos[self.index[i]]
            info['text']=text[i]
            outputData[self.index[i]] = info 

        self.file.saveFile(outputData, self.param.getFormat())
    
    def clear(self):
        '''
        清空并重置
        '''
        if self.__isROI:
            self.roiview.clearROIs()
        if self.__isOCR:
            self.param.clearResult()

        self.__isClear = True
        self.updateUi()
    
    def help(self):
        import webbrowser
        url = 'https://github.com/jiangyunfei/Michelangelo'
        webbrowser.open(url)
    
    def about(self):
        '''
        '''
        info = '''<h1>Michelangelo&trade;</h1>
                <h4>Version: %s (%s)</h4>
                <p>Copyright &copy;<a href="mailto:jiangyunfei93@bupt.edu.cn">%s</a>. All rights reserved.</p>
                <p>Python %s - PyQt %s - on %s</p>''' \
                % (__version__, __date__, __author__,platform.python_version(),
                QtCore.PYQT_VERSION_STR, platform.system())
                
        QtGui.QMessageBox.about(self,'About',info)
        
               
    def exit(self):
        '''
        关闭程序并保存
        '''
        if self.questionMessage('Do you want to Exit ?        '):
            self.close()

    #Dialogs:
    def showInfo(self,MESSAGE):
        self.info.setWindowTitle('Please wait')
        self.info.setIcon(QtGui.QMessageBox.Information)
        self.info.setText(MESSAGE)
        self.info.exec_()
        
        
    def questionMessage(self, MESSAGE='NULL'):     
        reply = QtGui.QMessageBox.question(self, "Michelangelo",
                MESSAGE,
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.Cancel)
        if reply == QtGui.QMessageBox.Yes:
            return True
        else:
            return False
        
        


'''
def informationMessage(self):    
    reply = QtGui.QMessageBox.information(self,
            "QMessageBox.information()", Dialog.MESSAGE)
    if reply == QtGui.QMessageBox.Ok:
        self.informationLabel.setText("OK")
    else:
        self.informationLabel.setText("Escape")

def questionMessage(self):    
    reply = QtGui.QMessageBox.question(self, "QMessageBox.question()",
            Dialog.MESSAGE,
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel)
    if reply == QtGui.QMessageBox.Yes:
        self.questionLabel.setText("Yes")
    elif reply == QtGui.QMessageBox.No:
        self.questionLabel.setText("No")
    else:
        self.questionLabel.setText("Cancel")

def warningMessage(self):    
    msgBox = QtGui.QMessageBox(QtGui.QMessageBox.Warning,
            "QMessageBox.warning()", Dialog.MESSAGE,
            QtGui.QMessageBox.NoButton, self)
    msgBox.addButton("Save &Again", QtGui.QMessageBox.AcceptRole)
    msgBox.addButton("&Continue", QtGui.QMessageBox.RejectRole)
    if msgBox.exec_() == QtGui.QMessageBox.AcceptRole:
        self.warningLabel.setText("Save Again")
    else:
        self.warningLabel.setText("Continue")

def errorMessage(self):    
    self.errorMessageDialog.showMessage("This dialog shows and remembers "
            "error messages. If the checkbox is checked (as it is by "
            "default), the shown message will be shown again, but if the "
            "user unchecks the box the message will not appear again if "
            "QErrorMessage.showMessage() is called with the same message.")
    self.errorLabel.setText("If the box is unchecked, the message won't "
            "appear again.")
'''



if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    cat = Michelangelo()
    cat.show()
    sys.exit(app.exec_())






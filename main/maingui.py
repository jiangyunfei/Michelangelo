#-*- encoding: utf-8 -*-
'''
Created on Apr 4, 2015
THis is the Main Window file
@author: jiang
'''

__author__ = 'Jiang Yunfei'
__version__ = '0.1.1'
__date__ = '2015.04'

import sys
import platform
from PyQt4 import QtCore,QtGui
from ui.ui_mainwindow import Ui_MainWindow

from main.tess import TessMgr
from main.file import FileMgr
from main.log import LogMgr
from main.roiview import ROIView
from main.param import Param 
from main.tesswarp import TessWarp

class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    """Class For MainWindow
    """
    
    def __init__(self, parent=None):
        """ Constructor
        """
        super(MainWindow, self).__init__(parent)
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
        
        self.rectDataList = None

        
        
    #initialize
    def initUi(self):
        self.roiview = ROIView()
        self.param = Param()
        
        rvWidght = self.roiview.getROIView()
        paWidght = self.param.getParamTree()
        self.centerLayout.addWidget(rvWidght)
        self.centerLayout.addWidget(paWidght)
        #self.dockLayout.addWidget(paWidght)
        self.progressBar.setVisible(False)

    
    def initTools(self):
        self.log = LogMgr()
        self.file = FileMgr(self)
        self.tess = TessMgr()
        
        self.tesswarp = TessWarp()
            
    def initConnection(self):
        self.actionOpen.triggered.connect(self.openFile)
        self.actionAnalyze.triggered.connect(self.analyze)
        self.actionAddROI.triggered.connect(self.addROI)
        self.actionOCR.triggered.connect(self.ocr)
        self.actionClear.triggered.connect(self.clear)
        self.actionAbout.triggered.connect(self.about)
        self.actionSave.triggered.connect(self.save)
        self.actionExit.triggered.connect(self.exit)
        
        self.connect(self.param, QtCore.SIGNAL('SaveClicked'),self.save)
        '''
        请使用修正后的ViewBox.py文件
        '''
        self.connect(self.param, QtCore.SIGNAL('ROIHighlight'),self.roiview.highlightROI)
    
    
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
        #get the Options:
        ops= self.param.getParamOptions()
        #set Options to OCR:
        self.tess.initTess(ops)
    
    def analyze(self):
        '''
        分析Rectangle区域
        '''
        #update the Options
        self.setupOCR()
        
        #get rects
        boxa = self.tess.getBoxa()
        if boxa is None:
            print('[ERROR] NULL')
            return
        
        self.rect = self.file.boxa2rect(boxa)
        self.roiview.setROIs(self.rect)
        
        self.__isROI = True
        self.updateUi()
        
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
        self.progressBar.setVisible(True)        
        #update the Options
        self.setupOCR()
        
        rdict = self.roiview.getPosDict()
        index= sorted(rdict)

        rlist = []
        for i in range(len(index)):
            key = index[i]
            value = rdict[key]
            iRect = [int(float(x)+0.5) for x in value] #truncate the numbers:FLoat to Int
            rlist.append(iRect)
        
        text= self.tess.getOCRText(rlist)
        if text:
            self.param.setResult(text, index)
            
            self.index = index
            self.__isOCR = True
            self.updateUi()
            
        self.progressBar.setVisible(False)
    
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
    
    def about(self):
        '''
        '''
        info = '''<h1>Michelangelo&trade;</h1>
                <h4>Version: %s (%s)</h4>
                <p>Copyright &copy;<a href="mailto:jiangyunfei93@bupt.edu.cn">%s</a>. All rights reserved.</p>
                <p>Python %s - PyQt %s - on %s</p>''' \
                % (__version__, __date__, __author__,platform.python_version(),
                QtCore.PYQT_VERSION_STR, platform.system())
                
        #QtGui.QMessageBox.about(self,'About',info)
        tag = '#02'
        self.roiview.highlightROI(tag)

    
    def exit(self):
        '''
        关闭程序并保存
        '''
        if self.questionMessage('Do you want to leave?'):
            self.close()

    
    #Dialogs:
    def questionMessage(self, msg='NULL', type=None):    
        reply = QtGui.QMessageBox.question(self, "Exit",
                msg,
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
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName("UTF-8"))
    app.setApplicationName('Michelangelo')
    app.setWindowIcon(QtGui.QIcon('../ui/icons/app.png'))
    cat = MainWindow()
    cat.show()
    sys.exit(app.exec_())






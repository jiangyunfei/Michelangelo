#-*- encoding: utf-8 -*-
'''
Created on Apr 4, 2015
THis is the Main Window file
@author: jiang
'''
__author__ = 'Jiang Yunfei'
__version__ = '0.5.0'
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
from main.parse import ParseMgr


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
        self.__isSaved = False
        self.outputData = {} #for final output
        
        #read setting:
        data = self.file.setting('LOAD')
        
        if data:
            self.file.setLastDir(data['DIR'])
            self.param.setting('LOAD', data['STATE'])
            
            
        self.resize(1000, 650)
        self.setWindowTitle('Michelangelo')
        
        if self.tess.VERSION: 
            self.LOG('Tesseract %s initialized!' % (self.tess.VERSION))
        else:
            self.LOG('Could not initialize tesseract.','red')
        
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
        self.log = LogMgr(self)
        self.file = FileMgr(self)
        self.tess = TessMgr(self)
        #self.parse = ParseMgr(self)
            
    def initConnection(self):
        self.actionOpen.triggered.connect(self.openFile)
        self.actionAnalyze.triggered.connect(self.analyze)
        #RubberBand
        #self.actionAddROI.triggered.connect(self.roiview.startRubberBandMode)
        self.actionAddROI.toggled.connect(self.addROIMode)
        
        self.actionOCR.triggered.connect(self.ocr)
        self.actionClear.triggered.connect(self.reset)
        self.actionAbout.triggered.connect(self.about)
        self.actionSave.triggered.connect(self.save)
        self.actionExit.triggered.connect(self.exit)
        self.actionHelp.triggered.connect(self.help)
        self.actionRestore.triggered.connect(self.restore)
        self.actionLog.triggered.connect(self.log.showLogs)
        #self.actionShow.triggered.connect(self.parse.show)
        self.actionShow.triggered.connect(self.parseJSON)
        
        #self.connect(self.param, QtCore.SIGNAL('SaveClicked'),self.save)
        #请使用修正后的ViewBox.py, ParameterTree文件
        self.connect(self.param, QtCore.SIGNAL('ROIHighlight'),self.roiview.highlightROI)
        
        #MultiThread
        self.connect(self.tess, QtCore.SIGNAL('UpdateROI'), self.updateROI)
        self.connect(self.tess, QtCore.SIGNAL('UpdateROI'), self.info.hide)
        
        self.connect(self.tess, QtCore.SIGNAL('UpdateOCR'), self.updateOCR)
        self.connect(self.tess, QtCore.SIGNAL('UpdateOCR'), self.info.hide)
        
        #self.connect(self.tess, QtCore.SIGNAL('OCRTEST'), self.updateOCRTEST)
        #self.connect(self.tess, QtCore.SIGNAL('OCRTEST'), self.info.hide)
        
        #RubberBand
        self.connect(self.roiview, QtCore.SIGNAL('RubberBand'), self.addROI)
        
        #Parse
        #self.connect(self.tess, QtCore.SIGNAL('SETPARSE'), self.parse.drawData)

        
    def updateUi(self):
        if self.__isClear:
            self.__isClear = False
            self.__isROI = False
            self.__isOCR = False
            self.actionClear.setEnabled(False)
            self.actionOCR.setEnabled(False)
            self.actionSave.setEnabled(False)
            self.actionShow.setEnabled(False)
        
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
            self.actionShow.setEnabled(True)
            
    #Actions
    def openFile(self, restore=False):
        
        if not restore:
            imgDir = self.file.openFile('image')
        else:
            imgDir = self.outputData['IMG']
            
        if imgDir:
            self.clear()
            roi_image = self.file.getImage(imgDir,'ROI')
            pix_image = self.file.getImage(imgDir,'PIX')
            
            #set image            
            self.roiview.setIamge(roi_image)
            self.tess.setOCRImageSource(pix_image)
            
            #self.parse.setImage(roi_image)
            
            self.setWindowTitle('Michelangelo - '+imgDir)
            self.outputData['IMG'] = str(imgDir)
            self.__isOpen=True
            self.updateUi()
            
            self.LOG('OPEN FILE -> '+imgDir)
    
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
        if self.__isROI:
            if not self.questionMessage('Do you want to Re-ROI ?        '):
                return 
                
        self.setupOCR()
        self.tess.startROIThread()
        
        self.LOG('[ROI] Searching...')
        #show Dialog
        self.showInfo('Tesseract OCR is searching ...        ')
    
        
    def boxa2rect(self,boxa):
        if boxa:
            rect = self.file.boxa2rect(boxa)
            return rect 
    
    
    def updateROI(self,boxa):
        if boxa:
            self.rect = self.file.boxa2rect(boxa)
            self.roiview.setROIs(self.rect)
            
            self.__isROI = True
            self.updateUi()
            self.LOG('[ROI] Find '+str(len(self.rect)) , 'green')
            
        else:
            self.log.writeLog('[ROI] No component found. Try to change PSM or RIL.', 'red')
    
    def addROIMode(self):
        flag = self.actionAddROI.isChecked()
        if flag:
            self.roiview.setRubberBandMode(True)
        else:
            self.roiview.setRubberBandMode(False)
            self.updateUi()
            
   
    def addROI(self,area = None):
        if area is None:
            area = [100,100,100,100]
        
        #print(area)    
        self.roiview.addROI(area)

        self.__isROI = True

        
    def ocr(self):
        '''
        文本识别并返回数据
        '''
        if self.__isOCR:
            if not self.questionMessage('Do you want to Re-OCR ?        '):
                return
        
        
        rdict = self.roiview.getPosDict()
        index= sorted(rdict)

        rlist = []
        for i in range(len(index)):
            key = index[i]
            value = rdict[key]
            iRect = [int(float(x)+0.5) for x in value] #truncate the numbers:FLoat to Int
            rlist.append(iRect)
        
        
        #set blocks
        #self.parse.setBlocks(rlist, index)
        
        self.index = index
        self.setupOCR()
        self.tess.startOCRThread(rlist)
        
        self.LOG('[OCR] Working...')
        
        #show Dialog
        self.showInfo('Tesseract OCR is working ...        ')
        
        
    def updateOCR(self,text,innerPos):
        if text:
            self.param.setResult(text, self.index)
                        
            self.__isOCR = True
            self.updateUi()
            
            #store the pos:
            self.outputData['innerPos'] = innerPos
            
            self.LOG('[OCR] Set Results!')
        else:
            self.LOG('[OCR] ERROR ->NULL RETURN','red')
            
            
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
        #Get text data
        text = self.param.getOutputText()
        
        #Get position data
        pos = self.roiview.getPosDict()
        innerPos = self.outputData.get('innerPos')
        
        if not (len(self.index) == len(text) and len(text)==len(pos)):
            self.LOG('[ERROR] The length of Index and Data is not equal', 'red')
            return

        for i in range(len(self.index)):
            info={}
            info['pos']=pos[self.index[i]] #pos is a dict
            info['innerPos']=innerPos[i]
            info['text']=text[i]
            self.outputData[self.index[i]] = info 
        
        msg = self.file.saveFile(self.outputData.copy(), self.param.getFormat())
        
        if msg:
            self.LOG('SAVE FILE -> '+ msg)
            self.__isSaved = True
    
    
    def reset(self):
        if self.warningMessage('All your results will be clean, confirm ?        '):
            self.clear()
    
    
    def clear(self):
        '''
        清空并重置
        '''
        if self.__isROI:
            self.roiview.clearROIs()
            
        if self.__isOCR:
            self.param.clearResult()
            
        if self.actionAddROI.isChecked():
            self.actionAddROI.setCheckable(False)
            self.addROIMode()

        
        self.__isClear = True
        self.updateUi()
        self.LOG('Cleared!','red')
    
    def help(self):
        import webbrowser
        url = 'https://github.com/jiangyunfei/Michelangelo'
        webbrowser.open(url)
    
    def about(self):
        info = '''<h1>Michelangelo&trade;</h1>
                <h4>Version: %s (%s)</h4>
                <p>Copyright &copy;<a href="mailto:jiangyunfei93@bupt.edu.cn">%s</a>. All rights reserved.</p>
                <p>Python %s - PyQt %s - on %s</p>
                <p><a href="https://github.com/jiangyunfei/Michelangelo/blob/master/LICENSE">Apache License, Version 2.0</a></p>''' \
                % (__version__, __date__, __author__,platform.python_version(),
                QtCore.PYQT_VERSION_STR, platform.system())
                
        QtGui.QMessageBox.about(self,'About',info)
               
    def exit(self):
        '''
        关闭程序并保存
        ''' 
        if self.__isOpen:      
            if self.questionMessage('Do you want to Exit ?        '):
                if self.__isOCR and not self.__isSaved:
                    if self.questionMessage('Do you want to save before exiting ?        '):
                        self.save()
                
                #save settings:
                data = {}
                data['DIR'] = self.file.lastDir
                data['STATE'] = self.param.setting('SAVE')
                self.file.setting('SAVE', data)
            
                self.close()
        else:
            self.close()
            
            
    def restore(self):
        '''
        Restore:
        load json file
        clear
        ->load img
        ->parse info:
            ->reflesh index
            ->generate pos
            ->generate text
        ->updateOCR
        '''
        path = self.file.openFile('json')
        
        if path:
            self.LOG('[RESTORE] '+path, 'green')
            self.outputData = self.file.parseJson(path)
            self.openFile(restore=True)
            
            keys = sorted(self.outputData.keys())
            
            self.index = []
            text = []
            pos = []
            innerPos = []
            for key in keys:
                if key == 'IMG':
                    continue
                item = self.outputData[key]
                text.append(item['text'])
                pos.append(item['pos'])
                self.index.append(key)
                
                innerPos.append(item['innerPos'])
            
            self.roiview.setROIs(pos, self.index)

            self.__isROI = True
            self.updateOCR(text,innerPos)
            
            
    def LOG(self,message,color=None):
        '''
        write logs and update the statusBar
        '''
        if message:
            self.statusBar.showMessage(message, 3000)
            
            msg = message
            if color:
                msg = '<span style="color:%s"> %s </span>'%(color, message)
            
            self.log.writeLog(msg)
    
    
    def parseJSON(self):
        
        #pop the choose dialog:
        clist = QtCore.QStringList()
        clist <<'Horizontal'<<'Vertical'
        ori, re = QtGui.QInputDialog.getItem(self, 'Confirm Arguments', 
                                                'Select the Orientation of the text:        ', 
                                                clist, 0, False)
        if not re:
            return
                
        '''
        the img
        the pos and index
        the innerPos
        the text
        '''
        #img
        imgDir = self.outputData['IMG']
        roi_image = self.file.getImage(imgDir,'ROI')
        
        #block
        posDict = self.roiview.getPosDict()
        posList = [posDict[i] for i in self.index] #transfer to list
        
        #text and pivot
        text = self.param.getOutputText()
        innerPos = self.outputData['innerPos']
                
        #process the text to fill the FORMAT
        
        for i in range(len(text)):
            tmp = text[i]
            tmp = tmp.rstrip('\n') #here, there should be no '\n' in the end
            innerList = tmp.splitlines(True)
            
            # if the oritention is vertical need add the '\n'
            for j in range(len(innerList)):
                line = innerList[j]
                if ori == 'Vertical':
                    line = line.replace('','\n')
                    
                line = line.strip('\n') #remove the \n in the end
                innerList[j] = line
            
            text[i] = innerList
  

        self.parse = ParseMgr(self)
        self.parse.setImage(roi_image)
        self.parse.setBlocks(posList, self.index)
        self.parse.setText(text,innerPos)
        
        self.parse.show()
        
        '''
        Remain：
        [1] Oritention Option -DONE
        [2] Image Process
        '''

        
    #Dialogs:
    def showInfo(self,MESSAGE):
        self.info.setWindowTitle('Please wait')
        self.info.setIcon(QtGui.QMessageBox.Information)
        self.info.setText(MESSAGE)
        self.info.exec_()
    
    def warningMessage(self, MESSAGE='NULL'):
        reply = QtGui.QMessageBox.warning(self, 'Attention', MESSAGE,
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.Cancel)
        if reply == QtGui.QMessageBox.Yes:
            return True
        else:
            return False    
        
    def questionMessage(self, MESSAGE='NULL'):     
        reply = QtGui.QMessageBox.question(self, "Michelangelo",MESSAGE,
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            return True
        else:
            return False
        

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    cat = Michelangelo()
    cat.show()
    sys.exit(app.exec_())






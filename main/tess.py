#-*- encoding: utf-8 -*-
'''
Created on Apr 5, 2015
This is the OCR Engine file
@author: jiang
'''
import os
import locale
import ctypes
import threading
from PyQt4 import QtCore
from libs import tesstool


class TessMgr(QtCore.QObject):
    def __init__(self,parent = None):
        QtCore.QObject.__init__(self)
        '''
        initialize
        '''
        self.tesseract = tesstool.get_tesseract(os.path.dirname(__file__))
        if not self.tesseract:
            print('Tesseract initialization failed...')
            return
        
        self.api = self.tesseract.TessBaseAPICreate()
        self.tessdata_prefix = tesstool.get_tessdata_prefix()
        locale.setlocale(locale.LC_ALL, 'C')
            
        #print('Tesseract %s initialized!' % (tesstool.VERSION)) 
        
        self.pixImage = None
        self.VERSION = tesstool.VERSION
        
        self.parent = parent
        
    def setOCRImageSource(self, pixImage):
        # Set PIX structure to tesseract api
        self.pixImage = pixImage      
        
    def initTess(self,ops):
        
        '''
        ops, dictionary, Keys: Language, Oritention, PSM, RIL
        it seems that Tesseract needn't Oritention
        '''
        self.lang = ops['Language']
        self.PSM = ops['PSM']
        self.RIL = ops['RIL']
        
        self.__isReady = False
        isFailure = self.tesseract.TessBaseAPIInit3(self.api,self.tessdata_prefix,self.lang)
        if isFailure:
            self.tesseract.TessBaseAPIDelete(self.api)
            print('<span style="color:red">Could not initialize tesseract.</span>')
            return
        
        self.tesseract.TessBaseAPISetImage2(self.api, self.pixImage)
        self.tesseract.TessBaseAPIReadConfigFile(self.api, 
                                                 tesstool.turn2char('opitimize'))
        

        #print('Tess Ready!')
        
        
    def clearAPI(self):
        #Clear
        self.tesseract.TessBaseAPIClear(self.api) 
        self.tesseract.TessBaseAPIEnd(self.api)
    
    
    def startROIThread(self):
        t = threading.Thread(target=self.getBoxa)
        t.start()
    
    def startOCRThread(self,rects):
        t = threading.Thread(target=self.getOCRText, args=(rects,))
        t.start()
    
    
    def getBoxa(self):        
        self.tesseract.TessBaseAPISetPageSegMode(self.api, 
                                                 tesstool.turn2Cint(self.PSM))
        
        #API args: (TessBaseAPI* handle, TessPageIteratorLevel level, BOOL text_only, PIXA** pixa, int** blockids)
        
        boxa = self.tesseract.TessBaseAPIGetComponentImages(self.api,
                                                            tesstool.turn2Cint(self.RIL),
                                                            True, None, None)
        
        if not boxa:
            return
        
        self.clearAPI()
        #return boxa

        self.emit(QtCore.SIGNAL('UpdateROI'),boxa)
        #print('ROI done!')
    
    
    def getOCRText(self,rects):
        if rects is None:
            return
        
        '''
        for every block:
            get the block pos
                restore the left-top point
                
            analyze with textline
                get the boxa
                (tesseract is smart which returns the results with right to left order)
                
            turn2rect
                add the left-top point
                return the correct rect
            
            use the nomoral ocr
                return the results
                exclude the \n
                appand to a list 
                return the result
            
        '''
        
        data = []
        pos = []
        rawText = []
        for r in rects:
                
                self.tesseract.TessBaseAPISetRectangle(self.api,
                                                       tesstool.turn2Cint(r[0]),
                                                       tesstool.turn2Cint(r[1]), 
                                                       tesstool.turn2Cint(r[2]), 
                                                       tesstool.turn2Cint(r[3]))
                
                # TessBaseAPI* handle, PIXA** pixa, int** blockids
                #boxa = self.tesseract.TessBaseAPIGetTextlines(self.api, None, None)
                
                self.tesseract.TessBaseAPISetPageSegMode(self.api, 
                                                         tesstool.turn2Cint(self.PSM))
        
                #API args: (TessBaseAPI* handle, TessPageIteratorLevel level, BOOL text_only, PIXA** pixa, int** blockids)
                mode = 2 #['RIL_BLOCK', 'RIL_PARA', 'RIL_TEXTLINE', 'RIL_WORD', 'RIL_SYMBOL']
                boxa = self.tesseract.TessBaseAPIGetComponentImages(self.api,
                                                                    tesstool.turn2Cint(mode),
                                                                    True, None, None)
                '''
                boxa2rect
                add the point
                '''
                areas = self.parent.boxa2rect(boxa)
                
                textPos= []
                for rect in areas:
                    rect[0] += r[0]
                    rect[1] += r[1]

                    textPos.append(rect)
                    
                text = self.getBlockText(areas) #text is a string list
                rawText.append(text)
                
                newText = []
                for t in text:
                    tmp = t.replace('\n', '')
                    tmp += '\n'
                    newText.append(tmp)
                
                strTmp = ''.join(unicode(x) for x in newText) #convert a list to string                
                data.append(strTmp)
                
                pos.append(textPos)
                
        self.clearAPI()
        self.emit(QtCore.SIGNAL('UpdateOCR'),data)
        self.emit(QtCore.SIGNAL('SETPARSE'),pos,rawText)
        #print('OCR TEST done!')
    
    
    def getBlockText(self,areas):
        '''
        import the vertical areas
        export the horizontal text lines
        '''
        
        ril = tesstool.RIL[self.RIL]
        if ril == 'RIL_BLOCK':
            ocr_psm = tesstool.PSM_SINGLE_BLOCK
        else:
            ocr_psm = tesstool.PSM_SINGLE_BLOCK_VERT_TEXT
        
        self.tesseract.TessBaseAPISetPageSegMode(self.api, ocr_psm)
        
        data = []
        for r in areas:
                self.tesseract.TessBaseAPISetRectangle(self.api,
                                                       tesstool.turn2Cint(r[0]),
                                                       tesstool.turn2Cint(r[1]), 
                                                       tesstool.turn2Cint(r[2]), 
                                                       tesstool.turn2Cint(r[3]))
                
                ocr_result = self.tesseract.TessBaseAPIGetUTF8Text(self.api)
                
                text = unicode(ctypes.string_at(ocr_result).decode('utf-8').strip())
                data.append(text)
        
        return data
        


        
            
                
        
        
    
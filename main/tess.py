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
    def __init__(self):
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
        
        ocr_psm = tesstool.PSM_SINGLE_BLOCK
        ril = tesstool.RIL[self.RIL]
        if ril == 'RIL_PARA':
            ocr_psm = tesstool.PSM_SINGLE_BLOCK
        elif ril == 'RIL_TEXTLINE':
            ocr_psm = tesstool.PSM_SINGLE_LINE
        elif ril == 'RIL_WORD':
            ocr_psm = tesstool.PSM_SINGLE_WORD
        elif ril == 'RIL_SYMBOL':
            ocr_psm = tesstool.PSM_SINGLE_CHAR
         
        self.tesseract.TessBaseAPISetPageSegMode(self.api, ocr_psm)
        
        data = []
        for r in rects:
                self.tesseract.TessBaseAPISetRectangle(self.api,
                                                       tesstool.turn2Cint(r[0]),
                                                       tesstool.turn2Cint(r[1]), 
                                                       tesstool.turn2Cint(r[2]), 
                                                       tesstool.turn2Cint(r[3]))
                
                ocr_result = self.tesseract.TessBaseAPIGetUTF8Text(self.api)
                #text = ocr_result.strip().decode('utf-8')
                result_text = ctypes.string_at(ocr_result).decode('utf-8').strip()
                data.append(unicode(result_text))
        
        self.clearAPI()
        
        self.emit(QtCore.SIGNAL('UpdateOCR'),data)
        #print('OCR done!')
        
    

        
        
    

        
            
                
        
        
    
#-*- encoding: utf-8 -*-
'''
Created on Apr 5, 2015
This is the OCR Engine file
@author: jiang
'''
import os
import locale
import ctypes
from libs import tesstool
from chardet.universaldetector import UniversalDetector


class TessMgr:
    def __init__(self):
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
        
        '''
        此处可以让Tesseract加载优化东亚文字字符识别的config
        ''' 
        try:
            opi = tesstool.turn2char('opitimize')
            
            #self.tesseract.TessBaseAPIReadConfigFile(self.api, opi)
            #print('！！！未加载文件！！！->未知错误')
        except Exception:
            print('Load file ERROR!')
        else:
            print('[FALSE]Tesseract Opitimized file loaded！')
            
        print('Tesseract %s initialized!' % (tesstool.VERSION)) 
        
        self.__isReady = False
        self.__OCRLOCK = False
        self.pixImage = None
        
        
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
        print('Tess Ready!')
        self.__isReady = True
        
        
    def clearAPI(self):
        #Clear
        self.tesseract.TessBaseAPIClear(self.api) 
        self.tesseract.TessBaseAPIEnd(self.api)
        print('OCR -> UNLOCKED')
        self.__OCRLOCK = False

    def checkAPI(self):
        if not self.__isReady:
            return False
        
        if self.__OCRLOCK:
            print('ERROR->OCR is Working')
            return False
        return True
    
    def getStatus(self):
        return self.__OCRLOCK
    
    def getBoxa(self):
        if not self.checkAPI():
            return
        else:
            self.__OCRLOCK = True
        
        self.tesseract.TessBaseAPISetPageSegMode(self.api, 
                                                 tesstool.turn2Cint(self.PSM))
        
        #API args: (TessBaseAPI* handle, TessPageIteratorLevel level, BOOL text_only, PIXA** pixa, int** blockids)
        boxa = self.tesseract.TessBaseAPIGetComponentImages(self.api,
                                                            tesstool.turn2Cint(self.RIL),
                                                            True, None, None)
        
        
        if not boxa:
            print('No component found. Try to change PSM or RIL.')
            return
        
        self.clearAPI()
        return boxa
    
        
    def getOCRText(self,rects): 
        print(self.__OCRLOCK)
        if not self.checkAPI():
            return None
        else:
            self.__OCRLOCK = True
        
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
        
        textList = []
        for r in rects:
                self.tesseract.TessBaseAPISetRectangle(self.api,
                                                       tesstool.turn2Cint(r[0]),
                                                       tesstool.turn2Cint(r[1]), 
                                                       tesstool.turn2Cint(r[2]), 
                                                       tesstool.turn2Cint(r[3]))
                
                ocr_result = self.tesseract.TessBaseAPIGetUTF8Text(self.api)
                #text = ocr_result.strip().decode('utf-8')
                result_text = ctypes.string_at(ocr_result).decode('utf-8').strip()
                textList.append(result_text)
        
        self.clearAPI()
        return textList
    

        
        
    

        
            
                
        
        
    

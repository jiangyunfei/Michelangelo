#-*- encoding: utf-8 -*-
'''
Created on Apr 9, 2015

@author: jiang
'''
from tesserwrap import Tesseract, PageSegMode


class TessWarp:
    def __init__(self):
        '''
        eng #English
        chi_sim #Simplified Chinese
        chi_tra #Traditional Chinese
        '''
        lang = 'eng'
        path = '/usr/local/share/tessdata/' 

        self.rectList = []
        self.tr = Tesseract(path,lang)
    
    def setOCRImage(self, pix_image):
        self.img = pix_image
    
            
    def getTextArea(self):
        self.tr.set_image(self.img)
        self.tr.set_page_seg_mode(mode=PageSegMode.PSM_AUTO_OSD)
        
        self.tr.ocr_image(self.img)
        lst = self.tr.get_textlines()
        size = len(lst)
        print('Amount: '+str(size))
        for i in range(size):
            rect = lst[i].box
            if self.textDetector(rect):
                self.rectList.append(rect)

        return self.rectList
    
    
    def textDetector(self,rect):
        '''
        *70 < the number of the black pixels <7999
        *horizontal range of the black pixels <100
        *0.2 < the ratio of the horizontal range and the vertical range of the black pixels < 10
        *0.43 < the percentage of the area of the image the black pixels cover  
        OR 3000< the number of the black pixels
        '''
        #the horizontal range and vertical range
        x1,y1,x2,y2 = rect
        w=abs(x2-x1)
        h=abs(y2-y1)
        if w>350:
            print('[1]horizontal range False: %s'%w)
            return False
        print('[1]horizontal range PASS: %s'%w)
        ratio = w/h
        if ratio<0.2 or ratio>12:
            print('[2]ratio range False: %s'%ratio)
            return False
        print('[2]ratio range PASS: %s'%ratio)
        
        print('-->')
        print(' '*5+'Text Area')
        return True
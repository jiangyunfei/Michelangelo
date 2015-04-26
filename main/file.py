#-*- encoding: utf-8 -*-
'''
Created on Apr 5, 2015
This is the file controller
@author: jiang
'''
from PIL import Image
import numpy
import json
from PyQt4 import QtGui, QtCore
from libs import lepttool


class FileMgr:
    def __init__(self,parent = None):
        '''
        initialize
        '''
        self.leptonica = lepttool.get_leptonica()
        self.parent = parent
        self.imageDir = None
        
        self.dafultDir = {'default': QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.HomeLocation),
                        'image': QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.PicturesLocation),
                        'json': QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.DocumentsLocation) }
        
        self.lastDir = {'image':None,
                        'json':None}
    
    def setLastDir(self,data):
        self.lastDir = data
        
    def openFile(self,TYPE):
        
        if self.lastDir[TYPE] is None:
            self.lastDir[TYPE] = self.dafultDir[TYPE]
                
        if TYPE == 'image':
            imageDir = QtGui.QFileDialog.getOpenFileName(self.parent,'Open Image file',self.lastDir[TYPE],
                        'Images (*.jpg *.jpeg *.bmp *.png *.tiff *.tif *.gif);;All files (*.*)')
            
            if imageDir:
                self.imageDir = imageDir
                
                self.lastDir[TYPE] = str(QtCore.QFileInfo(imageDir).absolutePath()) 
                
                return imageDir
            
        elif TYPE == 'json':
            jsonDir = QtGui.QFileDialog.getOpenFileName(self.parent, 'Load Json file',self.lastDir[TYPE],
                                                     'JSON (*.json);;All files (*.*)')
            if jsonDir:
                self.lastDir[TYPE] = str(QtCore.QFileInfo(jsonDir).absolutePath()) 
                return jsonDir
                        
    def getImage(self,imageDir,TYPE):
        
        self.loadIamge(imageDir)
        
        if TYPE == 'PIX':
            return self.pix_image
        elif TYPE == 'PIL':
            return self.PILimage
        elif TYPE == 'ROI':
            return self.ROIimage
    
    def parseJson(self,filePath):
        with open(filePath) as data_file:    
            data = json.load(data_file)
        if data:
            return data   
    
        
    def loadIamge(self,filename):
        self.image_name = str(filename)  # filename must be c-string
        
        # Read image with leptonica => create PIX structure and report image
        # size info
        self.pix_image = self.leptonica.pixRead(self.image_name)
        
        self.image_width = self.leptonica.pixGetWidth(self.pix_image)
        self.image_height = self.leptonica.pixGetHeight(self.pix_image)
        
        img = Image.open(self.image_name)
        self.PILimage = img

        img = img.transpose(Image.FLIP_LEFT_RIGHT)
        img = img.rotate(90)
        self.ROIimage =numpy.array(img)
        
        self.__isLoad = True

    
    def saveFile(self,data,FORMAT):
        if data is None:
            return
        
        #pop the useless innerPos
        data.pop('innerPos')
        
        TYPE = 'json'
        if self.lastDir[TYPE] is None:
            self.lastDir[TYPE] = self.dafultDir[TYPE]
        
        filePath = QtGui.QFileDialog.getSaveFileName(self.parent, 'Save file',self.lastDir[TYPE],
                                                     'FILE (*.json *.txt);;All files (*.*)')
        if filePath:
            self.lastDir[TYPE] = str(QtCore.QFileInfo(filePath).absolutePath()) 
            
            outfileDir = filePath+FORMAT
            outfile = open(outfileDir, "w")
            if FORMAT =='.json':
                json.dump(data, outfile)
            elif FORMAT == '.txt':
                keys = sorted(data.keys())
                for key in keys:
                    if key == 'IMG':
                        continue
                    val = data[key]
                    text = val['text']
                    outfile.write(('='*10 +' %s '+'='*10)%(key))
                    outfile.write('\n%s\n\n'%(text.encode('utf-8')))
            
            outfile.close()   
            return outfileDir         
            
    def boxa2rect(self,boxa):
        
        rectList = []
        # Get info about number of items on image
        n_items = self.leptonica.boxaGetCount(boxa)
        #print('Find %s '%n_items)
        
        # Set up result type (BOX structure) for leptonica function boxaGetBox
        self.leptonica.boxaGetBox.restype = lepttool.BOX_PTR_T
        self.leptonica.boxaGetBox.argtypes = []
        
        # Display items and print its info
        for item in range(n_items):
            lept_box = self.leptonica.boxaGetBox(boxa, item, lepttool.L_CLONE)
            box = lept_box.contents
            #print('Box[%d]: x=%d, y=%d, w=%d, h=%d, '%(item, box.x, box.y, box.w, box.h))
            rectList.append([box.x, box.y, box.w, box.h])
            
        return rectList  
    
    def setting(self,action,data = None):
        import os
        currentPath = os.path.split(os.path.realpath(__file__))[0]
        
        if action =='SAVE':
            with open(currentPath+'/setting.conf','w') as setting_file:
                json.dump(data, setting_file)
        
        elif action =='LOAD':
            try:
                with open(currentPath+'/setting.conf','r') as setting_file:
                    setting = json.load(setting_file)
                    return setting
            except Exception:
                print('No setting files')
                return
            
                
            
          
        
 
            
            
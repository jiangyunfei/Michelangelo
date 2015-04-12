#-*- encoding: utf-8 -*-
'''
Created on Apr 5, 2015
This is the file controller
@author: jiang
'''
from PIL import Image
import numpy
import json
from PyQt4 import QtGui
from libs import lepttool


class FileMgr:
    def __init__(self,parent = None):
        '''
        initialize
        '''
        self.leptonica = lepttool.get_leptonica()
        self.parent = parent
        self.image_dir = None
        
        self.file_dir = QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.PicturesLocation)
        
    def openFile(self,type):
        if type == 'image':
            """Load Image
            """
            image_dir = QtGui.QFileDialog.getOpenFileName(self.parent,'Open Image file',self.file_dir,
                        'Images (*.jpg *.jpeg *.bmp *.png *.tiff *.tif *.gif);;All files (*.*)')
            if image_dir:
                self.image_dir = image_dir
                return image_dir
            
        elif type == 'json':
            filePath = QtGui.QFileDialog.getOpenFileName(self.parent, 'Save file',self.file_dir,
                                                     'JSON (*.json);;All files (*.*)')
            if filePath:
                return filePath
                        
    def getImage(self,image_dir,type):
        

        self.loadIamge(image_dir)
        
        if type == 'PIX':
            return self.pix_image
        elif type == 'PIL':
            return self.PILimage
        elif type == 'ROI':
            return self.ROIimage
        else:
            print('Type Wrong!')
            return
    
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

    
    def saveFile(self,data,format):
        if data is None:
            return
        
        filePath = QtGui.QFileDialog.getSaveFileName(self.parent, 'Save file',self.file_dir,
                                                     'FILE (*.json,*.txt);;All files (*.*)')
        if filePath:
            outfile_dir = filePath+format
            outfile = open(outfile_dir, "w")
            if format =='.json':
                json.dump(data, outfile)
            elif format == '.txt':
                keys = sorted(data.keys())
                for key in keys:
                    if key == 'IMG':
                        continue
                    val = data[key]
                    text = val['text']
                    outfile.write('\n%s : \n%s\n'%(key,text.encode('utf-8')))

                
            else:
                print('FORMAT WRONG')
                
            outfile.close()        
            print('Saved to ' + outfile_dir)
            
        
    def boxa2rect(self,boxa):
        
        rectList = []
        # Get info about number of items on image
        n_items = self.leptonica.boxaGetCount(boxa)
        print('Find %s '%n_items)
        
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
        
 
            
            
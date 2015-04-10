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
        self.__isLoad = False
        self.parent = parent
        self.image_dir = None
        self.__isLoad = False
        
    def openFile(self,type):
        if type == 'image':
            """Load Image
            """
            
            #input_dir = sett.readSetting('images/input_dir')
            input_dir = QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.PicturesLocation)
            
            image_dir = QtGui.QFileDialog.getOpenFileName(self.parent,'Open Image file',input_dir,
                        'Images (*.jpg *.jpeg *.bmp *.png *.tiff *.tif *.gif);;All files (*.*)')
            if image_dir:
                self.image_dir = image_dir
                self.__isLoad = False
                return image_dir
            else:
                return
            
    def getImage(self,image_dir,type):
        
        if not self.__isLoad:
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
        
        output_dir = QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.DocumentsLocation)
        filePath = QtGui.QFileDialog.getSaveFileName(self.parent, 'Save file',output_dir,
                                                     'FILE (*.json,*.txt);')
        if filePath:
            outfile_dir = filePath+format
            outfile = open(outfile_dir, "w")
            if format =='.json':
                json.dump(data, outfile)
            elif format == '.txt':
                for key in data.keys():
                    val = data[key]
                    outfile.write('%s : %s'%(key,val['text']))
                    print('%s : %s' % (key,val['text']))
            else:
                print('FORMAT WRONG')
                
            outfile.close()        
            print('Saved to ' + outfile_dir)
        
    def boxa2rect(self,boxa):
        
        rectList = []
        # Get info about number of items on image
        n_items = self.leptonica.boxaGetCount(boxa)
        print('Find %s !'%n_items)
        
        # Set up result type (BOX structure) for leptonica function boxaGetBox
        self.leptonica.boxaGetBox.restype = lepttool.BOX_PTR_T
        self.leptonica.boxaGetBox.argtypes = []
        
        # Display items and print its info
        for item in range(0, n_items):
            lept_box = self.leptonica.boxaGetBox(boxa, item, lepttool.L_CLONE)
            box = lept_box.contents
            print('Box[%d]: x=%d, y=%d, w=%d, h=%d, '%(item, box.x, box.y, box.w, box.h))
            rectList.append([box.x, box.y, box.w, box.h])
            
        return rectList    
        
 
            
            
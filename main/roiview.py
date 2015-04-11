#-*- encoding: utf-8 -*-
'''
Created on Apr 5, 2015
This is the main view file
@author: jiang
'''

from PyQt4 import QtGui

import pyqtgraph as pg


class ROIView:
    def __init__(self):
        self.pgView = pg.GraphicsView()
        self.vb = pg.ViewBox()
        
        self.image = None
        self.lastIm = None
        self.__isIm = False
        
        self.initROIs()
    
    def initROIs(self):
        self.index=1 #TAG标签
        self.posDict = {}
        self.ROIs = {}

    
    def getROIView(self):
        
        self.pgView.setBackground(QtGui.QColor(127,127,127))      # Transparent background outside of the image
        self.pgView.setCentralWidget(self.vb)    # Autoscale the image when the window is rescaled
        return self.pgView
        
    
    def setIamge(self, image):
        if image is None:
            return
            
        im = pg.ImageItem()
        im.setImage(image)
        
        if self.__isIm:
            self.vb.removeItem(self.lastIm)
            self.clearROIs()
            
        self.vb.addItem(im)
        self.vb.setAspectLocked(True)    # No aspect distortions
        self.vb.autoRange()
        self.vb.invertY(b=True)
        
        self.lastIm = im
        self.image = image
        self.__isIm = True
    
    
    def setROIs(self,rlist):
        '''
        此处需要清空原始的ROI
        '''
        if self.__isIm:
            self.clearROIs()
        
        if rlist is None:
            return
        for r in rlist:
            self.addROI(r)
            
    
    def addROI(self,r):
        posx = r[0]
        posy = r[1]
        w= r[2]
        h=r[3]
        
        if self.index < 10:
            numStr = '0'+ str(self.index)
        else:
            numStr = str(self.index)
        
        tag = '#'+numStr

        roi = TagROI((posx, posy), (w,h),tag,pen=0, 
                         centered=False, 
                         sideScalers=True, 
                         removable=True)
        
        #set TAG Text Item
        textItem = QtGui.QGraphicsSimpleTextItem(tag,roi)
        
        s=textItem.boundingRect()
        textItem.setPos(posx,posy-s.height())
        tagBrush=QtGui.QBrush(QtGui.QColor(255,0,0))
        QtGui.QAbstractGraphicsShapeItem.setBrush(textItem,tagBrush)
        
        roi.setTextItem(textItem)
        
        #connection
        #roi.sigRegionChangeStarted.connect(self)
        roi.sigRegionChanged.connect(self.posChanged)
        #roi.sigHoverEvent.connect(self.showInfo)
        roi.sigRemoveRequested.connect(self.removeROI)
    
        self.vb.addItem(roi)
        self.vb.addItem(textItem)
        self.index+=1
        
        #ADD
        self.posDict[tag]=[posx,posy,w,h]
        self.ROIs[tag]=roi
    
        
    def clearROIs(self):
        for key in self.ROIs.keys():
            roi = self.ROIs[key]
            self.removeROI(roi)
        
        #reset           
        self.initROIs()
   
               
    def posChanged(self,roi):
        tag = roi.getTAG()
        posx,posy = roi.pos()
        w,h = roi.size()
        #print(tag +'-> position changed: ',pos,size)
        
        textItem = roi.getTextItemPointer()
        if textItem is None:
            print('get NULL!')
            return
        s=textItem.boundingRect()
        textItem.setPos(posx, posy-s.height())
        
        #Changed
        if self.posDict.has_key(tag):
            self.posDict[tag]=[posx,posy,w,h]
            
    
    
    def highlightROI(self,TAG):
        if TAG in self.ROIs.keys():
            item = self.ROIs[TAG]
        else:
            print('Not Found!')
            return
                
        self.vb.locate(item, timeout=2.0)
    
           
    def removeROI(self,roi):
        tag = roi.getTAG()
        textItem = roi.getTextItemPointer()
        self.vb.removeItem(roi)
        self.vb.removeItem(textItem)
        
        #Remove
        if self.posDict.pop(tag):
            self.ROIs.pop(tag)
            print(tag +'-> is removed! ')
        
        
       
    def getPosDict(self):
        if self.posDict is None:
            return

        return self.posDict 
        
        
        
class TagROI(pg.ROI):
    '''
     参考RectROI的结构，编写的ROI
    ============== =============================================================
    **Arguments**
    pos            (length-2 sequence) The position of the ROI origin.
                   See ROI().
    size           (length-2 sequence) The size of the ROI. See ROI().
    centered       (bool) If True, scale handles affect the ROI relative to its
                   center, rather than its origin.
    sideScalers    (bool) If True, extra scale handles are added at the top and 
                   right edges.
    \**args        All extra keyword arguments are passed to ROI()
    ============== =============================================================
    
    '''
    def __init__(self, pos, size, tag, centered=True, sideScalers=True, **args):
        pg.ROI.__init__(self, pos, size, **args)
        if centered:
            center = [0.5, 0.5]
        else:
            center = [0, 0]
            
        #self.addTranslateHandle(center)
        self.addScaleHandle([1, 1], center)
        if sideScalers:
            self.addScaleHandle([1, 0.5], [center[0], 0.5])
            self.addScaleHandle([0.5, 1], [0.5, center[1]])
            
        self.TAG = tag
        self.TextItem = None
    
    def getTAG(self):
        return self.TAG
    
    def getTextItemPointer(self):
        '''
        item: the pointer to the text item
        '''
        if self.TextItem is None:
            return
        
        return self.TextItem
    
    def setTextItem(self,item):
        self.TextItem = item





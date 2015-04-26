#-*- encoding: utf-8 -*-
'''
Created on Apr 15, 2015
parse the json file to handle the infomations:

Automatic detect the orientation:
    compare the w and h

@author: jiang
'''

from PyQt4 import QtGui,QtCore
import pyqtgraph as pg

class ParseMgr(QtGui.QDialog):
    def __init__(self,parent = None):
        QtGui.QDialog.__init__(self,parent)
        
        self.vb = pg.ViewBox()
        
        self.pgView = pg.GraphicsView()
        self.pgView.setBackground(QtGui.QColor(127,127,127))      # Transparent background outside of the image
        self.pgView.setCentralWidget(self.vb)    # Autoscale the image when the window is rescaled
        
        ly = QtGui.QVBoxLayout()
        ly.addWidget(self.pgView)
        self.setLayout(ly)
        
        self.resize(600, 500)
        self.setWindowTitle('Parse')
        self.image = None
     
        
    def setImage(self, image):
        self.image = image.copy()
                
        im = pg.ImageItem()
        im.setImage(self.image)
        self.vb.addItem(im)
        self.vb.setAspectLocked(True)    # No aspect distortions
        self.vb.autoRange()
        self.vb.invertY(b=True)
        
        

    def setBlocks(self, blockList, index):    
        '''
        clear first
        clear the pos area
        generate the index and boundingRect, add to viewbox
        '''
        length = len(blockList)
        if length == len(index):
            for i in range(length):
                pos = blockList[i]
                tag = index[i]

                self.addRectWithTag(pos, tag)                
                    
    def addRectWithTag(self,pos,tag):
        posx,posy,w,h = pos
        
        #Process the image
        self.image[posx:posx+w, posy:posy+h] = 255
        
        rectItem = QtGui.QGraphicsRectItem(posx,posy,w,h)
        textItem = QtGui.QGraphicsSimpleTextItem(tag,rectItem)
        
        s=textItem.boundingRect()
        textItem.setPos(posx,posy-s.height())
        tagBrush=QtGui.QBrush(QtCore.Qt.red)
        QtGui.QAbstractGraphicsShapeItem.setBrush(textItem,tagBrush)
        
        pen = QtGui.QPen(QtCore.Qt.red,1)
        rectItem.setPen(pen)

        self.vb.addItem(rectItem)
        self.vb.addItem(textItem)
    
    def processIMG(self,img,pos):
        pass
        
    def setText(self,text,pos):
        '''
        text: list [[...],[...],...]
        pos:lsit[[...],[...],...]
        generate the simpleTextItem, add it to viewBox
        '''     
        #drawText
        length = len(text)
        if length == len(pos):
            for i in range(length):
                tlist = text[i]
                plist = pos[i]
                
                #add the text in every block
                if len(tlist) == len(plist):
                    for j in range(len(tlist)):
                        self.addText(tlist[j], plist[j])
                
                
    def addText(self,text,pos):
        posx,posy,w,h = pos
        
        textItem = QtGui.QGraphicsTextItem(text.rstrip('\n')) #remove the '\n' in the end 
        
        font = QtGui.QFont()
        font.setPointSize(12)
        textItem.setFont(font) 
        
        textItem.setDefaultTextColor(QtCore.Qt.red)
        textItem.setTextWidth(w)
        textItem.setPos(posx,posy)
        textItem.adjustSize()
        
        self.vb.addItem(textItem)
        
    
        
    

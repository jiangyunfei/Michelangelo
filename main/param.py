#-*- encoding: utf-8 -*-
'''
Created on Apr 5, 2015
This is the Parameter file
@author: jiang
'''
from __future__ import print_function
from PyQt4 import QtCore
from pyqtgraph.parametertree import Parameter, ParameterTree


class Param(QtCore.QObject):
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.initParam()
        
        ## Create tree of Parameter objects
        self.parameter = Parameter.create(name='OCR Parameter', type='group', children=self.params)
        
        def turn2change(param, changes):
            self.changeParam(param, changes)
        
        self.parameter.sigTreeStateChanged.connect(turn2change)
        self.tree = ParameterTree(None, showHeader=False)
        self.tree.setParameters(self.parameter, showTop=True)
        
        #Lazy Mode:
        self.textList = None
        self.ocrIndex = None
        
        #DEBUG
        index=['#1','#2','#3']
        ocrText = ['text1','text2','text3']        
        #self.setResult(ocrText, index)
        
                
    
    def initParam(self):
        self.LANG = ['eng', 'chi_sim', 'chi_tra']
        LANGparam = {}
        for i in range(len(self.LANG)):
            LANGparam[self.LANG[i]]=i
        
        
        self.ORI = ["Horizontal", "Vertical"]
        ORIparam = {}
        for i in range(len(self.ORI)):
            ORIparam[self.ORI[i]]=i
        
        self.PSM = ['PSM_OSD_ONLY', 'PSM_AUTO_OSD', 'PSM_AUTO_ONLY', 'PSM_AUTO',
                    'PSM_SINGLE_COLUMN', 'PSM_SINGLE_BLOCK_VERT_TEXT', 'PSM_SINGLE_BLOCK',
                    'PSM_SINGLE_LINE', 'PSM_SINGLE_WORD', 'PSM_CIRCLE_WORD', 'PSM_SINGLE_CHAR',
                    'PSM_SPARSE_TEXT', 'PSM_SPARSE_TEXT_OSD']
        PSMparam = {}
        for i in range(len(self.PSM)):
            PSMparam[self.PSM[i]]=i
        
        
        self.RIL = ['RIL_BLOCK', 'RIL_PARA', 'RIL_TEXTLINE', 'RIL_WORD', 'RIL_SYMBOL']
        RILparam = {}
        for i in range(len(self.RIL)):
            RILparam[self.RIL[i]]=i
        
        
        self.params = [
        {'name': 'Options', 'type': 'group', 'children': [
            {'name': 'Language', 'type': 'list', 'values':LANGparam, 'value': 0},
            {'name': 'Orientation', 'type': 'list', 'values': ORIparam, 'value': 0},
            {'name': 'PSM', 'type': 'list', 'values': PSMparam, 'value': 3},
            {'name': 'RIL', 'type': 'list', 'values': RILparam, 'value': 0}
            ]}
        ]
        
        self.FORMAT = [".json", ".txt"]
        FORparam = {}        
        for i in range(len(self.FORMAT)):
            FORparam[self.FORMAT[i]]=i
            
        self.textParams = [{'name': 'Output', 'type': 'group','children': [
                                {'name': 'Format', 'type': 'list', 'values':FORparam , 'value': 0},
                                {'name': 'Save', 'type': 'action'}
                                ]}]
        
        self.textList = None
        self.ocrIndex = None
    
    
    def changeParam(self,param,changes):
        ## If anything changes in the tree, print a message
        for name, change, data in changes:
            path = self.parameter.childPath(name)
            if path == []:
                return
            
            if path is not None:
                (item,ops) = path
                if item == 'Text':
                    if ops in self.ocrIndex:
                        idx = self.ocrIndex.index(ops)
                        self.textList[idx]=data
                        #print('%s -> %s'%(self.textList[idx], data))
                        
                        self.emit(QtCore.SIGNAL('ROIHighlight'),ops)
                        print(ops+' -> Emit highlight signal')
                    else:
                        print('Nothing changed!')
                else:
                    if ops == 'TEST':
                        #TEST
                        print('TEST -> Nothing!')
                        pass
                        
                    if ops == 'Save':
                        self.emit(QtCore.SIGNAL('SaveClicked'))
                    print('%s changed!.'%ops)
                    
                
    def setResult(self,textList=[],ocrIndex= []):
        if textList is []:
            return
        
        #FORMAT : {'name': '#1', 'type': 'text', 'value': '#1 OCR text...'}
        ocrText = []
        for i in range(len(ocrIndex)):
            item = {'name': ocrIndex[i], 'type': 'text', 'value':textList[i]}
            ocrText.append(item)
        
        #添加信息：
        if self.textList:
            self.clearResult()
                
        self.textParams.append({'name': 'Text', 'type': 'group', 'children': ocrText})
         
        #增加结果
        self.parameter.addChildren(children=self.textParams)
        
        self.textList = textList
        self.ocrIndex = ocrIndex
    
    def clearResult(self):
        if self.textList:
            children = self.parameter.children()
            for c in children:
                if c.name() == 'Options':
                    continue
                c.remove()
            
            #初始化    
            self.textParams.pop()
            self.ocrIndex = None
            self.textList = None   
    
    def getParamTree(self):
        return self.tree
    
    def getParamOptions(self):
        Opstions = {}
        ops = self.parameter.child('Options')
        children = ops.children()
        for ptr in children:
            Opstions[ptr.name()] = ptr.value()
            
        #Transfer
        Opstions['Language']=self.LANG[Opstions['Language']]
        return Opstions
        
    def getFormat(self):
        
        ops = self.parameter.child('Output')
        format = ops.child('Format')
        return self.FORMAT[format.value()]
    
    def getOutputText(self):
        return self.textList
        
        

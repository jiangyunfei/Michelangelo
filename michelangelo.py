'''
https://github.com/jiangyunfei/Michelangelo

@author: jiang
'''

import sys
from PyQt4 import QtGui
from main.maingui import Michelangelo

 
app = QtGui.QApplication(sys.argv)
cat = Michelangelo()
cat.show()
sys.exit(app.exec_())
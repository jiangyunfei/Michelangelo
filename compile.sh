#!/bin/sh

pyuic4 ui/MainWindow.ui > ui/ui_mainwindow.py
pyrcc4 ui/resources.qrc -o ui/resources_rc.py

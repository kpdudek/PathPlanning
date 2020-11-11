#!/usr/bin/env python3

from PyQt5.QtWidgets import * 
from PyQt5 import QtCore, QtGui, QtSvg, uic
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
import random, sys, os, math, time

from lib.Utils import *
from lib.PaintUtils import *
from lib.Game import *

def main():
    file_paths = FilePaths()
    assert(file_paths.cc_lib_path in os.listdir('./lib/')),"cc_lib.so doesn't exist! Be sure to compile collision_check.c as cc_lib.so!"

    QApplication.setStyle("fusion")

    app = QApplication(sys.argv)
    log('Game started...',color='g')

    # Now use a palette to switch to dark colors
    palette = DarkColors().palette
    app.setPalette(palette)
    
    # create the instance of our Window 
    fps = 60.
    game_window = Game(app.primaryScreen(),fps) 

    # start the app 
    sys.exit(app.exec()) 

if __name__ == '__main__':
    try:
        main()
    finally:
        log('Game ended...',color='g')
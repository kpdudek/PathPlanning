#!/usr/bin/env python3

import os
import sys
import time
import datetime as dt
from threading import Thread
import inspect

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class ElementColors():
    ###################################################
    # Game Colors
    ###################################################
    brown = {'hex':'#996633','rgb':[153,102,51]}
    sky_blue = {'hex':'#1BADDE','rgb':[27,173,222]}
    midnight_blue = {'hex':'#051962','rgb':[5,25,98]}
    star_gold = {'hex':'#F7D31E','rgb':[247, 211, 30]}
    white = {'hex':'#FFFFFF','rgb':[255,255,255]}
    forest_green = {'hex':'#38690E','rgb':[56,105,14]}

    ###################################################
    # Welcome Screen Colors
    ###################################################
    title_blue = '#000080'
    title_white = '#FFFFFF'
    divider_color = '#ff9955'
    background_color = '#353535'
    warning_text = '#FB0101'

class DarkColors(ElementColors):
    
    def __init__(self):
        super().__init__()
        self.palette = QPalette()
        self.palette.setColor(QPalette.Window, QColor(self.background_color))
        self.palette.setColor(QPalette.WindowText, Qt.white)
        self.palette.setColor(QPalette.Base, QColor(25, 25, 25))
        self.palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        self.palette.setColor(QPalette.ToolTipBase, Qt.white)
        self.palette.setColor(QPalette.ToolTipText, Qt.white)
        self.palette.setColor(QPalette.Text, Qt.white)
        self.palette.setColor(QPalette.Button, QColor(53, 53, 53))
        self.palette.setColor(QPalette.ButtonText, QColor(255, 153, 85)) #Qt.white
        self.palette.setColor(QPalette.BrightText, Qt.red)
        self.palette.setColor(QPalette.Link, QColor(255, 153, 85))
        self.palette.setColor(QPalette.Highlight, QColor(255, 153, 85))
        self.palette.setColor(QPalette.HighlightedText, Qt.black)

class Colors(ElementColors):

    def __init__(self):
        super().__init__()
        self.palette = QPalette()
        self.palette.setColor(QPalette.Window, QColor(self.background_color))
        self.palette.setColor(QPalette.WindowText, Qt.white)
        self.palette.setColor(QPalette.Base, QColor(25, 25, 25))
        self.palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        self.palette.setColor(QPalette.ToolTipBase, Qt.white)
        self.palette.setColor(QPalette.ToolTipText, Qt.white)
        self.palette.setColor(QPalette.Text, Qt.white)
        self.palette.setColor(QPalette.Button, QColor(53, 53, 53))
        self.palette.setColor(QPalette.ButtonText, QColor(255, 153, 85)) #Qt.white
        self.palette.setColor(QPalette.BrightText, Qt.red)
        self.palette.setColor(QPalette.Link, QColor(255, 153, 85))
        self.palette.setColor(QPalette.Highlight, QColor(255, 153, 85))
        self.palette.setColor(QPalette.HighlightedText, Qt.black)

class FusionColor(ElementColors):

    def __init__(self):
        super().__init__()
        self.palette = QPalette()
        self.palette.setColor(QPalette.Window, QColor(53,53,53))
        self.palette.setColor(QPalette.WindowText, Qt.white)
        self.palette.setColor(QPalette.Base, QColor(15,15,15))
        self.palette.setColor(QPalette.AlternateBase, QColor(53,53,53))
        self.palette.setColor(QPalette.ToolTipBase, Qt.white)
        self.palette.setColor(QPalette.ToolTipText, Qt.white)
        self.palette.setColor(QPalette.Text, Qt.white)
        self.palette.setColor(QPalette.Button, QColor(53,53,53))
        self.palette.setColor(QPalette.ButtonText, Qt.white)
        self.palette.setColor(QPalette.BrightText, Qt.red)
            
        self.palette.setColor(QPalette.Highlight, QColor(142,45,197).lighter())
        self.palette.setColor(QPalette.HighlightedText, Qt.black)

class PaintBrushes():
    def __init__(self):
        pass    
    def hollow_poly(self,color,width):
        pen = QPen()
        pen.setWidth(width)
        pen.setColor(QColor(color))

        brush = QBrush()
        brush.setColor(QColor(self.brown['hex']))
        brush.setStyle(Qt.NoBrush)

        return pen,brush
    
    def solid_poly(self,color,width):
        pen = QPen()
        pen.setWidth(width)
        pen.setColor(QColor(color))

        brush = QBrush()
        brush.setColor(QColor(color))
        brush.setStyle(Qt.SolidPattern)

        return pen,brush

    def transparent_poly(self,color,width):
        pen = QPen()
        pen.setWidth(width)
        pen.setColor(QColor(color))

        brush = QBrush()
        brush.setColor(QColor(color))
        brush.setStyle(Qt.DiagCrossPattern)

        return pen,brush

    def connection_line(self):
        pen = QPen()
        pen.setWidth(1)
        pen.setColor(QColor(self.star_gold['hex']))

        brush = QBrush()
        brush.setColor(QColor(self.star_gold['hex']))
        brush.setStyle(Qt.SolidPattern)

        return pen,brush

    def path_line(self):
        pen = QPen()
        pen.setWidth(2)
        pen.setColor(QColor(self.title_blue))

        brush = QBrush()
        brush.setColor(QColor(self.title_blue))
        brush.setStyle(Qt.SolidPattern)

        return pen,brush

    def swept_volume(self):
        pen = QPen()
        pen.setWidth(2)
        pen.setColor(QColor(self.divider_color))

        brush = QBrush()
        brush.setColor(QColor(self.divider_color))
        brush.setStyle(Qt.Dense6Pattern)

        return pen,brush
    
    def free_space(self):
        pen = QPen()
        pen.setWidth(1)
        pen.setColor(Qt.black)
        pen.setStyle(Qt.DotLine)

        brush = QBrush()
        brush.setColor(Qt.white)
        brush.setStyle(Qt.SolidPattern)

        return pen,brush
    
    def text_color(self):
        pen = QPen()
        pen.setWidth(1)
        pen.setColor(Qt.black)

        brush = QBrush()
        brush.setColor(Qt.black)
        brush.setStyle(Qt.SolidPattern)

        return pen,brush
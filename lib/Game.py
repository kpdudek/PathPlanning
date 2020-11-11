#!/usr/bin/env python3

from PyQt5.QtWidgets import * 
from PyQt5 import QtCore, QtGui, QtSvg, uic
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
import random, sys, os, math, time
import numpy as np

from lib.Utils import *
from lib.PaintUtils import *
import lib.RoadmapBuilder as rb 

class Canvas(QLabel):
    tile_click = pyqtSignal(int,int)
    
    def __init__(self,grid_size):
        super().__init__()
        self.mouse_pose = None
        self.selected_item = None
        self.grid_size = grid_size

    def mousePressEvent(self,e):
        print(f'Canvas clicked: x:{e.x()} y:{e.y()}')
        self.mouse_pose = np.array([[e.x()],[e.y()]])

        y_offset = (self.geometry().height()-self.geometry().width())/2

        r = math.floor(e.x()/(self.geometry().width()/self.grid_size))
        c = math.floor((e.y()-y_offset)/(self.geometry().width()/self.grid_size))
        print(f"{r} {c}")
        self.tile_click.emit(r,c)

class Game(QMainWindow,FilePaths,ElementColors,PaintBrushes):

    def __init__(self,screen,fps=60.0):
        super().__init__()
        
        uic.loadUi(f'{self.user_path}ui/main_window.ui',self)
        self.setFocusPolicy(Qt.StrongFocus)
        
        self.screen_height = screen.size().height()
        self.screen_width = screen.size().width()

        self.width = self.screen_width * (2./3.)
        self.height = self.screen_height* (2./3.)
        self.setGeometry(math.floor((self.screen_width-self.width)/2), math.floor((self.screen_height-self.height)/2), self.width, self.height) 

        self.grid_size = self.grid_size_spinbox.value()
        self.grid_size_spinbox.valueChanged.connect(self.redraw_graph)

        self.canvas_label = Canvas(self.grid_size)
        self.verticalLayout_6.addWidget(self.canvas_label)
        self.canvas = QPixmap(self.width/2.,self.height)
        self.canvas_label.setPixmap(self.canvas)
        self.canvas_label.tile_click.connect(self.tile_click_action)

        self.roadmap = rb.RoadmapBuilder()
        self.roadmap.construct_square(self.grid_size)
        self.roadmap.set_obstacles(self.grid_size)
        self.roadmap.init_roadmap()
        self.roadmap.set_neighbors()
    
        # Show main window
        self.show()
    
    def get_paint_type(self):
        for widget in self.paint_tool_frame.children():
            if isinstance(widget, QRadioButton):
                if widget.isChecked():
                    if widget.text() == 'Start':
                        self.draw_color = self.forest_green['hex']
                    elif widget.text() == 'Goal':
                        self.draw_color = self.warning_text
                    elif widget.text() == 'Obstacle':
                        self.draw_color = self.sky_blue['hex']
                    elif widget.text() == 'Free':
                        self.draw_color = self.white['hex']

    def tile_click_action(self,r,c):
        print(f'{r} {c}')
        self.painter = QtGui.QPainter(self.canvas_label.pixmap())
        
        self.get_paint_type()
        pen,brush = self.solid_poly(self.draw_color,1)
        self.painter.setPen(pen)
        self.painter.setBrush(brush)

        size = self.canvas_label.geometry().width()/self.grid_size
        rec = QRect(r*size,c*size,size,size)
        self.painter.drawRect(rec)

        self.painter.end()

        self.canvas_label.update()

    def resizeEvent(self, event):
        self.height = float(event.size().height())
        self.width = float(event.size().width())
        self.update_canvas()

    def redraw_graph(self):
        self.grid_size = self.grid_size_spinbox.value()

        self.roadmap = rb.RoadmapBuilder()
        self.roadmap.construct_square(self.grid_size)
        self.roadmap.set_obstacles(self.grid_size)
        self.roadmap.init_roadmap()
        self.roadmap.set_neighbors()

        self.update_canvas()

    def draw_grid(self):
        # draw the checkerboard based on numpy arrays
        pen,brush = self.solid_poly(self.sky_blue['hex'],1)

        size = self.canvas_label.geometry().width()/self.grid_size

        self.painter.setPen(pen)
        self.painter.setBrush(brush)

        r,c = self.roadmap.graph.shape

        r = int(r)
        c = int(c)

        for i in range(0,r):
            for j in range(0,c):
                # print(self.roadmap.graph[i,j].occupied)
                # print(f'{i} {j}')
                if self.roadmap.graph[i,j].occupied:
                    rec = QRect(i*size,j*size,size,size)
                    self.painter.drawRect(rec)
        print(f"Roadmap length: {len(self.roadmap.roadmap)}")

    def update_canvas(self):
        self.canvas = QPixmap(self.canvas_label.geometry().width(),self.canvas_label.geometry().width())
        self.canvas_label.setPixmap(self.canvas)
        
        self.painter = QtGui.QPainter(self.canvas_label.pixmap())
        rec = QRect(0,0,self.canvas_label.geometry().width(),self.canvas_label.geometry().width())
            
        pen,brush = self.solid_poly(self.white['hex'],1)
        self.painter.setPen(pen)
        self.painter.setBrush(brush)
        self.painter.drawRect(rec)

        self.draw_grid()

        self.painter.end()
            
    def game_loop(self):
        curr_time = time.time()

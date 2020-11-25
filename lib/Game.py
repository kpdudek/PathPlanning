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
from lib.AStar import *
from lib.PriorityQueue import *

class Canvas(QLabel):
    tile_click = pyqtSignal(int,int)
    tile_drag = pyqtSignal(int,int)
    tile_release = pyqtSignal(int,int)
    
    def __init__(self,grid_size):
        super().__init__()
        self.mouse_pose = None
        self.selected_item = None
        self.grid_size = grid_size
        self.square_size = None

    def mousePressEvent(self,e):
        log(f'Canvas clicked: x:{e.x()} y:{e.y()}')
        log(f'\tGrid size: {self.grid_size}')
        self.mouse_pose = np.array([[e.x()],[e.y()]])
        y_offset = (self.geometry().height()-self.square_size)/2.
        r = int(e.x()/(self.square_size/self.grid_size))
        c = int((e.y()-y_offset)/(self.square_size/self.grid_size))
        if (r >= self.grid_size) or (c >= self.grid_size) or (r < 0) or (c < 0):
            return
        log(f'\tTile clicked: {r} {c}')
        self.tile_click.emit(r,c)

    def mouseMoveEvent(self,e):
        self.mouse_pose = np.array([[e.x()],[e.y()]])
        y_offset = (self.geometry().height()-self.square_size)/2.
        r = int(e.x()/(self.square_size/self.grid_size))
        c = int((e.y()-y_offset)/(self.square_size/self.grid_size))
        if (r >= self.grid_size) or (c >= self.grid_size) or (r < 0) or (c < 0):
            return
        self.tile_drag.emit(r,c)

    def mouseReleaseEvent(self,e):
        log(f'Canvas released: x:{e.x()} y:{e.y()}')
        self.mouse_pose = np.array([[e.x()],[e.y()]])
        y_offset = (self.geometry().height()-self.square_size)/2.
        r = int(e.x()/(self.square_size/self.grid_size))
        c = int((e.y()-y_offset)/(self.square_size/self.grid_size))
        if (r >= self.grid_size) or (c >= self.grid_size) or (r < 0) or (c < 0):
            return
        log(f'\tTile Released: {r} {c}')
        self.tile_release.emit(r,c)

class Game(QMainWindow,FilePaths,ElementColors,PaintBrushes):

    def __init__(self,screen,fps=60.0):
        super().__init__()
        
        uic.loadUi(f'{self.user_path}ui/main_window.ui',self)
        self.setFocusPolicy(Qt.StrongFocus)
        
        self.screen_height = screen.size().height()
        self.screen_width = screen.size().width()

        self.width = self.screen_width * (7./8.)
        self.height = self.screen_height* (7./8.)
        self.setGeometry(math.floor((self.screen_width-self.width)/2), math.floor((self.screen_height-self.height)/2), self.width, self.height) 

        self.grid_size = self.grid_size_spinbox.value()

        self.generate_graph_button.clicked.connect(self.redraw_graph)
        self.generate_roadmap_button.clicked.connect(self.generate_roadmap)
        self.find_path_button.clicked.connect(self.find_path)
        self.perlin_noise_checkbox.stateChanged.connect(self.toggle_perlin_options)
        self.toggle_perlin_options()
        self.draw_checkbox.stateChanged.connect(self.toggle_paint_tool_frame)
        self.toggle_paint_tool_frame()

        self.debug_mode_checkbox.stateChanged.connect(self.toggle_debug_mode)
        self.toggle_debug_mode()

        self.canvas_label = Canvas(self.grid_size)
        self.verticalLayout_6.addWidget(self.canvas_label)
        # self.verticalLayout_6.setAlignment(Qt.AlignHCenter)
        self.canvas = QPixmap(self.width/2.,self.height)
        self.canvas_label.setPixmap(self.canvas)
        self.canvas_label.tile_click.connect(self.tile_click_action)
        self.canvas_label.tile_drag.connect(self.tile_drag_action)
        self.canvas_label.tile_release.connect(self.tile_release_action)

        self.redraw_graph()
        self.path = None
        self.astar = AStar(self.roadmap,self.debug_mode)

        # Show main window
        self.show()
        self.update()

        self.prev_tile = np.zeros([2,1])-1
        self.update_canvas()

    def toggle_perlin_options(self):
        log(f'Toggling perlin noise options: {self.perlin_noise_checkbox.isChecked()}')
        if self.perlin_noise_checkbox.isChecked():
            self.perlin_options_frame.show()
        else:
            self.perlin_options_frame.hide()
    
    def toggle_debug_mode(self):
        log(f'Toggling debug mode: {self.debug_mode_checkbox.isChecked()}')
        self.debug_mode = self.debug_mode_checkbox.isChecked()
        try:
            self.astar.debug_mode = self.debug_mode
        except:
            pass
    
    def toggle_paint_tool_frame(self):
        log(f'Toggling paint tool frame: {self.draw_checkbox.isChecked()}')
        if self.draw_checkbox.isChecked():
            self.paint_tool_frame.show()
        else:
            self.paint_tool_frame.hide()
    
    def get_paint_type(self):
        for widget in self.paint_tool_frame.children():
            if isinstance(widget, QRadioButton):
                if widget.isChecked():
                    self.draw_action = widget.text()
                    if widget.text() == 'Start':
                        self.draw_color = self.forest_green['hex']
                    elif widget.text() == 'Goal':
                        self.draw_color = self.warning_text
                    elif widget.text() == 'Obstacle':
                        self.draw_color = self.sky_blue['hex']
                    elif widget.text() == 'Free':
                        self.draw_color = self.white['hex']

    def tile_click_action(self,r,c):
        # If drawing is enabled
        if self.draw_checkbox.isChecked():
            self.painter = QtGui.QPainter(self.canvas_label.pixmap())
            self.get_paint_type()
            pen,brush = self.transparent_poly(self.draw_color,2)
            self.painter.setPen(pen)
            self.painter.setBrush(brush)
            size = self.square_size/self.grid_size
            rec = QRect(r*size,c*size,size,size)
            self.painter.drawRect(rec)
            log(f'\tDraw action: {self.draw_action}')
            if self.draw_action == 'Obstacle':
                self.roadmap.occupancy_graph[r,c] = 1
                self.roadmap.graph[r,c].occupied = True
            elif self.draw_action == 'Free':
                self.roadmap.occupancy_graph[r,c] = 0
                self.roadmap.graph[r,c].occupied = False
            elif self.draw_action == 'Start':
                self.roadmap.graph[r,c].start = True
                if np.sum(self.roadmap.start_idx)>=0:
                    prev_r = int(self.roadmap.start_idx[0])
                    prev_c = int(self.roadmap.start_idx[1])
                    self.roadmap.graph[prev_r,prev_c].start = False
                self.roadmap.start_idx = np.array([[r],[c]])
            elif self.draw_action == 'Goal':
                self.roadmap.graph[r,c].goal = True
                if np.sum(self.roadmap.goal_idx)>=0:
                    prev_r = int(self.roadmap.goal_idx[0])
                    prev_c = int(self.roadmap.goal_idx[1])
                    self.roadmap.graph[prev_r,prev_c].goal = False
                self.roadmap.goal_idx = np.array([[r],[c]])
            self.painter.end()

        log(f'\tNode type: {self.roadmap.graph[r,c].node_type()}')
        try:
            idx = self.roadmap.graph[r,c].idx
            neigh = self.roadmap.roadmap[idx].neighbors
            log(f'\tNeighbors: {neigh}')
            log(f'\tNeighbors cost: {self.roadmap.roadmap[idx].neighbors_cost}')
            log(f'\tBackpointer: {self.roadmap.roadmap[idx].backpointer}')
            log(f'\tBackpointer cost: {self.roadmap.roadmap[idx].backpointer_cost}')
        except:
            pass

        self.prev_tile = np.array([[r],[c]])
        self.canvas_label.update()

    def tile_drag_action(self,r,c):
        tile = np.array([[r],[c]])
        if np.all(self.prev_tile==tile):
            self.prev_tile = tile
            return
        
        log(f'Canvas dragged to tile: ({r},{c})')
        # If drawing is enabled
        self.get_paint_type()
        if self.draw_checkbox.isChecked():
            if self.draw_action == 'Obstacle':
                self.roadmap.occupancy_graph[r,c] = 1
                self.roadmap.graph[r,c].occupied = True
            elif self.draw_action == 'Free':
                self.roadmap.occupancy_graph[r,c] = 0
                self.roadmap.graph[r,c].occupied = False
            else:
                self.prev_tile = tile
                return
            self.painter = QtGui.QPainter(self.canvas_label.pixmap())
            pen,brush = self.transparent_poly(self.draw_color,2)
            self.painter.setPen(pen)
            self.painter.setBrush(brush)
            size = self.square_size/self.grid_size
            rec = QRect(r*size,c*size,size,size)
            self.painter.drawRect(rec)
            log(f'\tDraw action: {self.draw_action}')

            self.painter.end()

        self.prev_tile = tile
        self.canvas_label.update()

    def tile_release_action(self,r,c):
        pass

    def resizeEvent(self, event):
        self.height = float(event.size().height())
        self.width = float(event.size().width())
        self.update_canvas()

    def find_path(self):
        if np.sum(self.roadmap.start_idx)<0:
            log(f'Assign a start node!')
            return
        if np.sum(self.roadmap.goal_idx)<0:
            log(f'Assign a goal node!')
            return
        
        try:
            log(f'Beginning graph search...')
            self.astar.reset(self.roadmap)

            si,sj = self.roadmap.start_idx
            gi,gj = self.roadmap.goal_idx
            start_idx = self.roadmap.graph[int(si),int(sj)].idx
            goal_idx = self.roadmap.graph[int(gi),int(gj)].idx
            self.path = self.astar.get_plan(start_idx,goal_idx)
            self.draw_path()
        except Exception as e:
            log(f"Unable to find path. Likely one doesn't exist!")
            log(f'Find path call failed due to exception: {e}')

    def generate_roadmap(self):
        self.diag_val = self.allow_diagonals_checkbox.isChecked()
        log(f'Finding neighbors...')
        self.roadmap.init_roadmap()
        self.roadmap.set_neighbors(diagonals=self.diag_val)
        log(f'Done finding neighbors...')
        self.update_canvas()

    def redraw_graph(self):
        self.grid_size = self.grid_size_spinbox.value()
        self.canvas_label.grid_size = self.grid_size

        self.roadmap = rb.RoadmapBuilder()
        self.roadmap.construct_square(self.grid_size)

        if self.perlin_noise_checkbox.isChecked():
            self.passes = self.passes_spinbox.value()
            self.cutoff = self.cutoff_spinbox.value()
            self.roadmap.set_obstacles(self.grid_size,passes=self.passes,cutoff=self.cutoff)
        else:
            self.roadmap.clear_obstacles()

        self.roadmap.init_roadmap()
        self.update_canvas()

    def draw_grid(self):
        # draw the checkerboard based on numpy arrays
        size = self.square_size/self.grid_size
        r,c = self.roadmap.graph.shape
        r = int(r); c = int(c)

        pen,brush = self.text_color()
        self.painter.setPen(pen)
        self.painter.setBrush(brush)
        for i in range(0,r):
            for j in range(0,c):
                if self.roadmap.graph[i,j].occupied:
                    pen,brush = self.solid_poly(self.sky_blue['hex'],1)
                    self.painter.setPen(pen)
                    self.painter.setBrush(brush)
                    rec = QRect(i*size,j*size,size,size)
                    self.painter.drawRect(rec)
                elif self.roadmap.graph[i,j].goal:
                    pen,brush = self.solid_poly(self.warning_text,1)
                    self.painter.setPen(pen)
                    self.painter.setBrush(brush)
                    rec = QRect(i*size,j*size,size,size)
                    self.painter.drawRect(rec)
                elif self.roadmap.graph[i,j].start:
                    pen,brush = self.solid_poly(self.forest_green['hex'],1)
                    self.painter.setPen(pen)
                    self.painter.setBrush(brush)
                    rec = QRect(i*size,j*size,size,size)
                    self.painter.drawRect(rec)
                else:
                    pen,brush = self.free_space()
                    self.painter.setPen(pen)
                    self.painter.setBrush(brush)
                    rec = QRect(i*size,j*size,size,size)
                    self.painter.drawRect(rec)

        log(f"Roadmap length: {len(self.roadmap.roadmap)}")

    def draw_path(self):
        if len(self.path[0,:]) > 0:
            path = self.path
            self.painter = QtGui.QPainter(self.canvas_label.pixmap())
            
            size = self.square_size/self.grid_size
            for col_idx in range(0,len(path[0,:])):
                x,y = path[:,col_idx]
                x = int(x); y = int(y)
                rec = QRect(x*size,y*size,size,size)
                pen,brush = self.swept_volume()
                self.painter.setPen(pen)
                self.painter.setBrush(brush)
                self.painter.drawRect(rec)

                if (col_idx < len(path[0,:])-1):
                    x = x*size + (size/2.); y = y*size + (size/2.)
                    x2,y2 = path[:,col_idx+1]
                    x2 = int(x2)*size + (size/2); y2 = int(y2)*size + (size/2)
                    pen,brush = self.path_line()
                    self.painter.setPen(pen)
                    self.painter.setBrush(brush)
                    self.painter.drawLine(x,y,x2,y2)
            self.painter.end()
        self.update()

    def draw_connections(self):
        if len(self.roadmap.roadmap) > 0:
            size = self.square_size/self.grid_size
            for node in self.roadmap.roadmap:
                x,y = node.coord
                tx = int(x)*size + size/3.
                ty = int(y)*size + size/2.
                x = int(x)*size + (size/2.); y = int(y)*size + (size/2.)
                if self.debug_mode:
                    pen,brush = self.text_color()
                    self.painter.setPen(pen)
                    self.painter.setBrush(brush)
                    self.painter.drawText(tx,ty,f'{node.idx}')
                for neighbor_idx in node.neighbors:
                    x2,y2 = self.roadmap.roadmap[neighbor_idx].coord
                    x2 = int(x2)*size + (size/2); y2 = int(y2)*size + (size/2)
                    pen,brush = self.connection_line()
                    self.painter.setPen(pen)
                    self.painter.setBrush(brush)
                    self.painter.drawLine(x,y,x2,y2)

    def update_canvas(self):
        self.square_size = min([self.canvas_label.geometry().width(),self.canvas_label.geometry().height()])
        self.canvas_label.square_size = self.square_size

        self.canvas = QPixmap(self.square_size,self.square_size)
        self.canvas_label.setPixmap(self.canvas)
        
        self.painter = QtGui.QPainter(self.canvas_label.pixmap())
        rec = QRect(0,0,self.square_size,self.square_size)
            
        pen,brush = self.solid_poly(self.white['hex'],1)
        self.painter.setPen(pen)
        self.painter.setBrush(brush)
        self.painter.drawRect(rec)

        self.draw_grid()
        self.draw_connections()

        self.painter.end()
            
    def game_loop(self):
        curr_time = time.time()

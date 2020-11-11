#!/usr/bin/env python3
from PyQt5.QtWidgets import * 
from PyQt5 import QtCore, QtGui, QtSvg, uic
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
import random, sys, os, math, time, numpy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib import patches
from multiprocessing import Pool

path = os.getcwd()
sys.path.insert(1,os.path.dirname(path))

from Utils import *
from Geometry import *
from Player import *

class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        # self.axes = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.count = 331

    def plot(self,vertices,points):
        ax = self.figure.add_subplot(self.count)
        vertices = reshape_for_patch(vertices)
        patch = patches.Polygon(vertices, facecolor='b', fill='b')
        ax.add_patch(patch)
        try: 
            ax.plot(points[0,:],points[1,:],f'ro', markersize=3)
        except:
            pass # No point array passed
        ax.set_aspect('equal', adjustable='box')
        ax.grid(color='k', linestyle='-', linewidth=.5)
        self.count+=1
        self.draw()

class CollisionThreadTest(QMainWindow):

    def __init__(self):
        super().__init__()
        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)

        self.plot_canvas = PlotCanvas(parent=self.widget)
        self.layout.addWidget(self.plot_canvas)

        self.move(800,400)

        self.close_button = QPushButton('Close')
        self.close_button.clicked.connect(self.close_window)
        self.layout.addWidget(self.close_button)

        self.setCentralWidget(self.widget)

        self.run_test()

        self.show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close_window()
        return

    def close_window(self):
        self.close()

    def run_test(self):
        player = Player()
        player.pose[0] = 0.
        player.pose[1] = 0.
        player.set_geometry(player.geom)
        vertices_transformed = transform('img',player.vertices.copy(),translate=0.)

        num_players = 1.
        num_obstacles = 2.
        fps_multiplier = 1./((4*num_players)+(2*num_obstacles))

        log(f'FPS simulated for {num_players} Players and {num_obstacles} Obstacles')


        print()
        log('Without MultiProcessing...')
        '''
        n sided polygon collision check
        '''
        n = 6
        poly_type = f'{n} sided'

        poly = Polygon()
        poly.unit_circle(n,50)

        obstacle = np.fliplr(transform('img',poly.vertices.copy(),translate=0.))

        tic = time.time()
        res_1 = polygon_is_collision(obstacle,vertices_transformed)
        res_2 = polygon_is_collision(vertices_transformed,obstacle)
        toc = time.time()

        log(f'{poly_type} collision checking took (s): {toc-tic}')
        log(f'{poly_type} results: {res_1.any()} {res_2.any()}')
        log(f'FPS: {(1./(toc-tic))*fps_multiplier}')
        self.plot_canvas.plot(obstacle,vertices_transformed)

        print()
        log('With MultiProcessing...')
        '''
        n sided polygon collision check
        '''
        n = 6
        poly_type = f'{n} sided'

        poly = Polygon()
        poly.unit_circle(n,50)

        obstacle = np.fliplr(transform('img',poly.vertices.copy(),translate=0.))
        pool = Pool(5)

        tic = time.time()
        res_1 = multithreaded_polygon_is_collision(pool,obstacle,vertices_transformed)
        res_2 = multithreaded_polygon_is_collision(pool,vertices_transformed,obstacle)
        toc = time.time()

        log(f'{poly_type} collision checking took (s): {toc-tic}')
        log(f'{poly_type} results: {res_1.any()} {res_2.any()}')
        log(f'FPS: {(1./(toc-tic))*fps_multiplier}')
        self.plot_canvas.plot(obstacle,vertices_transformed)



def main():
    app = QApplication(sys.argv)
    window = CollisionThreadTest() 
    # start the app 
    sys.exit(app.exec()) 

if __name__ == '__main__':
    try:
        main()
    finally:
        pass
#!/usr/bin/env python3

import random, sys, os, math, time
from matplotlib import pyplot as plt
from matplotlib import patches
import numpy as np

import ctypes

path = os.getcwd()
sys.path.insert(1,os.path.dirname(path))

from Geometry import *
from Utils import *


class CollisionCheckTest(FilePaths):

    def __init__(self):
        super().__init__()

        self.poly1 = Polygon()
        self.poly1.unit_circle(4,39.37)
        self.poly1.translate(-7.,823.)

        self.poly2 = Polygon()
        self.poly2.unit_circle(4,950.32)
        self.poly1.translate(0,875)

        self.c_float_p = ctypes.POINTER(ctypes.c_double)
        self.fun = ctypes.CDLL(f'{os.path.dirname(path)}/cc_lib.so')   
                    
        self.fun.polygon_is_collision.argtypes = [self.c_float_p,ctypes.c_int,ctypes.c_int,self.c_float_p,ctypes.c_int,ctypes.c_int]
        self.fun.sphere_is_collision.argtypes = [self.c_float_p,ctypes.c_double,self.c_float_p,ctypes.c_double] 
    
    def run_test(self):
        #####################################################################
        # Polygon Collision Checking in C
        #####################################################################
        print('\nPolygon Collision Checking in C')
        tic = time.time()

        data = self.poly1.vertices.copy()
        data = data.astype(np.double)
        data_p = data.ctypes.data_as(self.c_float_p)

        data2 = self.poly2.vertices.copy() 
        data2 = data2.astype(np.double)
        data_p2 = data2.ctypes.data_as(self.c_float_p)


        returnVale = self.fun.polygon_is_collision(data_p,2,4,data_p2,2,4)
        toc = time.time()    
        print(f'C function took: {toc-tic}')
        print(f'Collision result: {returnVale}')

        #####################################################################
        # Polygon Collision Checking in Python
        #####################################################################
        print('\nPolygon Collision Checking in Python')

        tic = time.time()
        res = polygon_is_collision(self.poly1,self.poly2)
        toc = time.time()

        print(f'Python function took: {toc-tic}')
        print(f'Collision result: {res}')

        #####################################################################
        # Sphere Collision Checking in C
        #####################################################################
        print('\nSphere Collision Checking in C')
        tic = time.time()

        data_p = self.poly1.sphere.pose.ctypes.data_as(self.c_float_p)
        data_p2 = self.poly2.sphere.pose.ctypes.data_as(self.c_float_p)
        res = self.fun.sphere_is_collision(data_p,self.poly1.sphere.radius,data_p2,self.poly1.sphere.radius)

        toc = time.time()

        print(f'Python function took: {toc-tic}')
        print(f'Collision result: {res}')

        #####################################################################
        # Sphere Collision Checking in Python
        #####################################################################
        print('\nSphere Collision Checking in Python')

        tic = time.time()
        res = sphere_is_collision(self.poly1,self.poly2)
        toc = time.time()

        print(f'Python function took: {toc-tic}')
        print(f'Collision result: {res}')

def main():
    obj = CollisionCheckTest()
    obj.run_test()

if __name__ == '__main__':
    main()
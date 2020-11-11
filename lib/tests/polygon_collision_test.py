#!/usr/bin/env python3

import random, sys, os, math, time
from matplotlib import pyplot as plt
from matplotlib import patches
import numpy as np

path = os.getcwd()
sys.path.insert(1,os.path.dirname(path))

import Utils as util
import Geometry as geom


def polygon_is_collision_speed_test():
    '''
    Determine how long it takes for the concave capable polygon collision check
    call takes
    '''
    print('---------- Polygon Collision checking speed test ----------')
    poly1 = geom.Polygon()
    poly1.unit_circle(40,1.)
    poly1.translate(3.,3.)

    poly2 = geom.Polygon()
    poly2.unit_circle(40,1.)
    poly2.translate(3.2,3.2)

    num_players = 1.
    num_obstacles = 2.
    fps_multiplier = 1./((4*num_players)+(2*num_obstacles))

    tic = time.time()
    collis_res = geom.polygon_is_collision(poly1,poly2)
    toc = time.time()

    print(f'Collision checking took (s): {toc-tic}')
    print(f'Results: {collis_res.any()}')
    try:
        print(f'FPS: {(1./(toc-tic))*fps_multiplier}')
    except:
        print("Couldn't compute FPS...")

    geom.polygon_plot(poly1,poly2,lim=[0,15,0,15],title=f'Collision Result: {collis_res}')

def polygon_is_collision_vertices_test():
    '''
    Determine how long it takes for the concave capable polygon collision check
    call takes
    '''
    print('---------- Polygon Collision checking speed test ----------')
    
    poly1 = geom.Polygon()
    top_left = np.array([[200.],[77.3]])
    bot_right = np.array([[225.],[27.3]])
    poly1.rectangle(top_left,bot_right)

    poly2 = geom.Polygon()
    top_left = np.array([[0.],[50.]])
    bot_right = np.array([[1800.],[0.]])
    poly2.rectangle(top_left,bot_right)

    collis_res = geom.polygon_is_collision(poly2,poly1)

    print(f'Results: {collis_res.any()}')

    geom.polygon_plot(poly1,poly2,lim=[0,2000,0,200],title=f'Collision Result: {collis_res}')

def proximity_check_test():
    print('---------- Proximity Checking Test ----------')
    
    poly1 = geom.Polygon()
    poly1.unit_circle(5,3)
    
    poly2 = geom.Polygon()
    top_left = np.array([[0.],[3.]])
    bottom_right = np.array([[5.],[0.]])
    poly2.rectangle(top_left,bottom_right)

    poly1.translate(5,5)
    poly2.translate(7,7)

    tic = time.time()
    sphere_res = geom.sphere_is_collision(poly1,poly2)
    toc = time.time()
    print(f'Sphere time: {toc-tic}')

    tic = time.time()
    collis_res = geom.polygon_is_collision(poly1,poly2)
    toc = time.time()
    print(f'Poly time: {toc-tic}')

    geom.polygon_plot(poly1,poly2,lim=[0,15,0,15],title=f'Prominity Test\nCollision Result: {collis_res}\nSphere Collision: {sphere_res}')

def main():
    '''
    Run test cases
    '''
    
    polygon_is_collision_speed_test()
    
    # polygon_is_collision_vertices_test()

    # proximity_check_test()


    # Show plots
    plt.show()

if __name__ == '__main__':
    main()
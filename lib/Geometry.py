#!/usr/bin/env python3

import os, sys, time
import datetime as dt
from threading import Thread
from math import sin,cos,atan2
# from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process
from multiprocessing import Pool
import math
import numpy as np
import copy
import random
# from numba import jit

from lib.Utils import *
try:
    from matplotlib import pyplot as plt
    from matplotlib import patches
except:
    log('Matplot lib import skipped...')

def edge_angle(ang_type,*argv):
    '''
    The edge angle is found using unit vectors. This function can be passed two angles defined counter clowise from 0 being horizontal, or
    a set of three vertices.
    '''
    # This function finds the signed shortest distance between two vectors
    if ang_type == 'angle':
        assert(len(argv)==2)

        ang1 = float(argv[0])
        ang2 = float(argv[1])
        vertex0 = [0.0,0.0]
        vertex1 = [cos(ang1),sin(ang1)]
        vertex2 = [cos(ang2),sin(ang2)]
    elif ang_type == 'vertices':
        assert(len(argv)==3)

        vertex0 = argv[0]
        vertex1 = argv[1]
        vertex2 = argv[2]
    else:
        log('Edge angle type not recognized!',color='r')
        return None

    # Dot product of the vectors
    cosine_theta = vertex1[0]*vertex2[0] + vertex1[1]*vertex2[1]
    
    # Cross product of the vectors
    sin_theta = vertex1[0]*vertex2[1] - vertex1[1]*vertex2[0]
    
    # find the angle using the relationships sin(theta)== tan(theta) = sin(theta)/cos(theta)
    edge_angle = atan2(sin_theta,cosine_theta)
    return edge_angle

def cross_product(p1, p2):
    '''
    calculates the cross product of vector p1 and p2
    if p1 is clockwise from p2 wrt origin then it returns +ve value
    if p2 is anti-clockwise from p2 wrt origin then it returns -ve value
    if p1 p2 and origin are collinear then it returs 0
    source: https://algorithmtutor.com/Computational-Geometry/Determining-if-two-consecutive-segments-turn-left-or-right/
    '''
    return p1[0] * p2[1] - p2[0] * p1[1]


def direction(p1, p2, p3):
    '''
    returns the cross product of vector p1p3 and p1p2
    if p1p3 is clockwise from p1p2 it returns +ve value
    if p1p3 is anti-clockwise from p1p2 it returns -ve value
    if p1 p2 and p3 are collinear it returns 0
    source: https://algorithmtutor.com/Computational-Geometry/Determining-if-two-consecutive-segments-turn-left-or-right/
    '''
    return  cross_product(p3-p1, p2-p1)

def on_segment(p1, p2, p):
    '''
    checks if p lies on the segment p1p2
    source: https://algorithmtutor.com/Computational-Geometry/Determining-if-two-consecutive-segments-turn-left-or-right/
    '''
    return min(p1[0], p2[0]) <= p[0] <= max(p1[0], p2[0]) and min(p1[1], p2[1]) <= p[1] <= max(p1[1], p2[1])

def edge_is_collision(edge1,edge2,endpoint_collision=False):
    '''
    checks if line segment p1p2 and p3p4 intersect
    source: https://algorithmtutor.com/Computational-Geometry/Check-if-two-line-segment-intersect/
    '''
    p1 = edge1[:,0]
    p2 = edge1[:,1]
    p3 = edge2[:,0]
    p4 = edge2[:,1]

    d1 = direction(p3, p4, p1)
    d2 = direction(p3, p4, p2)
    d3 = direction(p1, p2, p3)
    d4 = direction(p1, p2, p4)

    if endpoint_collision:
        if d1 == 0 and on_segment(p3, p4, p1):
            return True
        elif d2 == 0 and on_segment(p3, p4, p2):
            return True
        elif d3 == 0 and on_segment(p1, p2, p3):
            return True
        elif d4 == 0 and on_segment(p1, p2, p4):
            return True

    # Overlap collision check
    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
        ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
        return True
    else:
        return False


def polygon_is_self_occluded(vertex,vertexPrev,vertexNext,point):
    '''
    Determines if a set of test points are Self Occluded, or non-intersecting but within a polygon 
    Inputs are three [2 x 1] vectors that represent a vertex on a polygon,
    the vertex that preceeded it, and the vertex that follows in
    construction, and a [2 x N] matrix of test points of the form [x1..xn; y1...yn].
    Function handles both counterclockwise or filled-in polygons and clockwise or
    hollow polygons. Output is [1 x N] boolean array where true is a self
    occluded test point.
    '''
    results = np.zeros(len(point[0,:]),dtype=bool)

    for iPoints in range(0,len(point[0,:])):
        angleNext = atan2(vertexNext[1]-vertex[1],vertexNext[0]-vertex[0])
        anglePrev = atan2(vertexPrev[1]-vertex[1],vertexPrev[0]-vertex[0])
        anglePoint = atan2(point[1,iPoints]-vertex[1],point[0,iPoints]-vertex[0])
        
        # maintaining the vertices gives a consistent relationship of what
        # angles constitue self-occlusion for both counterclockwise and
        # clockwise objects, but is dependent on whether the previous angle
        # was greater or less than the next angle.
        if anglePrev > angleNext:
            if anglePoint < anglePrev and anglePoint > angleNext:
                results[iPoints]=True
            else:
                results[iPoints]=False
        else:
            if anglePoint < anglePrev or anglePoint > angleNext:
                results[iPoints]=True
            else:
                results[iPoints]=False
    return results


def polygon_is_visible(vertices,indexVertex,points):
    '''
    Determines if a set of test points are visible by a paticular vertex of a polygon
    Inputs are a [2 x N] set of vertices that define a polygon of the form
    [x1..xn; y1..yn], an integer index to indicate which vertex to test,
    and a [2 x N] set of coordinates that are test points of the form [x; y].
    The function combines the output of two helper functions, to determine 
    if the test point is invisible to the vertex by either self-occlusion
    or collision with an edge of the polygon. Output is a [1 x N] boolean 
    array where true means the test point is visible.
    '''
    # Error handling for indexVertex
    if indexVertex > len(vertices[0,:])-1 or indexVertex < 0:
        log('IndexVertex must be a valid column index of "vertices" between 1 and size(vertices,2)')
        return
    
    # Converting inputs to inputs for polygon_isSelfOccluded() and handling
    # the roll-over cases for the indexVertex input
    vertex = vertices[:,indexVertex].reshape((2,1))
    if indexVertex == 0:
        vertexPrev = vertices[:,-1]
    else:
        vertexPrev=vertices[:,indexVertex-1]

    if indexVertex == len(vertices[0,:])-1:
        vertexNext=vertices[:,0]
    else:
        vertexNext=vertices[:,indexVertex+1]
    selfOccludedPoints = polygon_is_self_occluded(vertex,vertexPrev,vertexNext,points)
    
    # Running edge_isCollision for each test point against every edge of the
    # polygon. 'Break' is added to stop checking once the first collision is
    # found
    # edgeCollisionPoints=false(1,size(points,2))
    edgeCollisionPoints = np.zeros(len(points[0,:]),dtype=bool)
    for iPoints in range(0,len(points[0,:])): #1:size(points,2)
        # The first of the two lines to check collision for is always the
        # line from the test point to inputed vertex
        sightLine = np.concatenate((vertex,points[:,iPoints].reshape(2,1)),axis=1)
        for jEdges in range(0,len(vertices[0,:])): #=1:size(vertices,2)
            if jEdges == len(vertices[0,:])-1:
                edge = np.concatenate((vertices[:,jEdges].reshape(2,1),vertices[:,0].reshape(2,1)),axis=1)
            else:
                edge = np.concatenate((vertices[:,jEdges].reshape(2,1),vertices[:,jEdges+1].reshape(2,1)),axis=1)
            
            if edge_is_collision(sightLine,edge) == True:
                edgeCollisionPoints[iPoints]=True
                break
    # helper functions return 'is invisible'; invert results for 'visible'
    return np.logical_not(np.logical_or(selfOccludedPoints,edgeCollisionPoints))


def point_is_collision(poly1,point):
    '''
    For a given pair of polygon objects, check if the bounding spheres
    are in collision
    '''
    result = True
    for idx in range(0,len(poly1[0,:])):
        if polygon_is_visible(poly1,idx,point):
         result = False
         return result
    
    return result

def sphere_is_collision(poly1,poly2):
    '''
    This function determines if two spheres are in collision
    positive r --> solid sphere
    negative r --> hollow sphere
    '''
    dist = np.sqrt(np.power(poly1.sphere.pose[0]-poly2.sphere.pose[0],2)+np.power(poly1.sphere.pose[1]-poly2.sphere.pose[1],2))
    if (poly1.sphere.radius < 0) and (poly2.sphere.radius < 0):
        return True
    elif (poly1.sphere.radius < 0) or (poly2.sphere.radius < 0):
        if dist > -1*(poly1.sphere.radius+poly2.sphere.radius):
            return True
        else:
            return False
    else:
        if dist < (poly1.sphere.radius+poly2.sphere.radius):
            return True
        else:
            return False


def polygon_is_collision(poly1,poly2,*argv):
    '''
    Assume two sets of vertices are passed representing two polygons
    # Two instances of the Polygon class are passed to it 
    '''
    results = np.zeros(1,dtype=bool)

    if type(poly1) == Polygon:
        vertices1 = copy.deepcopy(poly1.vertices)

    else:
        vertices1 = copy.deepcopy(poly1)
    
    if type(poly2) == Polygon:
        vertices2 = copy.deepcopy(poly2.vertices)
    else:
        vertices2 = copy.deepcopy(poly2)

    collision = False
    for idx1 in range(0,len(vertices1[0,:])):
        for idx2 in range(0,len(vertices2[0,:])):
            r,c = vertices1.shape[0:2]
            if idx1 == c-1:
                edge1 = np.concatenate((vertices1[:,idx1].reshape(2,1),vertices1[:,0].reshape(2,1)),axis=1)
            else:
                edge1 = np.concatenate((vertices1[:,idx1].reshape(2,1),vertices1[:,idx1+1].reshape(2,1)),axis=1)
            
            r,c = vertices2.shape[0:2]
            if idx2 == c-1:
                edge2 = np.concatenate((vertices2[:,idx2].reshape(2,1),vertices2[:,0].reshape(2,1)),axis=1)
            else:
                edge2 = np.concatenate((vertices2[:,idx2].reshape(2,1),vertices2[:,idx2+1].reshape(2,1)),axis=1)
               
            if edge_is_collision(edge1,edge2,endpoint_collision=False):
                collision = True
                results[0] = True
                break
        
        if collision:
            break
    
    return results


def multithreaded_polygon_is_collision(pool,vertices,points):
    '''
    Determines if a set of points lies inside or outside of a given polygon
    Inputs are a [2 X N] set of vertices of the form [x1..xn; y1...yn] and
    a [2 x N] set of test points of the same form. Uses lower level
    function polygon_isVisible to determine if test point is visible to any
    vertex of the polygon, and thus inside or outside. Note: for a hollow
    polygon, 'outside' or non-collision is inside the polygon. Output is
    a [1 X N] boolean array where true means the point is colliding. 
    '''
    num_threads = 4

    point_args = []
    for idx in range(0,len(points[0,:])):
        point_args.append((vertices,points[:,idx].reshape(2,1)))
    reslts = pool.starmap(polygon_is_collision,point_args)
    
    results = np.zeros(1,dtype=bool)
    for res in reslts:
        results = np.logical_or(results, res)

    return results


def polygon_is_filled(vertices):
    '''
    Checks the ordering of the vertices, and returns whether the polygon is filled
    in or not.
    '''
    r_num,c_num = vertices.shape
    
    VecSet = np.zeros(vertices.size).reshape((r_num,c_num))
    SubVec = np.zeros(vertices.size).reshape((r_num,c_num))

    #Assignment for vectors.
    VecSet[:,0:c_num-2] = vertices[:,1:c_num-1]
    VecSet[:,c_num-1] = vertices[:,0]
    VecSet = VecSet-vertices

    SubVec[:,0:c_num-2] = VecSet[:,1:c_num-1]
    SubVec[:,c_num-1] = VecSet[:,0]

    angleSum = 0

    # compute the sum of angle that line segments rotate.
    for index in range(0,c_num):#1:c_num:
        angleSum += edge_angle('vertices',np.array([[0],[0]]),VecSet[:,index],SubVec[:,index])

    # positive --> counter-clockwise
    # negative --> clockwise
    if angleSum > 0:
        return True
    elif angleSum < 0:
        return False
    else:
        return None


def reshape_for_patch(vertices):
    '''
    Matplotlib patch() method takes vertives in [n,2] shape
    Polygon class stores vertices as [2,n]
    This function takes [2,n] format and returns [n,2]
    '''
    r,c = vertices.shape
    out = np.zeros(vertices.size)
    out = np.reshape(out,(c,r))
    for i in range(0,c):
        for j in range(0,r):
            out[i,j] = vertices[j,i]
    return out


def transform(frame,*argv,translate=None):
    '''
    Convert from image frame with origin in top left with positive y down, to
    conventional cartesian with origin in bottom left and positive y up.
    Both frames have positive x right when using the img transform.
    '''
    if frame == 'img':
        assert(translate!=None)
        transform_entities = []
        for arg in argv:
            arg[1,:] = -1 * arg[1,:]
            arg[1,:] = arg[1,:] + translate
            transform_entities.append(arg)

        if len(transform_entities) == 1:
            transform_entities = transform_entities[0]
        return transform_entities
    else:
        return argv

def polygon_plot(*argv,color=None,point_color=None,lim=[-5,5,-5,5],title='A Plot',poly_fill=True):
    _,ax = plt.subplots(1)
    if lim != None:
        assert(len(lim)==4)
        ax.set_xlim(lim[0], lim[1])
        ax.set_ylim(lim[2], lim[3])
    
    if color == None:
        color = ['r','g','b']
    else:
        color = list(color)

    for arg in argv:
        c_idx = random.randint(0,len(color)-1)
        vertices = reshape_for_patch(arg.vertices)
        patch = patches.Polygon(vertices, alpha=0.6,facecolor=color[c_idx],fill=True)
        ax.add_patch(patch)

        circle_patch = patches.Circle((arg.sphere.pose[0],arg.sphere.pose[1]),radius=arg.sphere.radius,fill=False)
        ax.add_patch(circle_patch)

    plt.gca().set_aspect('equal', adjustable='box')
    plt.grid(color='k', linestyle='-', linewidth=.5)
    plt.title(f'{title}')

class Sphere(object):
    def __init__(self,x,y,r):
        self.pose = np.array([[x],[y]])
        self.radius = r

class Polygon(object):
    def __init__(self,*argv,poly_type=None):
        self.vertices = None
        self.sphere = None

        if poly_type == 'rect':
            assert(len(argv)==2)
            self.rectangle(argv[0],argv[1])
        elif poly_type == 'peak':
            assert(len(argv)==3)
            self.peak(argv[0],argv[1],argv[2])

    def unit_circle(self,num,rad):
        self.vertices = np.zeros(num*2).reshape(2,num)
        theta = 0.
        d_theta = (2*np.pi)/float(num)
        for idx in range(0,num):
            x = rad*np.cos(theta)
            y = rad*np.sin(theta)
            self.vertices[0,idx] = x
            self.vertices[1,idx] = y
            theta += d_theta
        
        self.set_bounding_sphere()

    def rectangle(self,top_left,bottom_right):
        top_right = np.array([ bottom_right[0] , top_left[1] ],dtype=float)
        bottom_left = np.array([ top_left[0],bottom_right[1] ],dtype=float)
        self.vertices = np.concatenate((top_left,bottom_left,bottom_right,top_right),axis=1)

        self.set_bounding_sphere()
    
    def peak(self,top_left,bottom_right,rise):
        top_right = np.array([ bottom_right[0] , top_left[1] ],dtype=float)
        bottom_left = np.array([ top_left[0],bottom_right[1] ],dtype=float)
        center_high_1 = np.array([ ((top_right[0]-top_left[0])/2.)+300. , top_left[1]-rise ])
        center_high = np.array([ ((top_right[0]-top_left[0])/2.), top_left[1]-(rise/3.) ])
        center_high_2 = np.array([ ((top_right[0]-top_left[0])/2.)-300. , top_left[1]-rise ])

        self.vertices = np.concatenate((top_left,bottom_left,bottom_right,top_right,center_high_1,center_high,center_high_2),axis=1)

        self.set_bounding_sphere()

    def set_bounding_sphere(self):
        # Compute centroid    
        r,c = self.vertices.shape[0:2]
        x_c = np.sum(self.vertices[0,:]) / float(c)
        y_c = np.sum(self.vertices[1,:]) / float(c)

        # Compute radius
        r = 0.
        centroid = np.array([[x_c],[y_c]])
        for idx in range(0,len(self.vertices[0,:])):
            vert = self.vertices[:,idx]
            rad = np.sqrt(np.power(vert[0]-centroid[0],2)+np.power(vert[1]-centroid[1],2))
            if rad > r:
                r = rad 
        
        self.sphere = Sphere(x_c,y_c,r)

    def translate(self,x,y):
        for idx in range(0,len(self.vertices[0,:])):
            self.vertices[0,idx] += x
            self.vertices[1,idx] += y

        self.sphere.pose[0] += x
        self.sphere.pose[1] += y

    def teleport(self,x,y):
        coord = np.array([x,y])
        diff = coord - self.sphere.pose

        self.translate(diff[0],diff[1])

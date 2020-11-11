#!/usr/bin/env python3

import random, sys, os, math, time, numpy
from matplotlib import pyplot as plt
from matplotlib import patches

path = os.getcwd()
sys.path.insert(1,os.path.dirname(path))

from Utils import *
from Geometry import *

print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')

print('/////////////////////////////////////////////////////////////////////')
print('/ Edge Angle Tests')
print('/////////////////////////////////////////////////////////////////////')
ang1 = 0.
ang2 = 0.
same_edges_angle = edge_angle('angle',ang1,ang2)
print(f'Angles: {ang1} & {ang2}\nResults: {same_edges_angle}')

ang1 = 0.
ang2 = 7.
same_edges_angle = edge_angle('angle',ang1,ang2)
print(f'\nAngles: {ang1} & {ang2}\nResults: {same_edges_angle}')

ang1 = 0.2
ang2 = 6.
same_edges_angle = edge_angle('angle',ang1,ang2)
print(f'\nAngles: {ang1} & {ang2}\nResults: {same_edges_angle}')

print('\n/////////////////////////////////////////////////////////////////////')
print('/ Edge Collision Tests')
print('/////////////////////////////////////////////////////////////////////')
edge1 = np.array([ [0.,1.] , [0.,0.]])
edge2 = np.array([ [0.,1.] , [1.,1.]])
edge_collision = edge_is_collision(edge1,edge2)
print('Parallel:')
print(f'Expected: False\nResults: {edge_collision}')

edge1 = np.array([ [0.,1.] , [0.,0.]])
edge2 = np.array([ [0.5,0.5] , [-0.5,1.]])
edge_collision = edge_is_collision(edge1,edge2)
print('\nCollision')
print(f'Expected: True\nResults: {edge_collision}')

edge1 = np.array([ [0.,1.] , [0.,0.]])
edge2 = np.array([ [0.5,0.5] , [0.,1.]])
edge_collision = edge_is_collision(edge1,edge2)
print('\nOn Edge')
print(f'Expected: False\nResults: {edge_collision}')

edge1 = np.array([ [0.,-1.] , [-1.,1.]])
edge2 = np.array([ [0.,-1.] , [5.,-0.5]])
edge_collision = edge_is_collision(edge1,edge2)
print('\nSharing One Vertex')
print(f'Expected: False\nResults: {edge_collision}')

print('\n/////////////////////////////////////////////////////////////////////')
print('/ Polygon is Self Occluded')
print('/////////////////////////////////////////////////////////////////////')
# Clockwise ordering aka hollow
# Point in polygon
vertex = np.array([0.,0.])
vertexPrev = np.array([-1.,-1.])
vertexNext = np.array([1.,-1.])
point = np.array([ [0.] , [1.] ])
self_occluded = polygon_is_self_occluded(vertex,vertexPrev,vertexNext,point)
print(f'Expected: True\nResults: {self_occluded}')

# Clockwise ordering aka hollow
# Point outside polygon
vertex = np.array([0.,0.])
vertexPrev = np.array([-1.,-1.])
vertexNext = np.array([1.,-1.])
point = np.array([ [0.] , [-1.] ])
self_occluded = polygon_is_self_occluded(vertex,vertexPrev,vertexNext,point)
print(f'\nExpected: False\nResults: {self_occluded}')

# Counter-Clockwise ordering aka filled
# Point outside polygon
vertex = np.array([0.,0.])
vertexPrev = np.array([1.,-1.])
vertexNext = np.array([-1.,-1.])
point = np.array([ [0.] , [1.] ])
self_occluded = polygon_is_self_occluded(vertex,vertexPrev,vertexNext,point)
print(f'\nExpected: False\nResults: {self_occluded}')

print('\n/////////////////////////////////////////////////////////////////////')
print('/ Polygon is Visible')
print('/////////////////////////////////////////////////////////////////////')

####### Visible Test #########
print('VISIBLE TEST')
vertices = np.array([ [0.,5.,5.,0.] , [-1.,-0.5,0.5,1.] ])
points = np.array([ [-1.] , [1.] ])

is_visible = polygon_is_visible(vertices,0,points)
print(f'Expected: True\nResults: {is_visible}')
polygon_plot(vertices,points=points,title=f'Visible | Expected: True\nResults: {is_visible}')

####### InVisible Test #########
print('\nINVISIBLE TEST')
vertices = np.array([ [0.,5.,5.,0.] , [-1.,-0.5,0.5,1.] ])
points = np.array([ [1.] , [0.2] ])

is_visible = polygon_is_visible(vertices,0,points)
print(f'Expected: False\nResults: {is_visible}')
polygon_plot(vertices,points=points,title=f'InVisible | Expected: False\nResults: {is_visible}')

####### On Edge #########
print('\nON EDGE TEST')
vertices = np.array([ [0.,5.,5.,0.] , [-1.,-0.5,0.5,1.] ])
points = np.array([ [0.] , [0.] ])

is_visible = polygon_is_visible(vertices,0,points)
print(f'Expected: True\nResults: {is_visible}')
polygon_plot(vertices,points=points,title=f'Visible On Edge | Expected: True\nResults: {is_visible}')

print('\n/////////////////////////////////////////////////////////////////////')
print('/ Polygon is Collision Test')
print('/////////////////////////////////////////////////////////////////////')

print('In collision test:')
vertices = np.array([ [0.,5.,5.,0.] , [-1.,-0.5,0.5,1.] ])
points = np.array([ [1.,2.] , [0.2,2.] ])

start = time.time()
result = polygon_is_collision(vertices,points)
end = time.time()
print(f'Expected: True | Result: {result}')
print(f'Collision checking took {(end-start)/float(len(points[0,:]))} seconds per point.')
polygon_plot(vertices,points=points,title=f'Results: {result}')

print('\nOverlapping Test')
top_left = np.array([[0.],[1.]])
bottom_right = np.array([[1.],[0.]])
poly = Polygon(top_left,bottom_right,poly_type='rect')
poly2 = Polygon(top_left,bottom_right,poly_type='rect')

start = time.time()
result = polygon_is_collision(poly.vertices,poly2.vertices)
end = time.time()
print(f'Results: {result.any()}')
print(f'Collision checking took {(end-start)/float(len(poly2.vertices[0,:]))} per point')
polygon_plot(poly.vertices,lim=5,points=poly2.vertices,title=f'Results: {result.any()}')

print('\nPolygon Intersection')
top_left = np.array([[-2.],[2.]])
bottom_right = np.array([[2.],[-2.]])
poly = Polygon(top_left,bottom_right,poly_type='rect')

top_left = np.array([[0.],[1.]])
bottom_right = np.array([[1.],[0.]])
poly2 = Polygon(top_left,bottom_right,poly_type='rect')

start = time.time()
result = polygon_is_collision(poly.vertices,poly2.vertices)
end = time.time()
print(f'Results: {result.any()}')
print(f'Collision checking took {(end-start)/float(len(poly2.vertices[0,:]))} per point.')
polygon_plot(poly.vertices,lim=5,points=poly2.vertices,title=f'Results: {result.any()}')

print('\nGame Output Test')
points = np.array([ [600.,600.,625.,625. ] , [248.5,198.5,198.5,248.5] ])
vertices = np.array([ [0.,0.,1800.,1800.] , [50.,0.,0.,50.] ])

start = time.time()
result = polygon_is_collision(vertices,points)
fill1 = polygon_is_filled(vertices)
fill2 = polygon_is_filled(points)
print(f'Fills: {fill1} {fill2}')
end = time.time()
print(f'Result: {result}')
print(f'Collision checking took {(end-start)/float(len(points[0,:]))} seconds per point.')
polygon_plot(vertices,lim=None,points=points,title=f'Results: {result}')


print('\nGame Output Test')

points = np.array([ [868.20,868.20, 893.2, 893.2] , [510.6,460.6,460.6,510.66] ])
vertices = np.array([ [0.,0.,1800.,1800.] , [50.,0.,0.,50.] ])

start = time.time()
result = polygon_is_collision(vertices,points)
fill1 = polygon_is_filled(vertices)
fill2 = polygon_is_filled(points)
print(f'Fills: {fill1} {fill2}')
end = time.time()
print(f'Result: {result}')
print(f'Collision checking took {(end-start)/float(len(points[0,:]))} seconds per point.')
polygon_plot(vertices,lim=None,points=points,title=f'Results: {result}')

print('\n/////////////////////////////////////////////////////////////////////')
print('/ Polygon filled check')
print('/////////////////////////////////////////////////////////////////////')

print('Counter-Clockwise:')
vertices = np.array([ [0.,5.,5.,0.] , [-1.,-0.5,0.5,1.] ])
res = polygon_is_filled(vertices)
print(f'Expected: True | Result: {res}')

print('\nClockwise:')
vertices = np.flip(np.array([ [0.,5.,5.,0.] , [-1.,-0.5,0.5,1.] ]),1)
res = polygon_is_filled(vertices)
print(f'Expected: False | Result: {res}')

#### Display plots
plt.show()

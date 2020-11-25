#!/usr/bin/env python
""" Library for creating 2D graphs, and then determining free space and connections to generate a roadmap """

import numpy as np
import math, sys
import ctypes

from lib.PerlinNoise import *
from lib.Utils import *
from lib.Geometry import *

# Class that constructs an empty node in a graph
class Node(object):
    def __init__(self):
        self.occupied = False
        self.start = False
        self.goal = False
        self.idx = None

        self.coord = np.array([[],[]])
        self.neighbors = []
        self.neighbors_cost = []
        self.backpointer = None
        self.backpointer_cost = None
    def node_type(self):
        if self.occupied:
            node_type = 'Occupied'
        elif self.start:
            node_type = 'Start'
        elif self.goal:
            node_type = 'Goal'
        else:
            node_type = 'Free Space'
        return node_type

# Class that builds a 2D roadmap
class RoadmapBuilder(FilePaths):
    def __init__(self):
        super().__init__()
        self.roadmap = []
        self.obstacles = []

        self.grid_size = None
        self.graph = None
        self.occupancy_graph = None

        self.start_idx = np.zeros([2,1]) - 1
        self.goal_idx = np.zeros([2,1]) - 1

        # C library for collision checking
        self.c_float_p = ctypes.POINTER(ctypes.c_double)
        self.fun = ctypes.CDLL(f'{self.user_path}lib/{self.cc_lib_path}') # Or full path to file
        self.fun.polygon_is_collision.argtypes = [self.c_float_p,ctypes.c_int,ctypes.c_int,self.c_float_p,ctypes.c_int,ctypes.c_int] 
    
    def construct_square(self,num):
        self.grid_size = num
        self.graph = np.empty([num, num],dtype=Node)
        for x in range(0,num):
            for y in range(0,num):
                insert_node = Node()
                insert_node.coord = np.array([[x],[y]])
                self.graph[x][y] = insert_node
    
    def set_obstacles(self,size,passes=2,cutoff=1.1):
        self.occupancy_graph = None
        self.occupancy_graph = generate_graph(size,passes=passes,cutoff=cutoff)

    def clear_obstacles(self):
        self.occupancy_graph = None
        self.occupancy_graph = np.zeros([self.grid_size,self.grid_size])

    def init_roadmap(self):
        r,c = self.graph.shape
        self.roadmap = []
        roadmap_idx = 0
        for i in range(0,r):
            for j in range(0,c):
                if self.occupancy_graph[i,j] == 0:
                    self.graph[i,j].idx = roadmap_idx
                    self.graph[i][j].occupied = False
                    self.roadmap.append(self.graph[i,j])
                    roadmap_idx += 1
                else:
                    self.graph[i,j].idx = None
                    self.graph[i][j].occupied = True
    
    def set_neighbors(self,diagonals=True):
        r,c = self.graph.shape
        log(f'Generating neighbors for graph with shape: {r} {c}')
        for i in range(0,r):
            for j in range(0,c):
                self.graph[i,j].neighbors = []
                self.graph[i,j].neighbors_cost = []
                self.graph[i,j].backpointer = None
                self.graph[i,j].backpointer_cost = None

                if not self.graph[i,j].occupied:
                    idx = self.graph[i,j].idx
                    # immediate neighbors
                    if (i+1 < r):
                        if not self.graph[i+1,j].occupied:
                            neighbor_idx = self.graph[i+1,j].idx
                            self.roadmap[idx].neighbors.append(neighbor_idx)
                            self.roadmap[idx].neighbors_cost.append(1.)
                    if (j+1 < c):
                        if not self.graph[i,j+1].occupied:
                            neighbor_idx = self.graph[i,j+1].idx
                            self.roadmap[idx].neighbors.append(neighbor_idx)
                            self.roadmap[idx].neighbors_cost.append(1.)
                    if (i-1 >= 0):
                        if not self.graph[i-1,j].occupied:
                            neighbor_idx = self.graph[i-1,j].idx
                            self.roadmap[idx].neighbors.append(neighbor_idx)
                            self.roadmap[idx].neighbors_cost.append(1.)
                    if (j-1 >= 0):
                        if not self.graph[i,j-1].occupied:
                            neighbor_idx = self.graph[i,j-1].idx
                            self.roadmap[idx].neighbors.append(neighbor_idx)
                            self.roadmap[idx].neighbors_cost.append(1.)
                    # diagonals
                    if diagonals:
                        if (i+1 < r) and (j+1 < c):
                            if not self.graph[i+1,j+1].occupied:
                                neighbor_idx = self.graph[i+1,j+1].idx
                                self.roadmap[idx].neighbors.append(neighbor_idx)
                                self.roadmap[idx].neighbors_cost.append(1.414)
                        if (i-1 >= 0) and (j+1 < c):
                            if not self.graph[i-1,j+1].occupied:
                                neighbor_idx = self.graph[i-1,j+1].idx
                                self.roadmap[idx].neighbors.append(neighbor_idx)
                                self.roadmap[idx].neighbors_cost.append(1.414)
                        if (i-1 >= 0) and (j-1 >= 0):
                            if not self.graph[i-1,j-1].occupied:
                                neighbor_idx = self.graph[i-1,j-1].idx
                                self.roadmap[idx].neighbors.append(neighbor_idx)
                                self.roadmap[idx].neighbors_cost.append(1.414)
                        if (i+1 < r) and (j-1 >= 0):
                            if not self.graph[i+1,j-1].occupied:
                                neighbor_idx = self.graph[i+1,j-1].idx
                                self.roadmap[idx].neighbors.append(neighbor_idx)
                                self.roadmap[idx].neighbors_cost.append(1.414)

    def find_nearest_neighbors(self,node_idx,num_neighbors):
        nearest_idx = []
        nearest_dist = []
        nearest_neighbors = []
        costs = []

        for idx in range(0,len(self.roadmap)):
            dist = self.euclidian_distance(node_idx,idx)
            nearest_idx.append(idx)
            nearest_dist.append(dist)

        self_idx = nearest_idx.index(node_idx)
        nearest_dist.pop(self_idx)
        nearest_idx.pop(self_idx)

        for num in range(0,num_neighbors):
            idx = nearest_dist.index(min(nearest_dist))
            
            neighbor = nearest_idx[idx]
            cost = nearest_dist[idx]
            nearest_neighbors.append(neighbor)
            costs.append(cost)
            
            nearest_dist.pop(idx)
            nearest_idx.pop(idx)
        
        return nearest_neighbors,costs

    def euclidian_distance(self,idx_start,idx_end):
        start = self.roadmap[idx_start].coord
        end = self.roadmap[idx_end].coord
        return math.pow((math.pow(start[0]-end[0],2) + math.pow(start[1]-end[1],2)),.5)

    def collision_check(self,n1,n2):
        '''
        This function is passed two node indexes in the roadmap, and returns if the edge connecting them is collision free.
        The edge connecting them is assumed to be bi-directional.
        The roadmap builder's collision geometry is checked against the environment's collision geometry.
        Arguments:
            n1 [int]: index of node 1
            n2 [int]: index of node 2
        Returns:
            res [bool]: if the edge is collision free
        '''
        data = copy.deepcopy(self.sprite.polys[self.sprite.idx].vertices)
        data = data.astype(np.double)
        data_p = data.ctypes.data_as(self.c_float_p)

        data2 = copy.deepcopy(obs_check.vertices)
        data2 = data2.astype(np.double)
        data_p2 = data2.ctypes.data_as(self.c_float_p)

        # get two polygons
        # collision check
        # if not in collision, translate the agent
        # collision check
        # repeat

        # C Function call in python
        res = self.fun.polygon_is_collision(data_p,2,len(self.sprite.polys[self.sprite.idx].vertices[0,:]),data_p2,2,len(obs_check.vertices[0,:]))
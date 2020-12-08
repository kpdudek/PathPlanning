#!/usr/bin/env python
""" Library for creating 2D graphs, and then determining free space and connections to generate a roadmap """

import numpy as np
import math, sys
import ctypes

from lib.Noise import *
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
        self.geom = None

        self.grid_size = None
        self.tile_size = None
        self.graph = None
        self.occupancy_graph = None

        self.start_idx = np.zeros([2,1]) - 1
        self.goal_idx = np.zeros([2,1]) - 1

        self.epsilon = 5
        self.collision_calls = 0

        # C library for collision checking
        self.c_float_p = ctypes.POINTER(ctypes.c_double)
        self.fun = ctypes.CDLL(f'{self.user_path}lib/{self.cc_lib_path}') # Or full path to file
        self.fun.polygon_is_collision.argtypes = [self.c_float_p,ctypes.c_int,ctypes.c_int,self.c_float_p,ctypes.c_int,ctypes.c_int] 
    
    def set_geometry(self):
        self.geom = Polygon()
        self.geom.unit_circle(4,10)

    def construct_square(self,num,size):
        self.grid_size = num
        self.tile_size = size
        self.graph = np.empty([num, num],dtype=Node)
        for x in range(0,num):
            for y in range(0,num):
                insert_node = Node()
                insert_node.coord = np.array([[x],[y]])
                self.graph[x][y] = insert_node
    
    def set_obstacles(self,size,noise_type=None,passes=2,cutoff=1.1):
        if noise_type == 'perlin':
            log(f'Generating perlin noise.')
            tmp = perlin_noise(size,passes=passes,cutoff=cutoff)
            
        elif noise_type == 'random':
            log(f'Generating random noise.')
            tmp = random_noise(size,cutoff=cutoff)
        
        self.occupancy_graph = np.logical_or(self.occupancy_graph,tmp) 

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
        self.collision_calls = 0

        r,c = self.graph.shape
        log(f'Generating neighbors for graph with shape: {r} {c}')
        for i in range(0,r):
            for j in range(0,c):
                # reset all node elements except for its graph coordinate
                self.graph[i,j].neighbors = []
                self.graph[i,j].neighbors_cost = []
                self.graph[i,j].backpointer = None
                self.graph[i,j].backpointer_cost = None

                # Generate a list of lists where each sub list is the vector from the current node to its
                # prospective neighbor
                # TODO: assign random neighbors that are not immediate
                neighbor_list = []
                for k in range(-1,2):
                    for n in range(-1,2):
                        if (k == 0) and (n == 0):
                            pass
                        elif (k != 0) and (n != 0) and (not diagonals):
                            pass
                        else:
                            neighbor_list.append([k,n])
                
                # For every neighbor vector, check if it is a valid neighbor meaning:\
                #   - it is not occupied
                #   - it is a tile in the 2D graph
                #   - the path from start to the neighbor is collision free
                for neighbor in neighbor_list:
                    if not self.graph[i,j].occupied:
                        idx = self.graph[i,j].idx
                        # immediate neighbors
                        if (i+neighbor[0] < r) and (i+neighbor[0] >= 0) and (j+neighbor[1] < c) and (j+neighbor[1] >= 0):
                            if not self.graph[i+neighbor[0],j+neighbor[1]].occupied:
                                neighbor_idx = self.graph[i+neighbor[0],j+neighbor[1]].idx
                                if not self.collision_check(idx,neighbor_idx):
                                    self.roadmap[idx].neighbors.append(neighbor_idx)
                                    dist = self.euclidian_distance(idx,neighbor_idx)
                                    self.roadmap[idx].neighbors_cost.append(dist)
        
        log(f'Collision check calls made: {self.collision_calls}')
        log(f'Epsilon value for edge discretization: {self.epsilon}')

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
        start_coord = self.roadmap[n1].coord
        end_coord = self.roadmap[n2].coord

        x_interp = np.linspace(start_coord[0],end_coord[0],num=self.epsilon).reshape(1,self.epsilon)
        y_interp = np.linspace(start_coord[1],end_coord[1],num=self.epsilon).reshape(1,self.epsilon)
        interp = np.vstack((x_interp,y_interp))
        # print(interp)
        interp = np.hstack((start_coord,interp))
        interp = np.hstack((interp,end_coord))

        # print(interp)
        r,c = self.graph.shape
        for step_idx in range(0,self.epsilon+2):
            for i in range(0,r):
                for j in range(0,c):
                    if self.graph[i,j].occupied:
                        obs_coord = self.graph[i,j].coord * self.tile_size
                        
                        obs = Polygon()
                        obs.rectangle(obs_coord,obs_coord+self.tile_size)
                        data = obs.vertices
                        data = data.astype(np.double)
                        data_p = data.ctypes.data_as(self.c_float_p)


                        agent_coord = interp[:,step_idx].reshape(2,1) * self.tile_size
                        agent = Polygon()
                        agent.rectangle(agent_coord,agent_coord+self.tile_size)
                        data2 = agent.vertices
                        data2 = data2.astype(np.double)
                        data_p2 = data2.ctypes.data_as(self.c_float_p)

                        # # C Function call in python
                        res = self.fun.polygon_is_collision(data_p,2,4,data_p2,2,4)
                        if res:
                            return True
                    self.collision_calls += 1
        return False
#!/usr/bin/env python
""" Library for creating 2D graphs, and then determining free space and connections to generate a roadmap """

import numpy as np
import math
import sys

from lib.PerlinNoise import *

# Class that constructs an empty node in a graph
class Node(object):
    def __init__(self):
        self.occupied = False
        self.coord = np.array([[],[]])
        self.neighbors = []
        self.neighbors_cost = []
        self.backpointer = None
        self.backpointer_cost = None

# Class that builds a 2D roadmap
class RoadmapBuilder(object):
    def __init__(self):
        self.roadmap = []
        self.obstacles = []

        self.graph = None
        self.occupancy_graph = None
    
    def construct_square(self,num):
        self.graph = np.empty([num, num],dtype=Node)
        for x in range(0,num):
            for y in range(0,num):
                insert_node = Node()
                insert_node.coord = np.array([[x],[y]])
                self.graph[x][y] = insert_node
    
    def set_obstacles(self,size):
        self.occupancy_graph = generate_graph(size)

    def init_roadmap(self):
        r,c = self.graph.shape

        for i in range(0,r):
            for j in range(0,c):
                
                if self.occupancy_graph[i,j] == 0:
                    self.roadmap.append(self.graph[i,j])
                    self.graph[i][j].occupied = True
    
    def set_neighbors(self):
        for node_idx in range(0,len(self.roadmap)):
            # Count how many neighbors you have
            # Call nearest neighbors to fill remainer
            # num_neighbors = len(self.roadmap[node_idx].neighbors)
            nearest_neighbors,costs = self.find_nearest_neighbors(node_idx,4)
            self.roadmap[node_idx].neighbors = nearest_neighbors
            self.roadmap[node_idx].neighbors_cost = costs

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


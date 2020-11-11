#!/usr/bin/env python
""" Library for creating 2D graphs, and then determining free space and connections to generate a roadmap """

import sys
sys.path.insert(0,'..')
import numpy as np
import math
import RoadmapBuilder as rb 
import PriorityQueue as pq

class AStar(object):
    def __init__(self,roadmap):
        self.roadmap = roadmap
        self.queue = pq.PriorityQueue()

    def get_plan(self,start_idx,goal_idx):
        '''
        Returns a 2xn array of coordinates
        '''
        idx_closed = []
        self.queue.insert(start_idx,0)
        self.roadmap.roadmap[start_idx].backpointer_cost = 0

        while not self.queue.is_empty():
            idx_next,cost = self.queue.min_extract()
            idx_closed.append(idx_next)
            
            if idx_next == goal_idx:
                break
            
            neighbors = self.expand_list(idx_next,idx_closed)
            for idx_neighbor in range(0,len(neighbors)):
                self.expand_node(idx_next,goal_idx,neighbors[idx_neighbor])
        
        path = self.get_path(start_idx,goal_idx)
        return path

    def expand_list(self,idx_next,idx_closed):
        neighbors = []
        
        neighbors = self.roadmap.roadmap[idx_next].neighbors
        for idx in idx_closed:
            try:
                neighbors.remove(idx)
            except ValueError:
                # print('Closed element not a neighbor...')
                pass
        try:
            neighbors.remove(idx_next)
        except:
            # print('Self not in neighbors...')
            pass

        return neighbors
    
    def expand_node(self,idx_next,goal_idx,neighbor):
        backpointer_cost = self.roadmap.roadmap[idx_next].backpointer_cost
        heuristic = self.graph_heuristic(neighbor,goal_idx)
        idx_cost = self.roadmap.roadmap[idx_next].neighbors.index(neighbor)
        step_cost = self.roadmap.roadmap[idx_next].backpointer_cost + self.roadmap.roadmap[idx_next].neighbors_cost[idx_cost]

        if self.queue.is_member(neighbor):
            if step_cost < self.roadmap.roadmap[neighbor].backpointer_cost:
                self.roadmap.roadmap[neighbor].backpointer_cost = step_cost
                self.roadmap.roadmap[neighbor].backpointer = idx_next
        else:
            self.roadmap.roadmap[neighbor].backpointer_cost = step_cost
            self.roadmap.roadmap[neighbor].backpointer = idx_next
            self.queue.insert(neighbor, step_cost+heuristic)

    def graph_heuristic(self,idx_start,idx_end):
        start = self.roadmap.roadmap[idx_start].coord
        end = self.roadmap.roadmap[idx_end].coord

        return math.pow((math.pow(start[0]-end[0],2) + math.pow(start[1]-end[1],2)),.5)

    def get_path(self,start_idx,goal_idx):
        path = self.roadmap.roadmap[goal_idx].coord

        idx_current = self.roadmap.roadmap[goal_idx].backpointer

        while idx_current != start_idx:
            path = np.append(path,self.roadmap.roadmap[idx_current].coord,axis=1)
            idx_current = self.roadmap.roadmap[idx_current].backpointer
        path = np.append(path,self.roadmap.roadmap[start_idx].coord,axis=1)

        path = np.fliplr(path)
        return path

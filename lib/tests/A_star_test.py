#!/usr/bin/env python
""" Library for creating 2D graphs, and then determining free space and connections to generate a roadmap """

import sys
sys.path.insert(0,'../src')
import A_star as asp
import roadmap_builder as rb

roadmap = rb.RoadmapBuilder()
roadmap.construct_square(10)
roadmap.set_obstacles(10)
roadmap.init_roadmap()
roadmap.set_neighbors()

astar = asp.AStar(roadmap)
start = 0
goal = len(astar.roadmap.roadmap)-1

plan = astar.get_plan(start,goal)
idx_cur = goal
while idx_cur != start:
    print(astar.roadmap.roadmap[idx_cur].backpointer)
    print(astar.roadmap.roadmap[idx_cur].coord)
    idx_cur = astar.roadmap.roadmap[idx_cur].backpointer

print(plan)
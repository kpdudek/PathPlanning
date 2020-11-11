#!/usr/bin/env python
""" A first template for a PID controller """
import sys
sys.path.insert(0,'.\\lib\\')

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import RoadmapBuilder
import AStar as asp
import math
import copy

################################################
# Parameters
size = 15
obs_count = 30
obs_len = 4
obs_spread = size


################################################

# Matrix represnetation of the graph where:
# 0 --> Q_free
# 1 --> Q_collision
graph = np.ones(shape=(size,size),dtype=int) 

# Build a roadmap for the graph
roadmap = roadmap_builder.RoadmapBuilder()
roadmap.construct_square(size)
roadmap.set_obstacles(size)
roadmap.init_roadmap()
roadmap.set_neighbors()

# for node in roadmap.roadmap:
#     graph[node.coord[0],node.coord[1]] = 0

a_r = copy.deepcopy(roadmap)
astar = asp.AStar(a_r)
plan = astar.get_plan(0,len(astar.roadmap.roadmap)-1)
            
start_coord = astar.roadmap.roadmap[0].coord
end_coord = astar.roadmap.roadmap[len(astar.roadmap.roadmap)-1].coord

fig1, ax1 = plt.subplots()
print('')
for inode in roadmap.roadmap:
    ax1.plot(inode.coord[0],inode.coord[1],'k.')
    # print('# Neighbors: %d'%(len(inode.neighbors)))
    if len(inode.neighbors) == 0:
        print('Zero neighbor node')
    for idx in inode.neighbors:
        u = roadmap.roadmap[idx].coord[0] - inode.coord[0]
        v = roadmap.roadmap[idx].coord[1] - inode.coord[1]
        ax1.quiver(inode.coord[0],inode.coord[1],u,v,width=.007,color='r',scale=10.0)

### Plot graph, using the nodes
# ax1.matshow(graph,cmap='Greys')
# Display start and end location
ax1.plot(start_coord[0],start_coord[1],'gd',linewidth=2, markersize=14)
ax1.plot(end_coord[0],end_coord[1],'rs',linewidth=2, markersize=14)
ax1.plot(plan[0,:],plan[1,:],lw=3)
ax1.set_aspect('equal', adjustable='box')
# Display figure window
plt.show()


### Alternative method of plotting, using the obstacle list
# graph = np.zeros(shape=(size,size),dtype=int)
# for obs in roadmap.obstacles:
#     for seg in obs:
#         graph[seg[0],seg[1]] = 1
# plt.matshow(graph,cmap='Greys')
# plt.show()
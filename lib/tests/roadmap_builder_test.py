#!/usr/bin/env python
""" Library for creating 2D graphs, and then determining free space and connections to generate a roadmap """

import lib.RoadmapBuilder as rb 

roadmap = rb.RoadmapBuilder()
roadmap.construct_square(10)
roadmap.set_obstacles(10)
roadmap.init_roadmap()
roadmap.set_neighbors()

for inode in roadmap.roadmap:
    print(len(inode.neighbors))
    print(inode.coord)
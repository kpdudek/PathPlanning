#!/usr/bin/env python3

import random, sys, os, math, time
import numpy as np
sys.path.insert(0,'..')
from PerlinNoise import *

from matplotlib.pyplot import imshow, show, colorbar
from matplotlib.colors import LinearSegmentedColormap


def main():
    grid = generate_graph(10)    

    cm = LinearSegmentedColormap.from_list('checkerboard', [(1,1,1),(0,0,0)], N=2)
    imshow(grid,cmap=cm)
    colorbar()
    show()

if __name__ == '__main__':
    main()
#!/usr/bin/env python3

import random, sys, os, math, time
import numpy as np

def Shuffle(tab):
    for e in reversed(range(0,len(tab)-1)):
        index = round(random.random()*(e-1))
        temp  = tab[e]

        tab[e] = tab[index]
        tab[index] = temp

def MakePermutation():
    P = []

    for i in range(0,256):
        P.append(i)

    Shuffle(P)

    for i in range(0,256):
        P.append(P[i])

    return P

def GetConstantVector(v):
    # v is the value from the permutation table
    h = v & 3
    if(h == 0):
        return np.array([[1.0], [1.0]])
    elif(h == 1):
        return np.array([[-1.0], [1.0]])
    elif(h == 2):
        return np.array([[-1.0], [-1.0]])
    else:
        return np.array([[1.0], [-1.0]])


def Fade(t):
    return ((6*t - 15)*t + 10)*t*t*t

def Lerp(t, a1, a2):
    return a1 + t*(a2-a1)

def Perlin2D(x, y, P):
    X = int(x) & 255
    Y = int(y) & 255

    xf = x-int(x)
    yf = y-int(y)

    topRight = np.array([[xf-1.0], [yf-1.0]])
    topLeft = np.array([[xf], [yf-1.0]])
    bottomRight = np.array([[xf-1.0], [yf]])
    bottomLeft = np.array([[xf], [yf]])

    # Select a value in the array for each of the 4 corners
    valueTopRight = P[P[X+1]+Y+1]
    valueTopLeft = P[P[X]+Y+1]
    valueBottomRight = P[P[X+1]+Y]
    valueBottomLeft = P[P[X]+Y]

    dotTopRight = np.sum(topRight*GetConstantVector(valueTopRight))
    dotTopLeft = np.sum(topLeft*GetConstantVector(valueTopLeft))
    dotBottomRight = np.sum(bottomRight*GetConstantVector(valueBottomRight))
    dotBottomLeft = np.sum(bottomLeft*GetConstantVector(valueBottomLeft))

    u = Fade(xf)
    v = Fade(yf)

    return Lerp(u,Lerp(v, dotBottomLeft, dotTopLeft),Lerp(v, dotBottomRight, dotTopRight))

def perlin_noise(size,passes=2,cutoff=1.1):
    grid = np.ones([size,size])
    r,c = grid.shape

    for i in range(0,passes):
        P = MakePermutation()
        for y in range(0,c):
            for x in range(0,r):
                # Noise2D generally returns a value in the range [-1.0, 1.0]
                n = Perlin2D(x*0.1, y*0.1,P)
                
                # Transform the range to [0.0, 1.0], supposing that the range of Noise2D is [-1.0, 1.0]
                n += 1.0
                n /= 2.0
                grid[x][y] += n

    cutoff = float(cutoff)
    passes = float(passes)
    for y in range(0,c):
        for x in range(0,r):
            if grid[x][y] > (cutoff*passes):
                grid[x][y] = 1
            else:
                grid[x][y] = 0

    return grid


def random_noise(size,cutoff=0.5):
    grid = np.zeros([size,size])
    r,c = grid.shape

    for i in range(0,r):
        for j in range(0,c):
            val = random.random()
            if val >= cutoff:
                grid[i,j] = 1

    return grid
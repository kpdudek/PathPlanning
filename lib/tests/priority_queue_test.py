#!/usr/bin/env python
""" A first template for a PID controller """

import sys
sys.path.insert(0,'..')
import priority_queue as pq


### Initializing queue
# key and cost in range(0,5)
print('Initializing queue...')
queue = pq.PriorityQueue()
for vals in range(0,5):
    queue.insert(vals,vals)
# Print queue
for elems in queue.queue:
    print('%3d %3d'%(elems.key,elems.cost))

### Pop element
print('\nExtracting min key...')
min_val,idx = queue.min_extract()
print('Min key: {}, Min cost: {}'.format(min_val,idx))
# Print queue
for elems in queue.queue:
    print('%3d %3d'%(elems.key,elems.cost))

### Check if is element
print('\nChecking if 5 is a key: {}'.format(queue.is_member(5)))
print('Checking if 3 is a key: {}'.format(queue.is_member(3)))

### Insert element
print('\nInserting key=33 & cost=540')
queue.insert(33,540)
# Print queue
for elems in queue.queue:
    print('%3d %3d'%(elems.key,elems.cost))
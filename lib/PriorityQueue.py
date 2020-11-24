#!/usr/bin/env python
""" A first template for a PID controller """

class QueueElement(object):
    def __init__(self):
        self.key = None
        self.cost = None

class PriorityQueue(object):
    def __init__(self):
        self.queue = []
    
    def is_empty(self):
        if len(self.queue) == 0:
            return True
        else:
            return False

    def insert(self,key,cost):
        insert = QueueElement()
        insert.key = key
        insert.cost = cost
        self.queue.append(insert)
    
    def is_member(self,key):
        for member in self.queue:
            if member.key == key:
                return True

    def min_extract(self):
        min_val = None
        min_idx = None

        for member_idx in range(0,len(self.queue)):
            member = self.queue[member_idx]
            
            if min_val == None:
                min_val = member.cost
                min_idx = member_idx
            elif member.cost < min_val:
                min_val = member.cost
                min_idx = member_idx
        
        min_extract = self.queue.pop(min_idx)
        return min_extract.key, min_extract.cost
    
    
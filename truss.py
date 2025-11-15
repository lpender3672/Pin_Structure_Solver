import pygame
import numpy as np

from member import member
from node import node, constraint, force

class truss(object): # made from nodes and members

    def __init__(self, res):
        self.nodes = []
        self.members = []

        self.surface = pygame.Surface(res)
        self.surface.fill((255,255,255))

    def add_node(self, node):
        
        for n in self.nodes:
            if n == node:
                return n
        
        self.nodes.append(node)
        node.display(self.surface)
        return node
    
    def add_member(self, member):
        self.members.append(member)
        member.display(self.surface)

    
    def delete_node(self, node):
        for n in self.nodes:
            if n == node:
                self.nodes.remove(n)
                break


    def delete_member(self, member):
        for m in self.members:
            if m == member:
                self.members.remove(m)
                break

    def delete_force(self, force, nd = None):

        if nd is not None:
            for f in nd.forces:
                if f == force:
                    nd.forces.remove(f)
                    return

        for nd in self.nodes:
            for f in nd.forces:
                if f == force:
                    nd.forces.remove(f)
                    return

    def delete_constraint(self, constraint, nd = None):
        if nd is not None:
            for c in nd.constraints:
                if c == constraint:
                    nd.constraints.remove(c)
                    return
            
        for nd in self.nodes:
            for c in nd.constraints:
                if c == constraint:
                    nd.constraints.remove(c)
                    return

    def update(self):
        pass

    def delete_entity(self, entity):
        
        if isinstance(entity, node):
            # delete all connected members, forces, constraints
            connected_members = [m for m in self.members if m.node1 == entity or m.node2 == entity]
            
            for m in connected_members:
                self.delete_member(m)
            for f in entity.forces:
                self.delete_force(f)
            for c in entity.constraints:
                self.delete_constraint(c)
            # then delete node
            self.delete_node(entity)
            
        elif isinstance(entity, member):
            self.delete_member(entity)
        elif isinstance(entity, force):
            self.delete_force(entity)
        elif isinstance(entity, constraint):
            self.delete_constraint(entity)

    def get_all_entities(self):
        for n in self.nodes:
            yield n
        for m in self.members:
            yield m
        for nd in self.nodes:
            for f in nd.forces:
                yield f
            for c in nd.constraints:
                yield c

    def re_draw(self):
        for member in self.members:
            member.display(self.surface)
        for node in self.nodes:
            node.display(self.surface)
    
    def display(self, display, clear = True, update = True):
        
        if clear:
            self.surface.fill((255,255,255))
            self.re_draw()
            
        display.blit(self.surface, (0,0))

        if update:
            pygame.display.flip()
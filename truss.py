import pygame
import numpy as np


class truss(object): # made from nodes and members

    def __init__(self, res):
        self.nodes = []
        self.members = []

        self.surface = pygame.Surface(res)
        self.surface.fill((255,255,255))


    
    def add_node(self, node):
        self.nodes.append(node)
        node.display(self.surface)
    
    def add_member(self, member):
        self.members.append(member)
        member.display(self.surface)
    

    def update(self):
        pass

    
    def re_draw(self):
        for member in self.members:
            member.display(self.surface)
        for node in self.nodes:
            node.display(self.surface)
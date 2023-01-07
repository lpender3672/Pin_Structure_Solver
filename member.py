import pygame
import numpy as np

class member(object):
    def __init__(self, node1, node2, mass_per_unit_length = 0):
        
        self.node1 = node1
        self.node2 = node2

        self.d = node2.pos - node1.pos
        self.p = self.d.dot(self.node1.pos)

        self.x = (self.node1.x + self.node2.x) / 2
        self.y = (self.node1.y + self.node2.y) / 2

        self.length = np.sqrt( self.d.dot( self.d))

        self.angle = np.arctan2(self.d[1], self.d[0])

        self.mass = self.length * mass_per_unit_length


    def display(self, disp, colour = (0,0,0)):
        pygame.draw.line(disp, colour, self.node1.pos, self.node2.pos, 5)
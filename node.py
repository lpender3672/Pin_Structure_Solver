import pygame
import numpy as np


class node(object):

    def __init__(self, id, x, y, mass = 0):

        self.id = id

        self.x = x
        self.y = y

        self.pos = np.array([x, y])

        self.mass = mass

        self.forces = []

    def __list__(self):
        return self.pos

    
    def __eq__(self, __o: object) -> bool:
        
        if isinstance(__o, node):
            return self.id == __o.id
    
    def display(self, display):
        pygame.draw.circle(display, (0, 0, 0), (self.x, self.y), 5)
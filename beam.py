import pygame
import numpy as np

class beam():
    def __init__(self, x1, y1, x2, y2, mass_per_unit_length):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

        

        self.x = (self.x1 + self.x2) / 2
        self.y = (self.y1 + self.y2) / 2

        self.length = np.sqrt((self.x2 - self.x1)**2 + (self.y2 - self.y1)**2)
        self.angle = np.arctan2(self.y2 - self.y1, self.x2 - self.x1)

        self.mass = self.length * mass_per_unit_length



    def display(self, disp):
        pygame.draw.line(disp, (0, 0, 0), (self.x1, self.y1), (self.x2, self.y2), 5)
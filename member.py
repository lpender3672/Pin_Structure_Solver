import pygame
import numpy as np
from utils import utils

class member(object):
    def __init__(self, node1, node2, mass_per_unit_length = 0):
        
        self.node1 = node1
        self.node2 = node2

        self.d = node2.pos - node1.pos
        self.d = utils.normalise(self.d)
        self.p = self.d.dot(self.node1.pos)

        self.x = (self.node1.x + self.node2.x) / 2
        self.y = (self.node1.y + self.node2.y) / 2

        self.length = np.sqrt( self.d.dot( self.d))

        self.angle = np.arctan2(self.d[1], self.d[0])

        self.mass = self.length * mass_per_unit_length

        self.selected = False

        self.tension = 0  # positive = tension, negative = compression

    def display(self, disp, colour = (0,0,0)):
        if self.selected:
            colour = (255, 0, 0)
        pygame.draw.line(disp, colour, self.node1.pos, self.node2.pos, 5)

    
    def annotate(self, surf, font_size=16):

        mid = 0.5 * (self.node1.pos + self.node2.pos)
        d = self.node2.pos - self.node1.pos
        length = np.linalg.norm(d)
        if length < 1e-9:
            return

        perp = np.array([-d[1], d[0]]) / length

        offset = 20.0   # pixels
        text_pos = mid + perp * offset

        if self.tension >= 0:
            colour = (255, 0, 0)  # tension = red
        else:
            colour = (0, 0, 255)  # compression = blue

        font = pygame.font.SysFont(None, font_size)
        text = f"{self.tension:.2f}"
        text_surf = font.render(text, True, colour)
        
        text_rect = text_surf.get_rect(center=(text_pos[0], text_pos[1]))
        surf.blit(text_surf, text_rect)

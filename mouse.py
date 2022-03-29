
import pygame
import numpy as np

from node import node
from utils import utils

def draw_line_dashed(surface, color, start_pos, end_pos, width = 1, dash_length = 10, exclude_corners = True):

    # convert tuples to numpy arrays
    start_pos = np.array(start_pos)
    end_pos   = np.array(end_pos)

    length = np.linalg.norm(end_pos - start_pos)

    dash_amount = int(length / dash_length)

    dash_knots = np.array([np.linspace(start_pos[i], end_pos[i], dash_amount) for i in range(2)]).transpose()

    return [pg.draw.line(surface, color, tuple(dash_knots[n]), tuple(dash_knots[n+1]), width)
            for n in range(int(exclude_corners), dash_amount - int(exclude_corners), 2)]


class mouse(object):
    
    def __init__(self, pos = None):

        if pos == None:
            self.x, self.y = pygame.mouse.get_pos()
        else:
            self.x = pos[0]
            self.y = pos[1]

        self.cursor_updated = False
    
    def to_node(self, node_id, mass = 0):
        return node(node_id, self.x, self.y, mass = 0)

    def __list__(self):
        return [self.x, self.y]

    def pos(self):
        return np.array([self.x, self.y])
    
    def update(self):
        self.x, self.y = pygame.mouse.get_pos()
        self.cursor_updated = True
    
    
    def snap_line(self, truss):

        

        #closest_node = min(truss.nodes, key = lambda node : np.linalg.norm(node.pos - self.pos()))
        n = truss.nodes[-1].pos


        lines = [[ np.array([1, 0]), n],
                 [ np.array([0, 1]), n]]

        members_connected = [m for m in truss.members if m.node1 == truss.nodes[-1] or m.node2 == truss.nodes[-1]]
        if len(members_connected) == 0:
            return
        for m in members_connected:
            lines.append([m.d, n])
            lines.append([utils.perpendicular(m.d), n])
        
        members_not_connected = [m for m in truss.members if m.node1 != truss.nodes[-1] and m.node2 != truss.nodes[-1]]
        for m in members_not_connected:
            lines.append([m.d, n])

        f = lambda l : utils.line_to_point(l[0], l[1], self.pos())

        closest_line = min(lines, key = f)
        d = utils.normalise(closest_line[0])
        
        pos = n + d * (self.pos() - n).dot(d)
        self.x = pos[0]
        self.y = pos[1] 
        self.cursor_updated = True

        # perpendicular to existing beams

    def snap_point(self, truss):

        if len(truss.nodes) == 0:
            return
        
        f = lambda node : np.linalg.norm(node.pos - self.pos())

        closest_node = min(truss.nodes, key = f)

        if f(closest_node) < 10:  # snapped to node
            self.x = closest_node.x
            self.y = closest_node.y
            self.cursor_updated = True
            return
        
    
        members_not_connected = [m for m in truss.members if m.node1 != truss.nodes[-1] and m.node2 != truss.nodes[-1]]
        
        if len(members_not_connected) == 0:
            return

        lines = []

        for m in members_not_connected:
            lines.append([m.d, m.node1.pos])
            m.display(truss.surface, (255,0,0))
            lines.append([utils.perpendicular(m.d), m.node1.pos])
            lines.append([utils.perpendicular(m.d), m.node2.pos])
                

        g = lambda l : utils.line_to_point(l[0], l[1], self.pos())
        closest_line = min(lines, key = g)

        if g(closest_line) < 20:

            d = utils.normalise(closest_line[0])
            n = closest_line[1]
        
            pos = n + d * (self.pos() - n).dot(d)



            self.x = pos[0]
            self.y = pos[1] 
            self.cursor_updated = True



        

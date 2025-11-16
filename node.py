import pygame
import numpy as np


class force(object):

    def __init__(self, magnitude, angle_radians, start_pos):

        self.FONT = pygame.font.SysFont("Arial", 20)

        self.magnitude = magnitude
        self.angle = angle_radians

        self.text = str(round(magnitude, 2))
        self.active = False
        self.textbox_rect = None
        self.start_pos = start_pos

        self.selected = False

    @property
    def vector(self):
        return np.array([
            self.magnitude * np.cos(self.angle),
            self.magnitude * np.sin(self.angle)
        ])

    def display(self, display, color=(0,0,255), width=5, arrow_size=18, scale=1):

        if self.selected:
            color = (255, 0, 0)

        start = self.start_pos
        end = start + pygame.Vector2(self.vector.tolist()) * scale

        # direction and perpendicular
        direction = (end - start)
        if direction.length() == 0:
            return
        direction = direction.normalize()
        perp = pygame.Vector2(-direction.y, direction.x)

        # arrowhead points
        tip = end
        base = end - direction * arrow_size
        p2 = base + perp * (arrow_size * 0.6)
        p3 = base - perp * (arrow_size * 0.6)

        pygame.draw.line(display, color, start, base, width)
        pygame.draw.polygon(display, color, [tip, p2, p3])

        txtpoint = (start + end) * 0.5 - perp * 20
        text_surface = self.FONT.render(self.text, True, (0,0,0))
        self.textbox_rect = text_surface.get_rect(center=(txtpoint.x, txtpoint.y))
        display.blit(text_surface, self.textbox_rect)



class constraint(object):
    def __init__(self, node, angle_radians, type = 'roller'):
        self.node = node
        self.angle = angle_radians
        self.type = type  # 'fixed', 'roller', 'pinned', etc.

        self.ground_point = node.pos

        self.selected = False

    def display(self, surf, size=20, color=(0, 200, 0), width=2):

        if self.selected:
            color = (255, 0, 0)
        
        self.size = size
        # node position (assumed numpy array-like)
        pos = pygame.Vector2(list(self.node.pos))

        # local basis from angle
        n = pygame.Vector2(np.cos(self.angle), np.sin(self.angle))  # "normal"
        if n.length() == 0:
            n = pygame.Vector2(0, -1)
        t = pygame.Vector2(-n.y, n.x)  # tangent

        self.ground_point = pos - n * size

        # always draw the node as a small circle
        pygame.draw.circle(surf, color, pos, size * 0.15)

        if self.type == 'fixed':
            # Fixed support: block behind node
            h = size * 0.9
            w = size * 0.6

            center = pos - n * (h * 0.5 + size * 0.2)

            v1 = center + t * (w * 0.5) + n * (h * 0.5)
            v2 = center - t * (w * 0.5) + n * (h * 0.5)
            v3 = center - t * (w * 0.5) - n * (h * 0.5)
            v4 = center + t * (w * 0.5) - n * (h * 0.5)

            pygame.draw.polygon(surf, color, [v1, v2, v3, v4], width)

        elif self.type == 'roller':
            # Roller: triangle + little rollers under it
            base_center = pos - n * (size * 0.25)

            p1 = base_center - t * (size * 0.6)
            p2 = base_center + t * (size * 0.6)
            p3 = base_center - n * size

            pygame.draw.polygon(surf, color, [p1, p2, p3], width)

            # rollers:
            r = size * 0.15
            offset = n * (r * 1.5)

            cL = (2 * p1 + p2) / 3 - offset
            cR = (p1 + 2 * p2) / 3 - offset

            pygame.draw.circle(surf, color, cL, r, width)
            pygame.draw.circle(surf, color, cR, r, width)

        else:
            # Default: pinned support (triangle)
            base_center = pos - n * (size * 0.25)

            p1 = base_center - t * (size * 0.6)
            p2 = base_center + t * (size * 0.6)
            p3 = base_center - n * size

            pygame.draw.polygon(surf, color, [p1, p2, p3], width)


class node(object):

    def __init__(self, id, x, y, mass = 0):

        self.id = id

        self.x = x
        self.y = y

        self.pos = np.array([x, y])

        self.mass = mass

        self.forces = []
        self.constraints = []

        self.selected = False

    def __list__(self):
        return self.pos

    
    def __eq__(self, __o: object) -> bool:
        
        if isinstance(__o, node):
            return np.array_equal(self.pos, __o.pos)
    
    def __neq__(self, __o: object) -> bool:
        return not self.__eq__(__o)
    
    def display(self, display, colour = (0,0,0)):
        if self.selected:
            colour = (255, 0, 0)
        pygame.draw.circle(display, colour, (self.x, self.y), 5)
        pygame.draw.circle(display, (255, 255, 255), (self.x, self.y), 3)

        for f in self.forces:
            f.display(display)

        for c in self.constraints:
            c.display(display)
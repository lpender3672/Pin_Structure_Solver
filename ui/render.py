import pygame
import numpy as np

from core import geometry as geom

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SELECTED = (255, 0, 0)
FORCE = (0, 0, 255)
CONSTRAINT = (0, 200, 0)
REACTION = (200, 120, 0)

NODE_RADIUS = 5
MEMBER_WIDTH = 5
CONSTRAINT_SIZE = 20
REACTION_LENGTH = 35

_fonts = {}


def font(size, name = "Arial"):
    if (name, size) not in _fonts:
        _fonts[(name, size)] = pygame.font.SysFont(name, size)
    return _fonts[(name, size)]


def pt(v):
    return (float(v[0]), float(v[1]))


def constraint_ground_point(cstrnt, pos, size = CONSTRAINT_SIZE):
    # where the support marker sits, used for drawing and for hit testing
    return geom.vec(pos) - cstrnt.normal * size


def draw_text(surf, text, pos, colour = BLACK, size = 20):
    surface = font(size).render(text, True, colour)
    surf.blit(surface, surface.get_rect(center = pt(pos)))


def draw_text_lines(surf, lines, size = 20):
    y = 20
    for l in lines:
        surf.blit(font(size).render(l, True, BLACK), (20, y))
        y += 30


def draw_arrow(surf, start, vector, colour, width = 5, arrow_size = 18):
    start = pygame.Vector2(pt(start))
    end = start + pygame.Vector2(pt(vector))

    d = end - start
    if d.length() == 0:
        return None
    d = d.normalize()
    perp = pygame.Vector2(-d.y, d.x)

    base = end - d * arrow_size
    pygame.draw.line(surf, colour, start, base, width)
    pygame.draw.polygon(surf, colour, [end, base + perp * (arrow_size * 0.6),
                                             base - perp * (arrow_size * 0.6)])
    return perp


def draw_force(surf, frce, origin, selected = False, scale = 1):
    colour = SELECTED if selected else FORCE

    perp = draw_arrow(surf, origin, frce.vector * scale, colour)
    if perp is None:
        return

    mid = geom.vec(origin) + frce.vector * scale * 0.5
    draw_text(surf, frce.text, mid - np.array(perp) * 20)


def draw_constraint(surf, cstrnt, pos, selected = False, size = CONSTRAINT_SIZE, width = 2):
    colour = SELECTED if selected else CONSTRAINT

    pos = pygame.Vector2(pt(pos))
    n = pygame.Vector2(pt(cstrnt.normal))
    t = pygame.Vector2(-n.y, n.x)

    pygame.draw.circle(surf, colour, pos, size * 0.15)

    base_center = pos - n * (size * 0.25)
    p1 = base_center - t * (size * 0.6)
    p2 = base_center + t * (size * 0.6)
    p3 = base_center - n * size

    pygame.draw.polygon(surf, colour, [p1, p2, p3], width)

    if cstrnt.type == 'roller':
        r = size * 0.15
        offset = n * (r * 1.5)
        pygame.draw.circle(surf, colour, (2 * p1 + p2) / 3 - offset, r, width)
        pygame.draw.circle(surf, colour, (p1 + 2 * p2) / 3 - offset, r, width)


def draw_node(surf, nd, selected = False):
    colour = SELECTED if selected else BLACK

    pygame.draw.circle(surf, colour, pt(nd.pos), NODE_RADIUS)
    pygame.draw.circle(surf, WHITE, pt(nd.pos), NODE_RADIUS - 2)


def draw_member(surf, mber, selected = False):
    colour = SELECTED if selected else BLACK
    pygame.draw.line(surf, colour, pt(mber.node1.pos), pt(mber.node2.pos), MEMBER_WIDTH)


def annotate_member(surf, mber, tension, size = 16):
    perp = geom.perpendicular(mber.direction)
    colour = SELECTED if tension >= 0 else FORCE  # tension red, compression blue
    draw_text(surf, f"{tension:.2f}", mber.midpoint + perp * 20, colour, size)


def annotate_reaction(surf, rctn, size = 16):
    if abs(rctn.magnitude) < 1e-9:
        return

    d = rctn.direction * np.sign(rctn.magnitude)
    start = geom.vec(rctn.node.pos) - d * (CONSTRAINT_SIZE + REACTION_LENGTH)

    draw_arrow(surf, start, d * REACTION_LENGTH, REACTION, width = 3, arrow_size = 10)
    draw_text(surf, f"{abs(rctn.magnitude):.2f}", start - d * 14, REACTION, size)


class renderer(object):

    def __init__(self, res):
        self.surface = pygame.Surface(res)
        self.surface.fill(WHITE)

        self.solution = None
        self.solution_revision = -1

    def set_solution(self, sol, revision):
        self.solution = sol
        self.solution_revision = revision

    def annotations_for(self, trss):
        # any edit bumps the revision, which retires the previous solution
        if self.solution is None or self.solution_revision != trss.revision:
            return None
        return self.solution if self.solution.ok else None

    def re_draw(self, trss, selected = ()):
        sol = self.annotations_for(trss)

        for m in trss.members:
            draw_member(self.surface, m, m in selected)

        if sol is not None:
            for m in trss.members:
                annotate_member(self.surface, m, sol.tensions[m])
            for r in sol.reactions:
                annotate_reaction(self.surface, r)

        for nd in trss.nodes:
            draw_node(self.surface, nd, nd in selected)

            for f in nd.forces:
                draw_force(self.surface, f, nd.pos, f in selected)
            for c in nd.constraints:
                draw_constraint(self.surface, c, nd.pos, c in selected)

    def draw(self, display, trss, selected = (), clear = True, update = True):
        if clear:
            self.surface.fill(WHITE)
            self.re_draw(trss, selected)

        display.blit(self.surface, (0, 0))

        if update:
            pygame.display.flip()

import pygame
import numpy as np

from member import member
from node import node, constraint, force

from utils import utils

class truss(object): # made from nodes and members

    def __init__(self, res):
        self.nodes = []
        self.members = []

        self.annotate = False

        self.surface = pygame.Surface(res)
        self.surface.fill((255,255,255))

    def add_node(self, nd):
        if not isinstance(nd, node):
            return None
        
        self.annotate = False
        
        for n in self.nodes:
            if n == nd:
                return n

        self.nodes.append(nd)
        nd.display(self.surface)
        return nd

    def add_member(self, mber):
        if not isinstance(mber, member):
            return None
        
        self.annotate = False

        for m in self.members:
            if m == mber:
                return m

        self.members.append(mber)
        mber.display(self.surface)

        return mber

    def delete_node(self, nd):

        for n in self.nodes:
            if n == nd:
                self.nodes.remove(n)
                self.annotate = False
                break


    def delete_member(self, mber):

        for m in self.members:
            if m == mber:
                self.members.remove(m)
                self.annotate = False
                break

    def delete_force(self, frce, nd = None):
        self.annotate = False

        if nd is not None:
            for f in nd.forces:
                if f == frce:
                    nd.forces.remove(f)
                    return

        for nd in self.nodes:
            for f in nd.forces:
                if f == frce:
                    nd.forces.remove(f)
                    return

    def delete_constraint(self, cstrnt, nd = None):
        self.annotate = False

        if nd is not None:
            for c in nd.constraints:
                if c == cstrnt:
                    nd.constraints.remove(c)
                    return
            
        for nd in self.nodes:
            for c in nd.constraints:
                if c == cstrnt:
                    nd.constraints.remove(c)
                    return

    def update(self):
        pass

    def delete_entity(self, entity):
        self.annotate = False
        
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
        for mber in self.members:
            mber.display(self.surface)

        if self.annotate:
            for mber in self.members:
                mber.annotate(self.surface)

        for nd in self.nodes:
            nd.display(self.surface)
    
    def display(self, display, clear = True, update = True, annotate = False):
        
        if clear:
            self.surface.fill((255,255,255))
            self.re_draw()

        if annotate:
            self.annotate()

        display.blit(self.surface, (0,0))

        if update:
            pygame.display.flip()


    def solve_forces(self):

        # each node has vertical and horizontal equilibrium equations
        # the number of unknowns depends on constraints
        unknowns = []
        for m in self.members:
            unknowns.append(m)

        num_unknowns = len(unknowns)
        # constraint reactions
        for nd in self.nodes:
            for c in nd.constraints:
                # roller or pinned
                cdir = [np.cos(c.angle), np.sin(c.angle)]
                unknowns.append((nd.id, *cdir))
                num_unknowns += 1

                if c.type == 'fixed':
                    perp_dir = [-cdir[1], cdir[0]]
                    unknowns.append((nd.id, *perp_dir))
                    num_unknowns += 1

        num_equations = 2 * len(self.nodes)

        A = np.zeros((num_equations, num_unknowns))
        b = np.zeros(num_equations)

        unknown_indices = {u: i for i, u in enumerate(unknowns)}

        for row, nd in enumerate(self.nodes):
            row_x = 2 * row
            row_y = 2 * row + 1

            for u, col_index in unknown_indices.items():

                if u in self.members:
                    m = u
                    if m.node1 == nd or m.node2 == nd:
                        direction = utils.normalise(m.node2.pos - m.node1.pos)
                        if m.node1 == nd:
                            A[row_x, col_index] += direction[0]
                            A[row_y, col_index] += direction[1]
                        else:
                            A[row_x, col_index] -= direction[0]
                            A[row_y, col_index] -= direction[1]

                # reactions:
                if isinstance(u, tuple):
                    ndid, *ndir = u
                    if ndid == nd.id:
                        A[row_x, col_index] = ndir[0]
                        A[row_y, col_index] = ndir[1]

            for f in nd.forces:
                b[row_x] -= f.magnitude * np.cos(f.angle)
                b[row_y] -= f.magnitude * np.sin(f.angle)

        x, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)

        if rank < num_equations:
            print("Geometrically unstable / mechanism (equilibrium equations dependent).")
            return

        if num_unknowns > num_equations and rank == num_equations:
            print("Statically indeterminate: more unknowns than independent equations.")
            return

        if np.any(residuals > 1e-5):
            print("Warning: Significant residuals detected, solution may be inaccurate.")
            return
        
        for u, col_index in unknown_indices.items():
            if u in self.members:
                m = u
                m.tension = x[col_index]

            elif isinstance(u, tuple):
                ndid, *ndir = u
                reaction_force = x[col_index]

        # we can now annotate the members with their forces
        self.annotate = True


    def solve_displacements(self):
        pass

        # be nice if we could draw displaced shape too



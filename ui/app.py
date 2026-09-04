import pygame

from core import geometry as geom
from core.model import node, member, force, constraint, truss
from core.solver import solve_forces

from ui import render
from ui.mouse import mouse


class runtime(object):

    help_text = [
        "H: Show help",
        "SPACE: Toggle drawing mode",
        "SHIFT (while drawing): Constrain to straight lines",
        "F: Enter force drawing mode",
        "C: Enter constraint drawing mode",
        "CTRL: Enter selection mode",
        "A (while in selection mode): Select all",
        "DELETE / BACKSPACE: Delete selected entities",
        "S: Solve truss"
    ]

    def __init__(self, res):

        self.disp = pygame.display.set_mode(res)

        self.crashed = False
        self.straight = False

        self.drawing_truss = False
        self.drawing_forces = False
        self.drawing_constraints = False

        self.show_help = True
        self.show_solver_out = False
        self.solver_out = ""

        self.selection_mode = False
        self.selections = []
        self.draw_from_node = None

        self.truss = truss()
        self.renderer = render.renderer(res)

    def draw_truss(self, clear = True, update = True):
        self.renderer.draw(self.disp, self.truss, self.selections, clear, update)

    def draw_node_to_cursor(self, nd, cursor):
        if nd is None:
            nd = self.truss.nodes[-1]

        pygame.draw.line(self.disp, (0, 0, 0), render.pt(nd.pos), render.pt(cursor.pos()), 5)


    def draw_force_from_cursor(self, nd, cursor):

        if nd is None:
            return

        vec = cursor.pos() - nd.pos
        if geom.norm(vec) == 0:
            return

        preview_force = force(vec)
        render.draw_force(self.disp, preview_force, nd.pos)

        return preview_force

    def draw_constraint_from_cursor(self, nd, cursor):
        if nd is None:
            return

        normal = geom.try_normalise(cursor.pos() - nd.pos)
        if normal is None:
            return

        preview_constraint = constraint(normal)
        render.draw_constraint(self.disp, preview_constraint, nd.pos)

        return preview_constraint


    def run(self):

        self.disp.fill((255, 255, 255))
        pygame.display.flip()

        cursor = mouse(self.disp)

        while not self.crashed:

            events = pygame.event.get()

            for e in events:

                if e.type == pygame.QUIT:
                    self.crashed = True
                    break

                elif e.type == pygame.KEYDOWN:
                    self.show_solver_out = False

                    if e.key == pygame.K_ESCAPE:
                        self.crashed = True
                        break

                    elif e.key == pygame.K_h:
                        self.show_help = True
                        self.disp.fill((155, 155, 155))
                        self.draw_truss(True, False)
                        self.display_lines(self.help_text)
                        pygame.display.flip()
                        continue

                    elif e.key == pygame.K_LSHIFT and self.drawing_truss:
                        self.straight = True

                        self.disp.fill((255, 255, 255))

                        cursor.snap_line(self.truss, self.draw_from_node)
                        cursor.snap_point(self.truss, self.draw_from_node)

                        self.draw_truss(clear = False, update = False)
                        self.draw_node_to_cursor(self.draw_from_node, cursor)
                        pygame.display.flip()


                    elif e.key == pygame.K_SPACE:
                        self.drawing_truss = not self.drawing_truss
                        self.straight = False

                        self.disp.fill((255, 255, 255))
                        cursor.update()

                        if self.drawing_truss and len(self.truss.nodes) > 0:

                            self.draw_truss(False, False)
                            cursor.snap_point(self.truss, self.draw_from_node)
                            self.draw_node_to_cursor(self.draw_from_node, cursor)
                        else:
                            self.draw_truss(False, False)

                        if self.show_help:
                            self.display_lines(self.help_text)
                        elif self.show_solver_out:
                            self.display_lines([self.solver_out])

                        pygame.display.flip()

                    elif e.key == pygame.K_f:
                        self.drawing_forces = True
                        self.handle_mouse_motion(cursor)

                    elif e.key == pygame.K_c:
                        self.drawing_constraints = True
                        self.handle_mouse_motion(cursor)

                    elif e.key == pygame.K_LCTRL:
                        self.selection_mode = True

                    elif e.key == pygame.K_a and self.selection_mode:
                        # select all
                        self.selections = list(self.truss.get_all_entities())

                    elif e.key == pygame.K_DELETE or e.key == pygame.K_BACKSPACE:
                        for entity in list(self.selections):
                            self.truss.delete_entity(entity)

                        self.selections = []
                        self.draw_from_node = None

                        self.disp.fill((255, 255, 255))
                        self.draw_truss(True, True)

                    elif e.key == pygame.K_s:
                        self.solve()

                elif e.type == pygame.KEYUP:
                    self.draw_truss(True, False)

                    if e.key == pygame.K_h:
                        self.show_help = False

                    elif e.key == pygame.K_LSHIFT:
                        self.straight = False

                    elif e.key == pygame.K_f:
                        self.drawing_forces = False
                        self.draw_truss()

                    elif e.key == pygame.K_c:
                        self.drawing_constraints = False
                        self.draw_truss()

                    elif e.key == pygame.K_LCTRL:
                        self.selection_mode = False

                    self.drawing_truss_update(cursor)

                    if self.show_help:
                        self.display_lines(self.help_text)
                    elif self.show_solver_out:
                        self.display_lines([self.solver_out])
                    pygame.display.flip()

                elif e.type == pygame.MOUSEMOTION:
                    self.handle_mouse_motion(cursor)


                elif e.type == pygame.MOUSEBUTTONDOWN:

                    if e.button == 1:
                        self.handle_left_click(e, cursor)

                    elif e.button == 3: # right click
                        pass

        pygame.quit()
        exit()

    def solve(self):

        sol = solve_forces(self.truss)

        self.solver_out = sol.message
        self.show_solver_out = not sol.ok
        self.renderer.set_solution(sol, self.truss.revision)

        self.draw_truss(True, False)
        if self.show_solver_out:
            self.display_lines([self.solver_out])
        pygame.display.flip()

    def drawing_truss_update(self, cursor):

        if self.drawing_truss and len(self.truss.nodes) > 0:

            if self.straight:
                cursor.snap_line(self.truss, self.draw_from_node)

            self.draw_truss(clear = True, update = False)
            cursor.snap_point(self.truss, self.draw_from_node)
            self.draw_node_to_cursor(self.draw_from_node, cursor)


    def handle_mouse_motion(self, cursor):
        cursor.update()

        # draw line from previous node to mouse position
        self.disp.fill((255, 255, 255))

        if self.drawing_truss and len(self.truss.nodes) > 0:
            self.drawing_truss_update(cursor)

        elif self.drawing_forces:

            closest_node = cursor.get_nearest_node(self.truss)
            if closest_node is None:
                self.draw_truss(False, update = False)
                return
            # snap line not point
            self.draw_truss(clear = False, update = False)
            cursor.snap_point(self.truss, closest_node)
            self.draw_force_from_cursor(closest_node, cursor)

        elif self.drawing_constraints:
            closest_node = cursor.get_nearest_node(self.truss)
            if closest_node is None:
                self.draw_truss(False, update = False)
                return
            # snap line not point
            self.draw_truss(clear = False, update = False)
            cursor.snap_point(self.truss, closest_node)
            self.draw_constraint_from_cursor(closest_node, cursor)

        else:
            self.draw_truss(False, False)

        if self.show_help:
            self.display_lines(self.help_text)
        if self.show_solver_out:
            self.display_lines([self.solver_out])

        pygame.display.update()

    def handle_left_click(self, e, cursor):

        update = False

        if self.drawing_truss and not self.selection_mode: # left click

            if (self.draw_from_node is None) and (len(self.truss.nodes) > 0):
                self.draw_from_node = self.truss.nodes[-1]

            new_node = self.truss.add_node(cursor.to_node())
            self.select(new_node)

            if self.draw_from_node is not None and self.draw_from_node is not new_node:

                self.truss.add_member(member(self.draw_from_node, new_node, 1))

                self.deselect(self.draw_from_node)

                update = True

            self.draw_from_node = new_node

        elif self.drawing_forces:
            closest_node = cursor.get_nearest_node(self.truss)
            cursor.snap_point(self.truss, closest_node)
            fc = self.draw_force_from_cursor(closest_node, cursor)
            if fc is None:
                return
            self.truss.add_force(fc, closest_node)
            update = True

        elif self.drawing_constraints:
            closest_node = cursor.get_nearest_node(self.truss)
            cursor.snap_point(self.truss, closest_node)
            con = self.draw_constraint_from_cursor(closest_node, cursor)
            if con is None:
                return
            self.truss.add_constraint(con, closest_node)
            update = True

        elif self.selection_mode:
            # if hovering over something
            # append to selection array

            for entity in cursor.get_hover_entities(self.truss):
                if entity in self.selections:
                    self.deselect(entity)
                else:
                    self.select(entity)

                    if isinstance(entity, node):
                        self.draw_from_node = entity

                update = True

        if update:
            self.draw_truss(True, False)
            if self.show_help:
                self.display_lines(self.help_text)
            elif self.show_solver_out:
                self.display_lines([self.solver_out])
            pygame.display.flip()

    def select(self, entity):
        if entity not in self.selections:
            self.selections.append(entity)

    def deselect(self, entity):
        if entity in self.selections:
            self.selections.remove(entity)

    def display_lines(self, lines):
        render.draw_text_lines(self.disp, lines)


def main():

    pygame.init()

    app = runtime((1600, 800))
    app.run()

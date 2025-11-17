import pygame
import numpy as np

from member import member
from mouse import mouse
from truss import truss
from node import node, force, constraint

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

        self.selection_mode = False
        self.selections = []
        self.draw_from_node = None

        self.truss =  truss(res)

    def draw_node_to_cursor(self, node, cursor):
        if node is None:
            node = self.truss.nodes[-1]

        pygame.draw.line(self.disp, (0, 0, 0), node.pos, cursor.pos(), 5)


    def draw_force_from_cursor(self, node, cursor):

        if node is None:
            return

        start = pygame.Vector2(list(node.pos))
        end = pygame.Vector2(list(cursor.pos()))
        vec = end - start
        if vec.length() == 0:
            return
        
        angle = np.arctan2(vec.y, vec.x)
        magnitude = vec.length()  # pixels → temporary magnitude

        preview_force = force(magnitude=magnitude, angle_radians=angle, start_pos=start)
        preview_force.display(self.disp)

        return preview_force

    def draw_constraint_from_cursor(self, node, cursor):
        if node is None:
            return

        start = pygame.Vector2(list(node.pos))
        end = pygame.Vector2(list(cursor.pos()))
        vec = end - start
        if vec.length() == 0:
            return
        
        angle = np.arctan2(vec.y, vec.x)

        preview_constraint = constraint(node=node, angle_radians=angle)
        preview_constraint.display(self.disp)

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
                        self.truss.display(self.disp, True, False)
                        self.display_lines(self.help_text)
                        pygame.display.flip()
                        continue

                    elif e.key == pygame.K_LSHIFT and self.drawing_truss:
                        self.straight = True

                        self.disp.fill((255, 255, 255))

                        cursor.snap_line(self.truss, self.draw_from_node)
                        cursor.snap_point(self.truss, self.draw_from_node)

                        self.truss.display(self.disp, clear=False, update=False)
                        self.draw_node_to_cursor(self.draw_from_node, cursor)
                        pygame.display.flip()
                        
                            
                    elif e.key == pygame.K_SPACE:
                        self.drawing_truss = not self.drawing_truss
                        self.straight = False

                        self.disp.fill((255, 255, 255))
                        cursor.update()

                        if self.drawing_truss and len(self.truss.nodes) > 0:
                            
                            self.truss.display(self.disp, False, False)
                            cursor.snap_point(self.truss, self.draw_from_node)
                            self.draw_node_to_cursor(self.draw_from_node, cursor)
                        else:
                            self.truss.display(self.disp, False, False)

                        if self.show_help:
                            self.display_lines(self.help_text)
                        elif self.show_solver_out:
                            self.display_lines([self.truss.solver_out])

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
                        self.selections = []
                        for entity in self.truss.get_all_entities():
                            entity.selected = True
                            self.selections.append(entity)

                    elif e.key == pygame.K_DELETE or e.key == pygame.K_BACKSPACE:
                        for entity in self.selections:
                            self.truss.delete_entity(entity)
                        
                        self.selections = []
                        self.draw_from_node = None

                        self.disp.fill((255, 255, 255))
                        self.truss.display(self.disp, True, True)

                    elif e.key == pygame.K_s:
                        self.show_solver_out = not self.truss.solve_forces()
                        self.truss.display(self.disp, True, False)
                        if self.show_solver_out:
                            self.display_lines([self.truss.solver_out])
                        pygame.display.flip()

                elif e.type == pygame.KEYUP:
                    self.truss.display(self.disp, True, False)
                    
                    if e.key == pygame.K_h:
                        self.show_help = False

                    elif e.key == pygame.K_LSHIFT:
                        self.straight = False
                        #self.truss.display(self.disp)
                    
                    elif e.key == pygame.K_f:
                        self.drawing_forces = False
                        self.truss.display(self.disp)

                    elif e.key == pygame.K_c:
                        self.drawing_constraints = False
                        self.truss.display(self.disp)

                    elif e.key == pygame.K_LCTRL:
                        self.selection_mode = False
                    
                    self.drawing_truss_update(cursor)

                    if self.show_help:
                        self.display_lines(self.help_text)
                    elif self.show_solver_out:
                        self.display_lines([self.truss.solver_out])
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
    
    def drawing_truss_update(self, cursor):

        if self.drawing_truss and len(self.truss.nodes) > 0:
            
            if self.straight:
                cursor.snap_line(self.truss, self.draw_from_node)

            self.truss.display(self.disp, clear=True, update=False)
            cursor.snap_point(self.truss, self.draw_from_node)
            self.draw_node_to_cursor(self.draw_from_node, cursor)


    def handle_mouse_motion(self, cursor):
        cursor.update()
        
        # draw line from previous node to mouse position
        self.disp.fill((255, 255, 255))
        self.drawing_truss_update(cursor)

        if self.drawing_truss and len(self.truss.nodes) > 0:
            
            if self.straight:
                cursor.snap_line(self.truss, self.draw_from_node)

            self.truss.display(self.disp, clear=True, update=False)
            cursor.snap_point(self.truss, self.draw_from_node)
            self.draw_node_to_cursor(self.draw_from_node, cursor)

        elif self.drawing_forces:

            closest_node = cursor.get_nearest_node(self.truss)
            if closest_node is None:
                self.truss.display(self.disp, False, update=False)
                return
            # snap line not point
            self.truss.display(self.disp, clear=False, update=False)
            cursor.snap_point(self.truss, closest_node)
            self.draw_force_from_cursor(closest_node, cursor)

        elif self.drawing_constraints:
            closest_node = cursor.get_nearest_node(self.truss)
            if closest_node is None:
                self.truss.display(self.disp, False, update=False)
                return
            # snap line not point
            self.truss.display(self.disp, clear=False, update=False)
            cursor.snap_point(self.truss, closest_node)
            self.draw_constraint_from_cursor(closest_node, cursor)

        else:
            self.truss.display(self.disp, False, False)

        if self.show_help:
            self.display_lines(self.help_text)
        if self.show_solver_out:
            self.display_lines([self.truss.solver_out])
            
        pygame.display.update()

    def handle_left_click(self, e, cursor):

        update = False

        if self.drawing_truss and not self.selection_mode: # left click
            
            if (self.draw_from_node is None) and (len(self.truss.nodes) > 0):
                self.draw_from_node = self.truss.nodes[-1]

            new_node = self.truss.add_node( cursor.to_node( len(self.truss.nodes) ))
            new_node.selected = True # select new node
            self.selections.append(new_node)

            if len(self.truss.nodes) > 1:

                mem = member(self.draw_from_node, new_node, 1)

                self.truss.add_member(mem)

                # deselect previous node
                for s in self.selections:
                    if s == self.draw_from_node:
                        s.selected = False
                        self.selections.remove(s)

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
                    entity.selected = False
                    self.selections.remove(entity)
                else:
                    entity.selected = True
                    self.selections.append(entity)

                    if isinstance(entity, node):
                        self.draw_from_node = entity
                    
                update = True

        if update:
            self.truss.display(self.disp, True, False)
            if self.show_help:
                self.display_lines(self.help_text)
            elif self.show_solver_out:
                self.display_lines([self.truss.solver_out])
            pygame.display.flip()


    def display_lines(self, lines):
        font = pygame.font.SysFont("Arial", 20)
        y = 20
        for line in lines:
            text_surface = font.render(line, True, (0, 0, 0))
            self.disp.blit(text_surface, (20, y))
            y += 30


def main():

    pygame.init()

    app = runtime((1600, 800))
    app.run()

if __name__ == '__main__':
    main()
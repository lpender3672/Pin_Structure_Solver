import pygame
import numpy as np

from member import member
from mouse import mouse
from truss import truss
from node import node

class runtime(object):

    def __init__(self, res):

        self.disp = pygame.display.set_mode(res)
        

        self.crashed = False

        self.straight = False

        self.drawing_truss = False
        self.drawing_forces = False
        self.drawing_fixtures = False

        self.selection_mode = False
        self.selections = []
        self.draw_from_node = None

        self.truss =  truss(res)

    def draw_node_to_cursor(self, node, cursor):
        if node is None:
            node = self.truss.nodes[-1]
        
        pygame.draw.line(self.disp, (0, 0, 0), node.pos, cursor.pos(), 5)

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

                    if e.key == pygame.K_ESCAPE:
                        self.crashed = True
                        break

                    if e.key == pygame.K_LSHIFT and self.drawing_truss and len(self.truss.nodes) > 0:
                        self.straight = True

                        self.disp.fill((255, 255, 255))

                        cursor.snap_line(self.truss, self.draw_from_node)
                        cursor.snap_point(self.truss, self.draw_from_node)

                        self.truss.display(self.disp, clear=False, update=False)
                        self.draw_node_to_cursor(self.draw_from_node, cursor)
                        pygame.display.flip()
                        
                            
                    if e.key == pygame.K_SPACE:
                        self.drawing_truss = not self.drawing_truss
                        self.straight = False

                        self.disp.fill((255, 255, 255))
                        cursor.update()

                        if self.drawing_truss and len(self.truss.nodes) > 0:
                            
                            self.truss.display(self.disp, False)
                            cursor.snap_point(self.truss, self.draw_from_node)
                            self.draw_node_to_cursor(self.draw_from_node, cursor)
                        else:
                            self.truss.display(self.disp, False)

                        pygame.display.update()

                    if e.key == pygame.K_f:
                        self.drawing_forces = True

                    if e.key == pygame.K_LCTRL:
                        self.selection_mode = True

                        
                elif e.type == pygame.KEYUP:
                    if e.key == pygame.K_LSHIFT:
                        self.straight = False
                        #self.truss.display(self.disp)
                    
                    if e.key == pygame.K_f:
                        self.drawing_forces = False
                        self.truss.display(self.disp)

                    if e.key == pygame.K_LCTRL:
                        self.selection_mode = False
                        self.truss.display(self.disp)

                elif e.type == pygame.MOUSEMOTION:
                    cursor.update()
                    # draw line from previous node to mouse position
                    self.disp.fill((255, 255, 255))

                    if self.drawing_truss and len(self.truss.nodes) > 0:
                        
                        if self.straight:
                            cursor.snap_line(self.truss, self.draw_from_node)
                        
                        self.truss.display(self.disp, clear=False, update=False)
                        cursor.snap_point(self.truss, self.draw_from_node)
                        self.draw_node_to_cursor(self.draw_from_node, cursor)

                    else:
                        
                        self.truss.display(self.disp, False)

                    pygame.display.update()

     
                    
                elif e.type == pygame.MOUSEBUTTONDOWN:

                    if e.button == 1:
                    
                        if self.drawing_truss: # left click
                            self.truss.add_node( cursor.to_node( len(self.truss.nodes) ))

                            if self.draw_from_node is None:
                                self.draw_from_node = self.truss.nodes[-1]
                                self.draw_from_node.selected = True

                            if len(self.truss.nodes) > 1:

                                n1, n2 = self.truss.nodes[-1], self.draw_from_node

                                mem = member(n1, n2, 1)

                                self.truss.add_member(mem)

                                self.draw_from_node.selected = False # deselect previous node
                                self.draw_from_node = self.truss.nodes[-1]
                                self.draw_from_node.selected = True # select new node

                                self.truss.re_draw()
                                self.truss.display(self.disp)
                        
                        if self.selection_mode:
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
                                    
                                self.disp.fill((255, 255, 255))
                                self.truss.re_draw()
                                self.truss.display(self.disp)
                                pygame.display.flip()
                                break


                    elif e.button == 3: # right click
                        pass
                

        pygame.quit()
        exit()
                
                

def main():

    pygame.init()

    app = runtime((2000, 1000))
    app.run()

if __name__ == '__main__':
    main()
import pygame
import numpy as np
from sympy import false

from member import member
from mouse import mouse
from truss import truss
class runtime(object):

    def __init__(self, res):

        self.disp = pygame.display.set_mode(res)
        

        self.crashed = False

        self.straight = False

        self.drawing_truss = False
        self.drawing_forces = False
        self.drawing_fixtures = False



        self.truss =  truss(res)

    def draw_last_node_to_cursor(self, cursor):
        if len(self.truss.nodes) == 0 or not self.drawing_truss:
            return
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

                    if e.key == pygame.K_LSHIFT and self.drawing_truss:
                        self.straight = True

                        self.disp.fill((255, 255, 255))

                        cursor.snap_line(self.truss)
                        self.truss.display(self.disp, clear=False, update=False)
                        cursor.snap_point(self.truss)

                        self.draw_last_node_to_cursor(cursor)

                        pygame.display.flip()
                        
                            
                    if e.key == pygame.K_SPACE:
                        self.drawing_truss = True

                        if len(self.truss.nodes) > 0:
                            self.disp.fill((255, 255, 255))

                            cursor.snap_point(self.truss)

                            self.truss.display(self.disp, False)
                            self.draw_last_node_to_cursor(cursor)
                    
                    if e.key == pygame.K_f:
                        self.drawing_forces = True

                    if e.key == pygame.K_LCTRL:
                        self.drawing_fixtures = True

                        
                elif e.type == pygame.KEYUP:
                    if e.key == pygame.K_LSHIFT:
                        self.straight = False
                        self.truss.display(self.disp)

                    
                    if e.key == pygame.K_SPACE:
                        self.drawing = False
                        self.truss.display(self.disp)

                    
                    if e.key == pygame.K_f:
                        self.drawing_forces = False
                        self.truss.display(self.disp)

                    if e.key == pygame.K_LCTRL:
                        self.drawing_fixtures = False
                        self.truss.display(self.disp)

                        

                elif e.type == pygame.MOUSEMOTION:

                    cursor.update()

                    # draw line from previous node to mouse position

                    
                        
                    self.disp.fill((255, 255, 255))

                    if self.drawing_truss and len(self.truss.nodes) > 0:
                        
                        if self.straight:
                            cursor.snap_line(self.truss)
                        
                        self.truss.display(self.disp, clear=False, update=False)

                        cursor.snap_point(self.truss)

                        # draw line from previous node to mouse position
                        self.draw_last_node_to_cursor(cursor)

                        pygame.display.update()

                    else:
                        
                        self.truss.display(self.disp, False)

     
                    
                elif e.type == pygame.MOUSEBUTTONDOWN:

                    if e.button == 1 and self.drawing_truss: # left click
                        new_node = cursor.to_node( len(self.truss.nodes) )
                        if len(self.truss.nodes) > 0:
                            old_node = self.truss.nodes[-1]

                        for n in self.truss.nodes:
                            if np.allclose(n.pos, new_node.pos):
                                new_node = n
                                break
                        else:
                            self.truss.add_node(new_node)

                        if len(self.truss.nodes) > 1:

                            mem = member(old_node, new_node, 1)

                            self.truss.add_member(mem)

                            self.truss.display(self.disp)

                

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
import pygame
import numpy as np

from member import member
from mouse import mouse
from truss import truss
class runtime(object):

    def __init__(self, res):

        self.disp = pygame.display.set_mode(res)
        

        self.crashed = False

        self.straight = False
        self.drawing = False


        self.truss =  truss(res)

    def draw_closest_node_to_cursor(self, cursor):
        self.disp.fill((255,255,255))
        self.disp.blit(self.truss.surface, (0,0))
        #node = min(self.truss.nodes, key = lambda node : np.linalg.norm(node.pos - cursor.pos()))
        node = self.truss.nodes[-1]
        pygame.draw.line(self.disp, (0, 0, 0), node.pos, cursor.pos(), 5)
        pygame.display.flip()

    def run(self):

        self.disp.fill((255, 255, 255))
        pygame.display.flip()

        cursor = mouse()

        while not self.crashed:

            events = pygame.event.get()

            

            for e in events:

                if e.type == pygame.QUIT:
                    self.crashed = True
                    break
    
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_LSHIFT and self.drawing and len(self.truss.nodes) > 0:
                        self.straight = True
                        self.straight_pos = pygame.mouse.get_pos()

                        cursor.snap_line(self.truss)
                        cursor.snap_point(self.truss)
                        self.draw_closest_node_to_cursor(cursor)
                        
                            
                    if e.key == pygame.K_SPACE:
                        self.drawing = True

                        if len(self.truss.nodes) > 0:
                            self.draw_closest_node_to_cursor(cursor)
                        
                elif e.type == pygame.KEYUP:
                    if e.key == pygame.K_LSHIFT:
                        self.straight = False

                        self.disp.fill((255,255,255))
                        self.disp.blit(self.truss.surface, (0,0))
                        pygame.display.flip()

                    
                    if e.key == pygame.K_SPACE:
                        self.drawing = False

                        self.disp.fill((255,255,255))
                        self.disp.blit(self.truss.surface, (0,0))
                        pygame.display.flip()

                elif e.type == pygame.MOUSEMOTION:

                    cursor.update()

                    # draw line from previous node to mouse position

                    
                        
                    

                    if self.drawing and len(self.truss.nodes) > 0:

                        cursor.snap_point(self.truss)

                        if self.straight:
                            cursor.snap_line(self.truss)

                        # draw line from previous node to mouse position
                        self.draw_closest_node_to_cursor(cursor)

                    else:
                        self.disp.fill((255,255,255))
                        self.disp.blit(self.truss.surface, (0,0))
                        pygame.display.flip()
     

                    
                elif e.type == pygame.MOUSEBUTTONDOWN:

                    if e.button == 1 and self.drawing: # left click
                        self.truss.add_node( cursor.to_node( len(self.truss.nodes) ))
                    

                        if len(self.truss.nodes) > 1:

                            n1, n2 = self.truss.nodes[-1], self.truss.nodes[-2]

                            mem = member(n1, n2, 1)

                            self.truss.add_member(mem)

                            self.disp.fill((255,255,255))
                            self.disp.blit(self.truss.surface, (0,0))
                            pygame.display.flip()

                

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
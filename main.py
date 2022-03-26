import pygame
import numpy as np


class runtime(object):

    def __init__(self, res):

        self.disp = pygame.display.set_mode(res)
        self.crashed = False

    def run(self):

        while not self.crashed:

            self.disp.fill((0, 0, 0))

            events = pygame.event.get()

            for e in events:
    
                if e.type == pygame.KEYDOWN:

                    if e.key == pygame.K_SPACE:
                        print("space pressed")

                if e.type == pygame.QUIT:
                    self.crashed = True
                    break
            
            pygame.display.flip()
    
        pygame.quit()
        exit()
                
                



def main():

    pygame.init()

    app = runtime((800, 400))
    app.run()

if __name__ == '__main__':
    main()
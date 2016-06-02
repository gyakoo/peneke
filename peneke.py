#Import Modules
import os, pygame, copy
import math, random
from pygame.locals import *
import engine

if not pygame.font : print "Warning, pygame 'font' module disabled!"
if not pygame.mixer: print "Warning, pygame 'sound' module disabled!"

# --------------------------------------------------------
# Clamping a number between min m and max M
# --------------------------------------------------------
def clamp(x,m,M):
    if   x < m : return m
    elif x > M : return M
    return x
    
ENGINE = None # Global GAME variable

# --------------------------------------------------------
'''A player has the input game logic'''
# --------------------------------------------------------
class Player:
    def __init__(self,engine):
        self.engine = engine        
        self.keys = [K_1, K_2, K_3, K_4, K_5]

    def update(self):
        for k in self.keys:
            if self.engine.KEYPRESSED[k]:
                print k

    def draw(self):
        None

# --------------------------------------------------------
# Entry point
# --------------------------------------------------------
def main():
    global ENGINE
    # Initialize
    pygame.init()
    ENGINE = engine.Engine( "peneke!", (640,480) )
    #pygame.mouse.set_visible(0)
 
    # Main Loop
    nextkey = 0.0
    finished = False
    while not finished:
        # Clock
        ENGINE.clock.tick(60)
        dt = ENGINE.clock.get_time()/1000.0
        
        # Input
        for event in pygame.event.get():
            if event.type == QUIT:
                finished = True
                break        
        ENGINE.KEYPRESSED = pygame.key.get_pressed()
        finished = finished or ENGINE.KEYPRESSED[K_ESCAPE]
        nextkey -= dt
        
        # Update
        ENGINE.update(dt)

        # Draw
        ENGINE.draw()

    ENGINE.destroy()
    pygame.quit()

# Execute the game when this py is exec, not imported
if __name__ == '__main__':
    main()    
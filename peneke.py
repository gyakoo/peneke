'''
Copyright (c) 2016 gyakoo
'''
import os, pygame, copy
import math, random
from pygame.locals import *
import engine
import pytmx
from pytmx.util_pygame import *

# --------------------------------------------------------
class Player(engine.Actor):
    def __init__(self,engine):
        super(Player,self).__init__(engine)
        self.tile_map = load_pygame("data/test01.tmx")

    def mouseUp(self,pos):
        None

    def draw(self):
        surf = self.tile_map.get_tile_image(0,0,0)


# --------------------------------------------------------
# Entry point, only when executed, not imported
# --------------------------------------------------------
if __name__ == '__main__':
    # Initialize engine and actors
    pygame.init()
    eng = engine.Engine( "Peneke", (640,480) )
    player = Player(eng)    
    eng.addActor( player )
    #pygame.mouse.set_visible(0)

    # Main loop
    eng.run()

    # Finishing 
    eng.destroy()
    pygame.quit()    
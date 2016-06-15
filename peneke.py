'''
Copyright (c) 2016 gyakoo
'''
import os, pygame, copy
import math, random
from pygame.locals import *
import engine
import pytmx
from pytmx.util_pygame import *


class Scene(engine.Actor):
    def __init__(self,engine):
        super(Scene,self).__init__(engine)
        self.tile_map = load_pygame("data/test01.tmx")
    
    def draw(self):
        surf = self.tile_map.get_tile_image(0,0,0)

# --------------------------------------------------------
class Player(engine.Actor):
    def __init__(self,engine):
        super(Player,self).__init__(engine)

    def mouseUp(self,pos):
        None

    def draw(self):
        None


# --------------------------------------------------------
# Entry point, only when executed, not imported
# --------------------------------------------------------
if __name__ == '__main__':
    # Initialize engine and actors
    pygame.init()
    eng = engine.Engine( "Peneke", (640,480) )
    eng.addActor( Player(eng) )
    eng.addActor( Scene(eng) )
    #pygame.mouse.set_visible(0)

    # Main loop
    eng.run()

    # Finishing 
    eng.destroy()
    pygame.quit()    
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
class Scene(engine.Actor):
    def __init__(self,tmxfile,engine):
        super(Scene,self).__init__(engine)
        self.tile_map = load_pygame(tmxfile)
        self.offset = (0,0)

    def draw(self):
        self.drawLayers(range(0,3)) 

    def drawLayers(self,lrang):
        tw, th = self.tile_map.tilewidth, self.tile_map.tileheight
        ox, oy = self.offset
        r = Rect( ox, oy, tw, th )        
        images = self.tile_map.images
        for l in lrang:
            layer = self.tile_map.layers[l] 
            r.y = oy
            for row in layer.data:
                r.x = ox
                for gid in row: 
                    r.x += tw
                    if gid:
                        self.engine.SCREEN.blit(images[gid], r)
                r.y += th
        
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
    ENG = engine.Engine( "Peneke", (640,480) )
    ENG.showFPS = True

    ENG.addActor( Player(ENG) )
    ENG.addActor( Scene("data/test01.tmx",ENG) )
    engine.BEHAVIORS.createText("peneke",(20,300))
    #pygame.mouse.set_visible(0)

    # Main loop
    ENG.run()

    # Finishing 
    ENG.destroy()
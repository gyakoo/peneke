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
        self.f = self.engine.loadFont("type_writer.ttf", 14)
        self.a = self.f.render("hello world!", False, (200,0,100,255))
        self.alpha = 255

    def mouseUp(self,pos):
        None
    def update(self,dt):
        self.alpha -= 100.0*dt
        if self.alpha < 0.0: 
            self.alpha = 255

    def draw(self):
        r = self.a.get_rect()
        r.topleft = (400,200)
        engine.HELPER.blitAlpha(self.engine.SCREEN,self.a,(40,20),int(self.alpha))

# --------------------------------------------------------
# Entry point, only when executed, not imported
# --------------------------------------------------------
if __name__ == '__main__':
    # Initialize engine and actors
    ENG = engine.Engine( "Peneke", (640,480) )
    ENG.showFPS = True

    ENG.addActor( Scene("data/test01.tmx",ENG) )
    ENG.addActor( Player(ENG) )
    engine.BEHAVIORS.createText("peneke",(20,300))
    #pygame.mouse.set_visible(0)

    # Main loop
    ENG.run()

    # Finishing 
    ENG.destroy()
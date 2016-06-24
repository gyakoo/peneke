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
        self.offsx, self.offsy = 0, 0

    def update(self,dt):
        self.offsx -= 50.0 * dt

    def draw(self):
        self.drawLayers(range(0,1)) 

    def drawLayers(self,lrang):
        tw, th = self.tile_map.tilewidth, self.tile_map.tileheight
        ox, oy = self.offsx, self.offsy
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
class TestActor(engine.Actor):
    def __init__(self,engine):
        super(TestActor,self).__init__(engine)
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
        engine.HELPER.fillRect((10,10,24,24), (0,255,0,255))


# --------------------------------------------------------
class BhSpriteAnim(engine.Behavior):
    def __init__(self,actor,imgName, rects,fps):
        super(BhSpriteAnim,self).__init__(actor)
        self.actor.img = self.actor.engine.loadImage(imgName)
        self.actor.area = rects
        self.actor.rect = (10,34,24,24)
        self.actor.areaIndex = 0
        self.period = 1.0/fps
        self.t = self.period

    def update(self,dt):
        self.t -= dt
        if self.t <= 0.0:
            self.actor.areaIndex = (self.actor.areaIndex + 1 ) % len(self.actor.area)
            self.t += self.period

# --------------------------------------------------------
# Entry point, only when executed, not imported
# --------------------------------------------------------
if __name__ == '__main__':
    # Initialize engine and actors
    ENG = engine.Engine( "Peneke", (640,320), (1280,640), False)
    ENG.showFPS = True

    ENG.addActor( Scene("data/test02.tmx",ENG) )
    ENG.addActor( TestActor(ENG) )

    a = engine.Actor(ENG)
    a.addBehavior( engine.BhBlit(a) )
    a.addBehavior( BhSpriteAnim(a, "tileset_char.png", [(0,0,24,24), (24,0,24,24)], 4.0) )
    ENG.addActor( a )
    engine.BEHAVIORS.createText("peneke",(20,300))

    # Main loop
    ENG.run()

    # Finishing 
    ENG.destroy()
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
        self.tgtCamWsX, self.tgtCamWsY = 1000, 300
        self.camWsX, self.camWsY= 0, 0        

    def update(self,dt):
        if abs(self.camWsX - self.tgtCamWsX)>6:
            self.camWsX += (self.tgtCamWsX-self.camWsX)*0.25*dt
        if abs(self.camWsY - self.tgtCamWsY)>6:
            self.camWsY += (self.tgtCamWsY-self.camWsY)*0.25*dt
        
        if self.engine.KEYPRESSED[K_LEFT]: self.tgtCamWsX -= 200.0*dt
        elif self.engine.KEYPRESSED[K_RIGHT]: self.tgtCamWsX += 200.0*dt

    def draw(self):
        self.drawLayers(0) 

    def fromWsToTs(self,wsX,wsY):
        '''Transform from World Space pixel coordinates to Tile Space indices'''
        tsX = wsX / self.tile_map.tilewidth
        tsY = wsY / self.tile_map.tileheight
        return int(tsX), int(tsY)

    def fromTsToGid(self,layerNdx,tsX,tsY):
        '''Transform from Tile Space indices coordinates to Gid'''
        w, h = self.tile_map.width, self.tile_map.height
        if tsX<0 or tsY<0 or tsX>=w or tsY>=h: 
            return 0
        layer = self.tile_map.layers[layerNdx]
        return layer.data[tsY][tsX]

    def drawLayers(self,layerNdx):
        images = self.tile_map.images
        tw, th = self.tile_map.tilewidth, self.tile_map.tileheight
        vr = self.engine.virtualRes
        vrTw, vrTh = vr[0]/tw+1, vr[1]/th+1
        tlWsX, tlWsY = self.camWsX-vr[0]/2, self.camWsY-vr[1]/2
        startTsX, startTsY = self.fromWsToTs(tlWsX, tlWsY)
        ox, oy = tlWsX % tw, tlWsY % th
        ox = -ox
        oy = -oy
        r = Rect( ox, oy, tw, th )
        tsY = startTsY
        for iY in range(0,vrTh):
            tsX = startTsX
            r.x = ox
            for iX in range(0,vrTw):
                gid = self.fromTsToGid(layerNdx,tsX,tsY)
                if gid:
                    self.engine.SCREEN.blit(images[gid], r)
                r.x += tw
                tsX += 1
            tsY += 1
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
    a.addBehavior( BhSpriteAnim(a, "tileset_char.png", [(0,0,24,24), (24,0,24,24)], 6.0) )
    ENG.addActor( a )
    engine.BEHAVIORS.createText("peneke",(20,300))

    # Main loop
    ENG.run()

    # Finishing 
    ENG.destroy()
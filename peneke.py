'''
Copyright (c) 2016 gyakoo
'''
import os, pygame, copy
import math, random
from pygame.locals import *
import engine

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
# Entry point, only when executed, not imported
# --------------------------------------------------------
if __name__ == '__main__':
    # Initialize engine and actors
    ENG = engine.Engine( "Peneke", (640,320), (1280,640), False)
    ENG.showFPS = True

    ENG.addActor( engine.AcScene("data/test02.tmx",ENG) )
    ENG.addActor( TestActor(ENG) )

    a = engine.Actor(ENG)
    a.addBehavior( engine.BhBlit(a) )
    a.addBehavior( engine.BhSpriteAnim(a, "tileset_char.png", [(0,0,24,24), (24,0,24,24)], 6.0) )
    ENG.addActor( a )
    engine.BEHAVIORS.createText("peneke",(20,300))

    # Main loop
    ENG.run()

    # Finishing 
    ENG.destroy()
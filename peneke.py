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

    # SCENE
    sceneActor = engine.AcScene("data/test02.tmx",ENG)
    ENG.addActor( sceneActor )

    # SPRITE
    spriteActor = engine.Actor(ENG)
    spriteActor.addBehavior( engine.BhBlit(spriteActor,True) )
    spriteActor.addBehavior( engine.BhSpriteAnim(spriteActor, "tileset_char.png", [(0,0,24,24), (24,0,24,24)], 6.0) )
    spriteActor.rect = Rect( engine.Engine.scene.getInitSpawn(), (24,24))
    ENG.addActor( spriteActor )

    # scene follow camera
    sceneActor.addBehavior( engine.BhSceneCameraFollowActor(sceneActor,spriteActor) )

    # TESTING
    engine.BEHAVIORS.createText("peneke",(20,300))
    ENG.addActor( TestActor(ENG) )


    # Main loop
    ENG.run()

    # Finishing 
    ENG.destroy()
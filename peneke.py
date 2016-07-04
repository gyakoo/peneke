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
        engine.HELPER.drawRect((10,10,24,24), (0,255,0,255))


# --------------------------------------------------------
class BhPlayer(engine.Behavior):
    def __init__(self,actor):
        super(BhPlayer,self).__init__(actor)        
        self.actor.rect.topleft = engine.Engine.scene.getInitSpawn()
        self.actor.rect.size = (16,16)

    def update(self,dt):
        keys = engine.Engine.instance.KEYPRESSED

        # gravity
        downMov = 100*dt
        newRect = engine.HELPER.raycastDown(self.actor.rect,downMov)

        # horiz mov
        moved=False        
        if keys[K_LEFT]: 
            moved, dx = True, -160*dt
        elif keys[K_RIGHT]: 
            moved, dx = True, 160*dt

        if moved:
            newRect = engine.HELPER.rayCastMov(newRect,dx)

        self.actor.rect = Rect(newRect)

    def keyUp(self,key):
        if key == pygame.K_SPACE:
            self.actor.rect.topleft = engine.Engine.scene.getInitSpawn()
        elif key == pygame.K_v:
            self.actor.rect.top -= 70
        elif key == pygame.K_LCTRL:
            None



# --------------------------------------------------------
# Entry point, only when executed, not imported
# --------------------------------------------------------
if __name__ == '__main__':
    # Initialize engine and actors
    virtualRes = (480,320)
    resFactor = 2
    fullscreen = False
    engineObj = engine.Engine( "Peneke", virtualRes, (int(virtualRes[0]*resFactor),int(virtualRes[1]*resFactor)), fullscreen)
    engineObj.showFPS = True

    # SCENE
    sceneActor = engine.AcScene("data/test02.tmx",engineObj,(30,16))
    engineObj.addActor( sceneActor )

    # SPRITE
    spriteActor = engine.Actor(engineObj)
    spriteActor.addBehavior( BhPlayer(spriteActor) )
    spriteActor.addBehavior( engine.BhSpriteAnim(spriteActor, "tileset_char.png", [(0,0,16,16), (16,0,16,16)], 6.0) )
    spriteActor.addBehavior( engine.BhBlit(spriteActor, True) )
    engineObj.addActor( spriteActor )

    # scene follow camera
    sceneActor.addBehavior( engine.BhSceneCameraFollowActor(sceneActor,spriteActor) )
    #sceneActor.addBehavior( engine.BhSceneCameraScrollByInput(sceneActor) )
    sceneActor.tgtCamWsX, sceneActor.tgtCamWsY = spriteActor.rect.topleft
    
    # TESTING
    #engine.BEHAVIORS.createText("peneke",(20,300))
    #ENG.addActor( TestActor(ENG) )


    # Main loop
    engineObj.run()

    # Finishing 
    engineObj.destroy()
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
        newRect = Rect(self.actor.rect)
        changed=False
        if keys[K_a]: 
            newRect.x -= 128*dt
            changed=True
        elif keys[K_d]: 
            newRect.x += 128*dt
            changed=True
        if keys[K_w]: 
            newRect.y -= 128*dt
            changed=True
        elif keys[K_s]: 
            newRect.y += 128*dt
            changed=True
        elif keys[K_SPACE]:
            self.actor.rect.topleft = engine.Engine.scene.getInitSpawn()

        if changed:
            newRect = engine.HELPER.collideAsRect(self.actor.rect, newRect)
            self.actor.rect = Rect(newRect)

# --------------------------------------------------------
# Entry point, only when executed, not imported
# --------------------------------------------------------
if __name__ == '__main__':
    # Initialize engine and actors
    virtualRes = (480,320)
    resFactor = 2
    fullscreen = False
    engineObj = engine.Engine( "Peneke", virtualRes, (virtualRes[0]*resFactor,virtualRes[1]*resFactor), fullscreen)
    engineObj.showFPS = True

    # SCENE
    sceneActor = engine.AcScene("data/test02.tmx",engineObj,(30,16))
    engineObj.addActor( sceneActor )

    # SPRITE
    spriteActor = engine.Actor(engineObj)
    spriteActor.addBehavior( BhPlayer(spriteActor) )
    spriteActor.addBehavior( engine.BhSpriteAnim(spriteActor, "tileset_char.png", [(0,0,16,16), (16,0,16,16)], 6.0) )
    spriteActor.addBehavior( engine.BhBlit(spriteActor,True) )
    engineObj.addActor( spriteActor )

    # scene follow camera
    #sceneActor.addBehavior( engine.BhSceneCameraFollowActor(sceneActor,spriteActor) )
    sceneActor.addBehavior( engine.BhSceneCameraScrollByInput(sceneActor) )
    sceneActor.tgtCamWsX, sceneActor.tgtCamWsY = spriteActor.rect.topleft
    
    # TESTING
    #engine.BEHAVIORS.createText("peneke",(20,300))
    #ENG.addActor( TestActor(ENG) )


    # Main loop
    engineObj.run()

    # Finishing 
    engineObj.destroy()
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
        engine.HELPER.blitAlpha(self.engine.SCREENVIRTUAL,self.a,(40,20),int(self.alpha))
        engine.HELPER.drawRect((10,10,24,24), (0,255,0,255))


# --------------------------------------------------------
class BhPlayerPlatformer(engine.Behavior):
    MAXVY = 6.0
    JUMPTIME = 0.25
    PLCOLLWIDTH, PLCOLLHEIGHT = 14,14
    VX = 150.0 # if >=125 then moves 2 pixels per frame
    def __init__(self,actor, size):
        super(BhPlayerPlatformer,self).__init__(actor)        
        self.actor.rect.size = size
        self.actor.crect = Rect( engine.Engine.scene.getInitSpawn(), (BhPlayerPlatformer.PLCOLLWIDTH,BhPlayerPlatformer.PLCOLLHEIGHT) )
        self.vx, self.vy = 0.0, 0.0
        self.t = 0.0
        self.jumping = BhPlayerPlatformer.JUMPTIME
        self.landed = 0.0
        self.pressedJump = False
        self.updateActorDrawRect()
        self.wasMoving = False
        self.wasInAir = True

    def updateActorDrawRect(self):
        self.actor.rect.top = self.actor.crect.top-2
        self.actor.rect.left = self.actor.crect.left-1

    def update(self,dt):
        keys = engine.Engine.instance.KEYPRESSED
        gp = engine.Engine.instance.getGamepad(0)
        
        # -- INPUT --
        # horiz mov
        moved=False        
        if keys[K_LEFT] or (gp and gp.get_axis(0)<-0.2): 
            moved, dx = True, -BhPlayerPlatformer.VX*dt
        elif keys[K_RIGHT] or (gp and gp.get_axis(0)>0.2): 
            moved, dx = True, BhPlayerPlatformer.VX*dt

        # jumping control
        newPressedJump = keys[K_z] or (gp and gp.get_button(0))
        if self.pressedJump:
            if self.jumping < BhPlayerPlatformer.JUMPTIME:
                if not newPressedJump: # was jumping and just released
                    self.startFalling()
                else: # was and is jumping
                    self.jumping += dt
                    if self.jumping > BhPlayerPlatformer.JUMPTIME:
                        self.startFalling()
        elif self.landed > 0.0:
            if newPressedJump : # was not jumping but just pressed it
                self.jumping = 0.0
                self.landed = 0.0

        self.pressedJump = newPressedJump

        # -- UPDATE --
        falling = self.jumping>=BhPlayerPlatformer.JUMPTIME
        inAir = falling
        if falling:
            # gravity
            self.vy += 5.0*self.t
            self.vy = min(self.vy, BhPlayerPlatformer.MAXVY)
            downMov = self.vy*self.t + self.t*self.t
            c, newRect = engine.HELPER.raycastDown(self.actor.crect,max(1,downMov))
            if c:
                self.vy, self.t = 0.0, 0.0
                self.landed += dt   
                inAir=False
            else:
                self.t += dt
                self.landed = 0.0
        else: 
            # jumping
            inAir=True
            j = self.jumping/BhPlayerPlatformer.JUMPTIME
            upMov = -400.0 * dt * (1.0-j)
            c, newRect = engine.HELPER.raycastUp(self.actor.crect, upMov)
            if c:
                self.startFalling() # has collided with something

        # collision
        if moved:
            newRect = engine.HELPER.rayCastMov(newRect,dx)
            self.actor.flipX = dx < 0.0

        # animation control
        if inAir:
            self.actor.message("ANIM","jump")
        elif moved:
            if self.wasInAir:
                self.actor.message("ANIM","runlanded")
            else:
                self.actor.message("ANIM","run")
        elif self.wasMoving or self.wasInAir:
            self.actor.message("ANIM","idle")
        
        # finally update collision rect! (and cache some states)
        self.actor.crect = Rect(newRect) # !!
        self.updateActorDrawRect()
        self.wasMoving = moved
        self.wasInAir = inAir

        # out of bounds
        if self.actor.crect.bottom > 500:
            self.spawn()

    def startFalling(self):
        self.jumping = BhPlayerPlatformer.JUMPTIME
        self.vy, self.t = 0.0, 0.0
        self.landed = 0.0

    def spawn(self):
        self.actor.crect.topleft = engine.Engine.scene.getInitSpawn()
        engine.Engine.scene.spawnCamera()

    def keyUp(self,key):
        if key == pygame.K_SPACE:
            self.spawn()            
        elif key == pygame.K_v:
            self.actor.crect.top -= 70
            self.startFalling()

# --------------------------------------------------------
def placeInTile(a,tx,ty):
    r = engine.Engine.scene.fromTsToTileRect(tx,ty)
    a.rect.left = r[0]
    a.rect.bottom = r[1]+16

def createSprite(spriteSheet, anim,animDef,tx,ty):
    actor = engine.Actor(engineObj)
    actor.addBehavior( engine.BhSprite(actor, spriteSheet, anim, animDef) )
    actor.addBehavior( engine.BhBlit(actor,True) )
    placeInTile(actor,tx,ty)
    return actor

# --------------------------------------------------------
# Entry point, only when executed, not imported
# --------------------------------------------------------
if __name__ == '__main__':
    # Some config
    virtualRes = (480,320)
    resFactor = 2
    fullscreen = False
    playerSize = tileSize = (16,16)
    sceneTiles = (30,16)
    colorKey = (0,255,255)

    # Initialize engine and actors    
    if not fullscreen:
        physRes = (int(virtualRes[0]*resFactor),int(virtualRes[1]*resFactor))
    else:
        physRes = (1024,768)
        
    engineObj = engine.Engine( "Peneke", virtualRes, physRes, fullscreen)
    engineObj.showFPS = True

    sceneActor = engine.AcScene("data/test02.tmx",engineObj,sceneTiles)

    # SPRITE
    spriteSheet = engine.SpriteSheet("tilesetchar256.png",True,tileSize,colorKey)
    spriteActor = engine.Actor(engineObj)
    spriteActor.addBehavior( BhPlayerPlatformer(spriteActor,playerSize) )
    spriteActor.addBehavior( engine.BhSprite(spriteActor, spriteSheet, "slug.anim" ) )
    spriteActor.addBehavior( engine.BhBlit(spriteActor, True) )
    engineObj.addActor( spriteActor )
       

    # scene follow camera
    sceneActor.addBehavior( engine.BhSceneCameraFollowActor(sceneActor,spriteActor,True) )
    #sceneActor.addBehavior( engine.BhSceneCameraScrollByInput(sceneActor) )
    sceneActor.tgtCamWsX, sceneActor.tgtCamWsY = spriteActor.rect.topleft
    
    # TESTING
    # ------------------------------------------------------------
    #ENG.addActor( TestActor(ENG) )
    engineObj.addActor( createSprite(spriteSheet,"erudito.anim","walk",49,12) )
    for i in range(43,48):
        if i % 2 == 1 :
            engineObj.addActor( createSprite(spriteSheet,"child.anim","idle",i,12) )
    engineObj.addActor( createSprite(spriteSheet,"bush.anim","idle",51,14) )
    engineObj.addActor( createSprite(spriteSheet,"bird.anim","fly",52,9) )
    engineObj.addActor( createSprite(spriteSheet,"naboman.anim","idle",55,14) )
    engineObj.addActor( createSprite(spriteSheet,"babosa.anim","walk",58,14) )
    engineObj.addActor( createSprite(spriteSheet,"mosquito.anim","fly",60,10) )
    engineObj.addActor( createSprite(spriteSheet,"carawood.anim","walk",54,11) )

    # ------------------------------------------------------------
    # SCENE
    engineObj.addActor( sceneActor )

    x, y = 100, 256
    y += engine.BEHAVIORS.createText("Pxlvetica",(x,y), "Pxlvetica.ttf", 16)
    y += engine.BEHAVIORS.createText("Thin Pixel-7",(x,y), "thin_pixel-7.ttf", 16)
    y += engine.BEHAVIORS.createText("Typewriter",(x,y), "type_writer.ttf", 8)
    y += engine.BEHAVIORS.createText("Bitout",(x,y), "bitout.fon", 14)
    x, y =300, 256
    y += engine.BEHAVIORS.createText("Computer Pixel-7",(x,y), "computer_pixel-7.ttf", 16)

    # Main loop
    engineObj.run()

    # Finishing 
    engineObj.destroy()
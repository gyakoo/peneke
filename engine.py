'''
Copyright (c) 2016 gyakoo
'''
import os, pygame, copy
import math, random
from pygame.locals import *

assert pygame.font
assert pygame.mixer

# -------------------------------------------------------
class Behavior(object):
    def __init__(self,actor):
        self.actor = actor
        self.markForDestroy = False
    
    def update(self,dt): None
    def draw(self): None
    def destroy(self): None

# -------------------------------------------------------
class Actor(object):
    '''Base Actor class'''
    def __init__(self,engine):
        self.engine = engine
        self.markForDestroy = False
        self.behaviors = []
        self.img = None
        self.rect, self.area = None, None
        self.alpha = 255
        self.imgIndex = -1
        self.areaIndex = -1

    def addBehavior(self,b):
        self.behaviors.append(b)
    def update(self, dt):
        toDestroy = []
        for b in self.behaviors: 
            b.update(dt)
            if b.markForDestroy:
                b.destroy()
                toDestroy.append(b)
        for b in toDestroy:
            self.behaviors.remove(b)
    def draw(self):        
        for b in self.behaviors: b.draw()
    def destroy(self): 
        for b in self.behaviors: b.destroy()
        self.behaviors = []
    def mouseUp(self,p): None

#----------------------------------------------------------------------
class HELPER:
    EASE_LINEAR = 0
    
    @staticmethod
    def easeCompute(): 
        return 1.0

    @staticmethod
    def clamp(x,m,M):
        if   x < m : return m
        elif x > M : return M
        return x

    @staticmethod
    def blitAlpha(target, source, location, opacity, area=None):
        x, y = location
        size = (source.get_width(), source.get_height())
        temp = Engine.instance.getScratchSurf(size)
        temp.blit(target, (-x, -y))
        temp.blit(source, (0, 0), area)
        temp.set_alpha(opacity)        
        target.blit(temp, location)

    @staticmethod
    def fillRect(r,color):
        pygame.draw.rect(Engine.instance.SCREEN, color, r)

    @staticmethod
    def blit(source,dstRect,area=None):
        Engine.instance.SCREEN.blit( source, dstRect, area)

# --------------------------------------------------------
class Engine:
    instance = None

    '''Main Engine class'''
    def __init__(self,name,vres,pres,fullscreen=False):
        '''Builds the Engine'''
        pygame.init()
        BEHAVIORS.engine = self
        self.name = name
        self.clock = pygame.time.Clock()
        self.virtualRes, self.physicalRes = vres, pres
        self.scaling = vres != pres
        self.IMAGECACHE, self.SOUNDCACHE, self.FONTCACHE = {}, {}, {}
        self.SCRATCHSURFCACHE = {}
        self.KEYPRESSED = None
        self.fullscreen = fullscreen
        flags = pygame.DOUBLEBUF
        if fullscreen: 
            flags = flags | pygame.FULLSCREEN | pygame.HWSURFACE
        bestdepth = pygame.display.mode_ok(self.physicalRes, flags, 32)        
        self.FINALSCREEN = pygame.display.set_mode(self.physicalRes, flags, bestdepth)
        self.SCREEN = pygame.Surface(self.virtualRes) if self.scaling else self.FINALSCREEN
        pygame.display.set_caption(name)
        self.atfps, self.nextSound = 0.0, 0.0        
        self.actors, self.actorsToDestroy = [], []
        self.showFPS, self.running = False, True
        self.pathToFonts = "data/fonts/"
        self.pathToSounds= "data/sounds/"
        self.pathToImages= "data/images/"
        self.imageExtensions = ["", ".png", ".bmp", ".gif"]
        self.bgColor = (0,0,0)
        Engine.instance = self
        if fullscreen: 
            pygame.mouse.set_visible(0)

    def addActor(self,a):
        '''Registers an actor in the game. an actor must be subclass of Actor'''
        self.actors.append(a)

    def destroy(self):        
        '''Deinit the engine'''
        for a in self.actors:
            a.destroy()
        self.actors = []
        pygame.quit()    

    def loadFont(self,fontname,size):
        '''Loads and caches a font handle'''
        assert pygame.font
        key = (fontname,size)
        font = None
        if not self.FONTCACHE.has_key(key):
            path = self.pathToFonts+fontname
            font = pygame.font.Font(path, size)
            assert font
            if font: self.FONTCACHE[key] = font
        else:
            font = self.FONTCACHE[key]
        return font
        
    def loadSound(self,name):
        '''Loads and caches a sound handle'''
        fullname = self.pathToSounds+name
        sound = None
        if not self.SOUNDCACHE.has_key(name):            
            try:
                s = ""
                if not fullname.endsWith(".wav"):
                    fullname = fullname + ".wav"
                sound = pygame.mixer.Sound(fullname)
            except pygame.error, message:
                print 'Cannot load sound:', name
            if sound:
                self.SOUNDCACHE[name] = sound
        else:
            sound = self.SOUNDCACHE[name]
        return sound

    def getScratchSurf(self,dim):
        ss = None
        if not self.SCRATCHSURFCACHE.has_key(dim):
            ss = pygame.Surface(dim).convert()
            self.SCRATCHSURFCACHE[dim] = ss
        else:
            ss = self.SCRATCHSURFCACHE[dim]
        return ss
    
    def loadImage(self,file, rotation = 0, flipx = False, flipy = False):
        '''Loads and caches an image handle'''
        key = (file, rotation, flipx, flipy)
        if not self.IMAGECACHE.has_key(key):
            path = self.pathToImages+file #os.path.join('data', file)            
            for e in self.imageExtensions:
                if os.path.exists(path + e):
                    path = path + e
                    break
            if rotation or flipx or flipy:
                img = self.loadImage(file)
            else:
                img = pygame.image.load(path).convert_alpha()
            if rotation:
                img = pygame.transform.rotate(img, rotation)
            if flipx or flipy:
                img = pygame.transform.flip(img, flipx, flipy)
            self.IMAGECACHE[key] = img
        return self.IMAGECACHE[key]
        
    def playSound(self,name,vol=1.0):
        '''Plays a sound by name'''
        if self.nextSound <= 0.0: # avoiding two very consecutive sounds
            sound = self.loadSound(name)
            sound.set_volume(vol)
            sound.play()
            self.nextSound = 0.1

    def draw(self):
        '''Draws and flip buffers'''
        self.SCREEN.fill(self.bgColor)
        for a in self.actors:
            a.draw()
        if self.scaling:
            pygame.transform.scale(self.SCREEN, self.physicalRes, self.FINALSCREEN)
        pygame.display.flip()
                   
    def update(self,dt):
        '''Updates the engine state'''
        # Update fps stats
        if self.showFPS:
            self.atfps += dt
            if self.atfps > 3.0:
                pygame.display.set_caption(self.name + " fps: " + str(int(self.clock.get_fps())))
                self.atfps -= 3.0
        # update sound timer and actors
        self.nextSound -= dt     
        self.actorsToDestroy=[]        
        for a in self.actors:
            a.update(dt)
            if a.markForDestroy:
                a.destroy()
                self.actorsToDestroy.append(a)
        for atr in self.actorsToDestroy:
            self.actors.remove(atr)
            
    def run(self):
        '''Main Loop'''
        nextkey = 0.0
        self.running = True
        while self.running:
            # Clock
            self.clock.tick(60)
            dt = 1.0/60.0#self.clock.get_time()/1000.0
        
            # Input
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONUP:
                    for a in self.actors: 
                        a.mouseUp(pygame.mouse.get_pos())
                        
            self.KEYPRESSED = pygame.key.get_pressed()
            if self.KEYPRESSED[K_ESCAPE]: break
            nextkey -= dt
            self.update(dt)
            self.draw()

#-----------------------------------------------------------
class BhBlit(Behavior):
    def __init__(self,actor):
        super(BhBlit,self).__init__(actor)

    def _blitFuncOp(self,tgt,src,r,op,a):
        tgt.blit(src,r,a)

    def _blitFuncAl(self,tgt,src,r,op,a):
        HELPER.blitAlpha(SCR,img[i],r[i].topleft,alpha,srcRect)

    def draw(self):
        img = self.actor.img
        r = self.actor.rect
        ai = self.actor.areaIndex        
        srcRect = self.actor.area if ai==-1 else self.actor.area[ai]
        if not img or not r: return
        SCR = self.actor.engine.SCREEN
        ii = self.actor.imgIndex
        alpha = self.actor.alpha
        blitFunc = self._blitFuncOp if alpha==255 else self._blitFuncAl
        if isinstance(img,list):
            if isinstance(r,list):
                if ii < 0:
                    for i in range(0,len(img)):
                        blitFunc(SCR,img[i],r[i],alpha,srcRect)
                else:
                    for i in range(0,len(img)):
                        blitFunc(SCR,img[ii],r[i],alpha,srcRect)
            else:
                if ii < 0:
                    for i in range(0,len(img)):
                        blitFunc(SCR,img[i],r,alpha,srcRect)
                else:
                    blitFunc(SCR,img[ii],r,alpha,srcRect)
        else: # IMG single
            if isinstance(r,list):
                if ii < 0 :
                    for i in range(0,len(r)):
                        blitFunc(SCR,img,r[i],alpha,srcRect)
                else:
                    blitFunc(SCR,img,r[ii],alpha,srcRect)
            else:
                blitFunc(SCR,img,r,alpha,srcRect)

#-----------------------------------------------------------
class BhText(Behavior):
    def __init__(self,actor,text,topleft,font="type_writer.ttf",size=14):
        assert text
        super(BhText,self).__init__(actor)
        self.text = ""        
        self.actor.color = (255,255,255)
        self.actor.rect = Rect(topleft,(0,0))
        self.setFont(font,size)
        self.setText(text)

    def setFont(self,fontName,size):
        self.font = self.actor.engine.loadFont(fontName,size)
        if self.text:
            self.setText(self.text)

    def setColor(self,color):
        if color != self.actor.color:
            self.actor.color = color
            self.setText(self.text)

    def setTopLeft(self,topleft):
        self.actor.rect.topleft = topleft

    def setText(self,text):
        assert self.font
        if self.text != text:
            self.actor.img = self.font.render(text,False,self.actor.color)
            self.actor.rect.size = self.actor.img.get_rect().size

#----------------------------------------------------------------------
class BhDestroyActor(Behavior):
    def __init__(self,actor,timeSec=0.0):
        super(BhDestroyActor,self).__init__(actor)
        self.time = timeSec

    def update(self,dt):
        self.time -= dt
        if self.time <= 0.0:
            self.actor.markForDestroy = True


class BhSequence(Behavior):
    None

#----------------------------------------------------------------------
class BhDestroyBehavior(Behavior):
    def __init__(self,behavior,timeSec=0.0):
        assert behavior
        self.innerBehavior = behavior
        super(BhDestroyBehavior,self).__init__(behavior.actor)
        self.time = timeSec

    def update(self,dt):
        self.time -= dt
        if self.time > 0.0:
            self.innerBehavior.update(dt)
        else:
            self.markForDestroy = True

    def draw(self): self.innerBehavior.draw()
    def destroy(self): self.innerBehavior.destroy()
            
#----------------------------------------------------------------------
class BhSequence(Behavior):
    def __init__(self,actor,seq):
        assert seq
        super(BhSequence,self).__init__(actor)
        self.sequence = seq
        self.index = 0
       
    def update(self,dt):
        if self.index < len(self.sequence):
            b = self.sequence[self.index]
            b.update(dt)
            if b.markForDestroy:
                self.index += 1
        if self.index >= len(self.sequence):
            self.markForDestroy = True

    def draw(self):
        if self.index < len(self.sequence):
            self.sequence[self.index].draw()

    def destroy(self):
        if self.index < len(self.sequence):
            for i in range(self.index,len(self.sequence)):
                self.sequence[i].destroy()

#----------------------------------------------------------------------
class BhWaitForTime(Behavior):
    def __init__(self,actor,timeInSec):
        super(BhWaitForTime,self).__init__(actor)
        self.time = timeInSec

    def update(self,dt):
        if self.time <= 0.0: self.markForDestroy = True
        else: self.time -= dt

#----------------------------------------------------------------------
class BhMoveTo(Behavior):
    def __init__(self,actor,targetTopLeft,timeSec,easeType=HELPER.EASE_LINEAR):
        super(BhMoveTo,self).__init__(actor)
        self.targetTopLeft = targetTopLeft
        self.easeType = easeType
        self.timeSec = timeSec
        self.time = timeSec
        self.dirx, self.diry = None, None
        self.srcTL = None

    def update(self,dt):
        if self.time <= 0.0:
            self.actor.rect.topleft = self.targetTopLeft
            self.markForDestroy=True
        else:
            if self.dirx == None:
                self.srcTL = self.actor.rect.topleft
                self.dirx = self.targetTopLeft[0]-self.srcTL[0]
                self.diry = self.targetTopLeft[1]-self.srcTL[1]
            t = 1.0 - self.time / self.timeSec
            x,y = self.srcTL
            x += t * self.dirx
            y += t * self.diry
            self.actor.rect.topleft = (x,y)
            self.time -= dt

#----------------------------------------------------------------------
class BEHAVIORS:
    engine = None

    @staticmethod
    def createText(text,topleft,fontname="type_writer.ttf",size=14):
        assert BEHAVIORS.engine
        a = Actor(BEHAVIORS.engine)
        a.addBehavior(BhBlit(a))
        a.addBehavior(BhText(a,text,topleft,fontname,size))
        a.addBehavior(BhSequence(a,
          [BhMoveTo(a,(100,200),3.0), 
           BhMoveTo(a,(100,300),3.0), 
           BhDestroyActor(a,3)]))
        BEHAVIORS.engine.addActor(a)


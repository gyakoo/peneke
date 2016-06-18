'''
Copyright (c) 2016 gyakoo
'''
import os, pygame, copy
import math, random
from pygame.locals import *

if not pygame.font : print "Warning, pygame 'font' module disabled!"
if not pygame.mixer: print "Warning, pygame 'sound' module disabled!"

# -------------------------------------------------------
def clamp(x,m,M):
    '''Clamping a number between min m and max M'''
    if   x < m : return m
    elif x > M : return M
    return x
    

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
        self.rect = None
        self.color = None
        self.imgIndex = -1

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

# --------------------------------------------------------
class Engine:
    '''Main Engine class'''
    def __init__(self,name,resolution):
        '''Builds the Engine'''
        pygame.init()
        BhFactory.engine = self
        self.clock = pygame.time.Clock()
        self.SCREENRECT = Rect(0, 0, resolution[0], resolution[1])
        self.IMAGECACHE, self.SOUNDCACHE, self.FONTCACHE = {}, {}, {}
        self.KEYPRESSED = None
        bestdepth = pygame.display.mode_ok(self.SCREENRECT.size, pygame.DOUBLEBUF, 32)
        self.SCREEN = pygame.display.set_mode(self.SCREENRECT.size, pygame.DOUBLEBUF, bestdepth)
        self.name = name
        pygame.display.set_caption(name)
        self.atfps, self.nextSound = 0.0, 0.0        
        self.actors, self.actorsToDestroy = [], []
        self.showFPS = False
        self.running = True
        self.pathToFonts = "data/fonts/"
        self.pathToSounds= "data/sounds/"
        self.pathToImages= "data/images/"
        self.imageExtensions = ["", ".png", ".bmp", ".gif"]

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
        self.SCREEN.fill((0,0,0))
        for a in self.actors:
            a.draw()        
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
            dt = self.clock.get_time()/1000.0
        
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

    def draw(self):
        img = self.actor.img
        r = self.actor.rect
        e = self.actor.engine
        ii = self.actor.imgIndex
        if not img or not r: return
        if isinstance(img,list):
            if isinstance(r,list):
                if ii < 0:
                    for i in range(0,len(img)):
                        e.SCREEN.blit( img[i], r[i] )
                else:
                    e.SCREEN.blit( img[ii], r[ii] )
            else:
                if ii < 0:
                    for i in range(0,len(img)):
                        e.SCREEN.blit( img[i], r )
                else:
                    e.SCREEN.blit(img[ii],r)
        else: # IMG single
            if isinstance(r,list):
                if ii < 0 :
                    for i in range(0,len(r)):
                        e.SCREEN.blit( img, r[i])
                else:
                    e.SCREEN.blit(img,r[ii])
            else:
                e.SCREEN.blit(img,r)

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
class BhDestroy(Behavior):
    def __init__(self,actor,timeSec=0.0):
        super(BhDestroy,self).__init__(actor)
        self.time = timeSec

    def update(self,dt):
        self.time -= dt
        if self.time <= 0.0:
            self.actor.markForDestroy = True


class BhSequence(Behavior):
    None

#----------------------------------------------------------------------
class BhFactory:
    engine = None

    @staticmethod
    def createText(text,topleft,fontname="type_writer.ttf",size=14):
        assert BhFactory.engine
        a = Actor(BhFactory.engine)
        a.addBehavior(BhBlit(a))
        a.addBehavior(BhText(a,text,topleft,fontname,size))
        a.addBehavior(BhDestroy(a,5.0))
        BhFactory.engine.addActor(a)

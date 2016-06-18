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
class Actor(object):
    '''Base Actor class'''
    def __init__(self,engine):
        self.engine = engine
        self.markForRemove = False

    def update(self, dt): None
    def draw(self): None
    def destroy(self): None
    def mouseUp(self,p): None
# --------------------------------------------------------
class Engine:
    '''Main Engine class'''
    def __init__(self,name,resolution):
        '''Builds the Engine'''
        self.clock = pygame.time.Clock()
        self.SCREENRECT = Rect(0, 0, resolution[0], resolution[1])
        self.IMAGECACHE, self.SOUNDCACHE, self.FONTCACHE = {}, {}, {}
        self.KEYPRESSED = None
        bestdepth = pygame.display.mode_ok(self.SCREENRECT.size, pygame.DOUBLEBUF, 32)
        self.SCREEN = pygame.display.set_mode(self.SCREENRECT.size, pygame.DOUBLEBUF, bestdepth)
        self.name = name
        pygame.display.set_caption(name)
        self.atfps, self.nextSound = 0.0, 0.0        
        self.actors, self.actorsToRemove = [], []
        self.showFPS = False
        self.running = True

    def addActor(self,a):
        '''Registers an actor in the game. an actor must be subclass of Actor'''
        self.actors.append(a)

    def destroy(self):        
        '''Deinit the engine'''
        for a in self.actors:
            a.destroy()
        self.actors = []

    def loadFont(self,fontname,size):
        '''Loads and caches a font handle'''
        if not pygame.font: return None
        key = (fontname,size)
        font = None
        if not self.FONTCACHE.has_key(key):
            path = "data/"+fontname
            font = pygame.font.Font(path, size)
            if font: self.FONTCACHE[key] = font
        else:
            font = self.FONTCACHE[ key ]
        return font
        
    def loadSound(self,name):
        '''Loads and caches a sound handle'''
        fullname = "data/"+name #os.path.join('data', name)
        sound = None
        if not self.SOUNDCACHE.has_key(name):            
            try: 
                sound = pygame.mixer.Sound(fullname+".wav")
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
            path = "data/"+file #os.path.join('data', file)
            ext = ["", ".png", ".bmp", ".gif"]
            for e in ext:
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
        self.actorsToRemove=[]        
        for a in self.actors:
            a.update(dt)
            if a.markForRemove:
                self.actorsToRemove.append(a)
        for atr in self.actorsToRemove:
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
                    finished = True
                    break
                elif event.type == pygame.MOUSEBUTTONUP:
                    for a in self.actors: 
                        a.mouseUp(pygame.mouse.get_pos())
                        
            self.KEYPRESSED = pygame.key.get_pressed()
            self.running = self.running or self.KEYPRESSED[K_ESCAPE]
            nextkey -= dt
        
            # Update
            self.update(dt)

            # Draw
            self.draw()

#-----------------------------------------------------------
class AcEase(Actor):
    LINEAR=0
    def __init__(self, engine, time, val, easeType=AcEase.LINEAR):
        assert time >= 0.0
        super(AcEase,self).__init__(engine)
        self.startValue, self.startTime = val, time
        self.value, self.time = val, time
        self.easeType = easeType

#-----------------------------------------------------------
class AcEaseOut(AcEase):
    def __init__(self, engine, timeOut, startValue, easeType=AcEase.LINEAR):
        assert startValue >= 0.0
        super(AcEaseOut,self).__init__(engine, timeOut, startValue, easeType)
        
    def update(self,dt):
        if self.time <= 0.0:
            self.markForRemove = True
            return        
        self.time -= dt
        if self.time <= 0.0:
            self.value = 0.0
        elif self.easeType == AcEase.LINEAR:
            self.value = self.startTime/self.time * self.startValue

#-----------------------------------------------------------
class AcEaseIn(AcEase):
    def __init__(self, engine, timeIn, endValue, easeType=AcEase.LINEAR):
        assert endValue >= 0.0
        super(AcEaseIn,self).__init__(engine, timeIn, endValue, easeType)
        
    def update(self,dt):
        if self.time <= 0.0:
            self.markForRemove = True
            return        
        self.time -= dt
        if self.time <= 0.0:
            self.value = 0.0
        elif self.easeType == AcEase.LINEAR:
            self.value = (1.0-self.startTime/self.time) * self.startValue
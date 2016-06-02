#Import Modules
import os, pygame, copy
import math, random
from pygame.locals import *

# --------------------------------------------------------
'''Main Engine class'''
# --------------------------------------------------------
class Engine:
    '''Builds the Engine'''
    def __init__(self,name,resolution):
        self.clock = pygame.time.Clock()
        self.SCREENRECT = Rect(0, 0, resolution[0], resolution[1])
        self.IMAGECACHE, self.SOUNDCACHE, self.FONTCACHE = {}, {}, {}
        self.KEYPRESSED = None
        bestdepth = pygame.display.mode_ok(self.SCREENRECT.size, pygame.DOUBLEBUF, 32)
        self.SCREEN = pygame.display.set_mode(self.SCREENRECT.size, pygame.DOUBLEBUF, bestdepth)
        self.name = name
        pygame.display.set_caption(name)
        self.atfps, self.nextSound = 0.0, 0.0                

    '''Deinit the engine'''
    def destroy(self):
        None

    '''Loads and caches a font handle'''
    def loadFont(self,fontname,size):
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
        
    '''Loads and caches a sound handle'''
    def loadSound(self,name):
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
    
    '''Loads and caches an image handle'''
    def loadImage(self,file, rotation = 0, flipx = False, flipy = False):
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
        
    '''Plays a sound by name'''
    def playSound(self,name,vol=1.0):
        if self.nextSound <= 0.0: # avoiding two very consecutive sounds
            sound = self.loadSound(name)
            sound.set_volume(vol)
            sound.play()
            self.nextSound = 0.1

    '''Draws and flip buffers'''
    def draw(self):                
        pygame.display.flip()
                   
    '''Updates the engine state'''
    def update(self,dt):
        # Update fps stats
        self.atfps += dt
        self.nextSound -= dt
        if self.atfps > 3.0:
            pygame.display.set_caption(self.name + " fps: " + str(int(self.clock.get_fps())))
            self.atfps = 0.0        
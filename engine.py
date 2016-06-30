'''
Copyright (c) 2016 gyakoo
'''
import os, pygame, copy
from sets import Set
import math, random
from pygame.locals import *
import pytmx
import util_pygame
from util_pygame import *

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
        self.rect, self.area = Rect(0,0,0,0), None
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
    COLLIDERS=Set(range(992,1003))
    
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
    def drawRect(r,color,w=0,ws=False):
        if ws:
            top,left = Engine.scene.fromWsToSs(r[0],r[1])
            r = (top,left,r[2],r[3])
        pygame.draw.rect(Engine.instance.SCREEN, color, r, w)

    @staticmethod
    def blit(source,dstRect,area=None):
        Engine.instance.SCREEN.blit( source, dstRect, area)

    @staticmethod
    def segmentVsSegment(a,b):
        x0,y0,x1,y1 = a[0][0],a[0][1], a[1][0], a[1][1]
        x2,y2,x3,y3 = b[0][0],b[0][1], b[1][0], b[1][1]
        b,c = x1 - x0, x3 - x2
        d,e = y1 - y0, y3 - y2	
        div = (c * d - e * b)
        if div:
            a, f = x2 - x0, y2 - y0
            inv = 1.0 / div
            t = (f * c - a * e) * inv
            s = (f * b - a * d) * inv
            if s >= 0.0 and s <= 1.0 and t >= 0.0 and t <= 1.0:
                return True,t
        return False,0

    @staticmethod
    def fractionToWs(seg,f):
        d = (seg[1][0] - seg[0][0], seg[1][1] - seg[0][1])
        return (seg[0][0] + d[0] * f, seg[0][1] + d[1] * f)

    @staticmethod
    def segmentVsManySegments(seg,segs):
        i,m = False,10 # t should be always 0-1
        for s in segs:
            c,t = HELPER.segmentVsSegment(seg,s)
            if c and t < m:
                m = t
                i = True
        return i,m

    @staticmethod
    def segmentVsRect(seg,r):
        rs = HELPER.getRectSegments(r)
        return HELPER.segmentVsManySegments(seg,rs)

    @staticmethod
    def segmentVsGidRect(seg,gr):
        rs = HELPER.getGidRectSegments(gr)
        return HELPER.segmentVsManySegments(seg,rs)

    @staticmethod
    def getRectSegments(r):
        return [ (r.topleft,r.topright), 
                (r.topright,r.bottomright), 
                (r.bottomright,r.bottomleft), 
                (r.bottomleft, r.topleft) ]

    @staticmethod
    def getGidRectSegments(gr):
        gid, r = gr[0], Rect(gr[1])
        if gid==997:
            l = [ (r.bottomleft, r.topright) ]
        elif gid==998:
            l = [ (r.topleft, r.bottomright) ]
        elif gid==999:
            l = [ (r.bottomleft, r.midright) ]
        elif gid==1000:
            l = [ (r.midleft, r.topright) ]
        elif gid==1001:
            l = [ (r.topleft, r.midright) ]
        elif gid==1002:
            l = [ (r.midleft, r.bottomright) ]
        else:
            l = HELPER.getRectSegments(r)
        return l

    @staticmethod
    def getRectSweepSegments(src,dst):
        return [ (src.topleft,dst.topleft), 
                (src.topright, dst.topright),
                (src.bottomright, dst.bottomright),
                (src.bottomleft, dst.bottomleft) ]

    @staticmethod
    def getClosestIntersection(src,dirOrDst,r):
        if len(dirOrDst)==2:
            dst = Rect(dirOrDst)
            dst.move_ip(dir)
        else:
            dst = dirOrDst
        sweepSegs = HELPER.getRectSweepSegments(src,dst)
        tgtSegs = HELPER.getRectSegments(Rect(r))
        isect,closest, cindex = False,10,-1  
        for j in range(0, len(sweepSegs)):
            i,t = HELPER.segmentVsManySegments(sweepSegs[j],tgtSegs)
            if i and t < closest:
                isect, closest, cindex = True, t, j
        return isect,closest, HELPER.fractionToWs(sweepSegs[cindex],closest) \
                if isect else (0,0)
    
    @staticmethod
    def rayCastVertical(r,dy):
        isect,mint = False, 10
        segs = [ ( r.bottomleft, (r.left,r.bottom+dy) ),
            ( r.bottomright, (r.right, r.bottom+dy) ) ]
        for j in range(0,len(segs)):
            seg = segs[j]
            lgr = Engine.scene.getCollGidsInSegment(seg)
            for gr in lgr:
                i, t = HELPER.segmentVsGidRect(seg,gr)
                if i and t < mint:
                    isect, mint = True, t
        
        newRect = Rect(r)
        dy = dy*mint if isect else dy
        newRect.move_ip(0,dy)
        #newRect.move_ip( -dx/abs(dx) if dx else 0, -dy/abs(dy) if dy else 0 )
        return newRect

    @staticmethod
    def rayCastMov(srcRect,dx):
        isect,mint = False, 10
        r = srcRect.inflate(0,-2)
        r.move_ip(dx/abs(dx),0)
        if dx > 0.0:
            segs = [ ( r.topright, (r.right+dx,r.top) ),
                     ( r.midright, (r.right+dx, r.centery) ),
                     ( r.bottomright, (r.right+dx, r.bottom) ) ]
        else:
            segs = [ ( r.topleft, (r.left+dx,r.top) ),                     
                     ( r.midleft, (r.left+dx, r.centery) ),
                     ( r.bottomleft, (r.left+dx, r.bottom) ) ]
        
        for j in range(0,len(segs)):
            seg = segs[j]
            lgr = Engine.scene.getCollGidsInSegment(seg)
            for gr in lgr:
                i, t = HELPER.segmentVsGidRect(seg,gr)
                if i and t < mint:
                    isect, mint = True, t
        
        newRect = Rect(srcRect)
        dx = dx*mint if isect else dx
        newRect.move_ip(dx,0)
        return newRect

    @staticmethod
    def collideAsRect(src,dst):
        return dst

    '''
    @staticmethod
    def rectVsRect(src,dst,otherRect):
        i,t,p = HELPER.getClosestIntersection(src,dst,otherRect)
        if not i: return dst
        dx,dy = dst.x-src.x, dst.y-src.y  
        newRect = Rect(src)
        newRect.x += dx*t
        newRect.y += dy*t
        return newRect

    @staticmethod
    def rectVsGidRects(src,dst,gidRects):
        c,mint=False,10
        for gr in gidRects:
            i,t,p = HELPER.getClosestIntersection(src,dst,gr[1])
            if i and t < mint:
                c,mint= True,t
        if not c: return dst
        dx,dy = dst.x-src.x, dst.y-src.y  
        newRect = Rect(src)
        newRect.move_ip(dx*mint,dy*mint)
        newRect.move_ip( -dx/abs(dx) if dx else 0, -dy/abs(dy) if dy else 0 )
        return newRect

    @staticmethod
    def collideAsRect(src,dst):
        expanded = src.union(dst)
        gidRects = Engine.scene.getCollGidsInAabb(expanded)
        return HELPER.rectVsGidRects(src,dst,gidRects)
    '''

        

# --------------------------------------------------------
class Engine:
    instance = None
    scene = None
    debug = False

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
            dt = 1.0/60.0
            #dt = self.clock.get_time()/1000.0
        
            # Input
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONUP:
                    for a in self.actors: 
                        a.mouseUp(pygame.mouse.get_pos())
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_F1:
                        Engine.debug = not Engine.debug
                        
            self.KEYPRESSED = pygame.key.get_pressed()
            if self.KEYPRESSED[K_ESCAPE]: break
            nextkey -= dt
            self.SCREEN.fill(self.bgColor)
            self.update(dt)
            self.draw()

#-----------------------------------------------------------
class BhBlit(Behavior):
    def __init__(self,actor,worldSpace=False):
        super(BhBlit,self).__init__(actor)
        self.worldSpace=worldSpace

    def _blitFuncOp(self,tgt,src,r,op,a):
        if self.worldSpace:
            top,left = Engine.scene.fromWsToSs(r[0],r[1])
            r = (top,left,r[2],r[3])
        tgt.blit(src,r,a)

    def _blitFuncAl(self,tgt,src,r,op,a):
        tl = r.topleft
        if self.worldSpace:
            top,left = Engine.scene.fromWsToSs(r[0],r[1])
            tl = (top,left)
        HELPER.blitAlpha(tgt,src,tl,a,a)

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

# --------------------------------------------------------
class BhSceneCameraFollowActor(Behavior):
    def __init__(self,sceneActor,targetActor):
        super(BhSceneCameraFollowActor,self).__init__(sceneActor)
        self.targetActor = targetActor

    def update(self,dt):
        w,h = self.targetActor.rect.size
        self.actor.tgtCamWsX = self.targetActor.rect.left+w/2
        self.actor.tgtCamWsY = self.targetActor.rect.top+h/2
        self.updateSmooth(dt)

    def updateSmooth(self,dt):
        difX = self.actor.tgtCamWsX-self.actor.camWsX 
        difY = self.actor.tgtCamWsY-self.actor.camWsY
        if abs(difX) > 6:
            if difX < 0 : difX = min(-AcScene.SCROLL_LIMIT_SP,difX)
            else: difX = max(AcScene.SCROLL_LIMIT_SP,difX)
            self.actor.camWsX += difX*dt
        if abs(difY) > 6:
            if difY < 0 : difY = min(-AcScene.SCROLL_LIMIT_SP,difY)
            else: difY = max(AcScene.SCROLL_LIMIT_SP,difY)
            self.actor.camWsY += difY*dt       

# --------------------------------------------------------
class BhSceneCameraScrollByInput(Behavior):
    def __init__(self,sceneActor):
        super(BhSceneCameraScrollByInput,self).__init__(sceneActor)
    
    def update(self,dt):
        keys = Engine.instance.KEYPRESSED
        if keys[K_LEFT]     : self.actor.tgtCamWsX -= 200.0*dt
        elif keys[K_RIGHT]  : self.actor.tgtCamWsX += 200.0*dt
        if keys[K_UP]       : self.actor.tgtCamWsY -= 200.0*dt
        elif keys[K_DOWN]   : self.actor.tgtCamWsY += 200.0*dt
        self.actor.camWsX = self.actor.tgtCamWsX
        self.actor.camWsY = self.actor.tgtCamWsY

# --------------------------------------------------------
class AcScene(Actor):
    SCROLL_LIMIT_SP = 120.0
    LAYER_FOREGROUND=0
    LAYER_COLLISION=1
    def __init__(self,tmxfile,engine,tilesCount=None):
        super(AcScene,self).__init__(engine)
        self.tile_map = load_pygame(tmxfile)
        self.tgtCamWsX, self.tgtCamWsY = 0, 0
        self.camWsX, self.camWsY= 0, 0        
        Engine.scene = self
        vr = self.engine.virtualRes
        self.vrHalfX, self.vrHalfY = vr[0]/2, vr[1]/2
        self.tw, self.th = self.tile_map.tilewidth, self.tile_map.tileheight
        if tilesCount:
            self.vrTw,self.vrTh = tilesCount[0]+1, tilesCount[1]+1
        else:
            self.vrTw, self.vrTh = vr[0]/self.tw+1, vr[1]/self.th+1

    def update(self,dt):
        super(AcScene,self).update(dt)
        #self.camWsX = max(self.camWsX,self.vrHalfX)         

    def draw(self):
        if Engine.debug:
            self.drawLayer([AcScene.LAYER_COLLISION])
        else:
            self.drawLayer([AcScene.LAYER_FOREGROUND]) 
        super(AcScene,self).draw()
        # test GUI
        h = (self.vrTh-1)*self.th
        r = Rect(0,h,(self.vrTw-1)*self.tw,Engine.instance.virtualRes[1]-h)        
        HELPER.drawRect(r, (40,40,200))
        pygame.draw.rect(self.engine.SCREEN,(30,30,160),r)
        pygame.draw.rect(self.engine.SCREEN,(200,200,200),r,1)

    def fromWsToSs(self,wsX,wsY):
        '''Transform from world space pixel coords to screen space pixel coords'''
        tlWsX, tlWsY = self.camWsX-self.vrHalfX, self.camWsY-self.vrHalfY
        return wsX-tlWsX, wsY-tlWsY

    def fromWsToTs(self,wsX,wsY):
        '''Transform from World Space pixel coordinates to Tile Space indices'''
        tsX = wsX / self.tile_map.tilewidth
        tsY = wsY / self.tile_map.tileheight
        return int(math.floor(tsX)), int(math.floor(tsY))

    def fromTsToGid(self,layerNdx,tsX,tsY):
        '''Transform from Tile Space indices coordinates to Gid'''
        w, h = self.tile_map.width, self.tile_map.height
        if tsX<0 or tsY<0 or tsX>=w or tsY>=h: 
            return 0
        layer = self.tile_map.layers[layerNdx]
        return layer.data[tsY][tsX]

    def getInitSpawn(self,name="initspawn"):
        for o in self.tile_map.objects:
            if o.name == name:
                return o.x, o.y
        return 0,0

    def fromTsToTileRect(self,tsX,tsY):
        w,h=self.tw,self.th
        return (tsX*w, tsY*h, w, h)

    def getCollGidsInAabb(self,aabb):
        '''Returns a set of collision Gids that the aabb touches'''
        x0,y0 = self.fromWsToTs(aabb.left, aabb.top)
        x1,y1 = self.fromWsToTs(aabb.right, aabb.bottom)
        gids = Set([])
        g=0
        for j in range(y0,y1+1):
            for i in range(x0,x1+1):
                g = self.fromTsToCollGid(i,j)
                if g in HELPER.COLLIDERS: 
                    gids.add( (g,self.fromTsToTileRect(i,j)) )
        return gids

    def getCollGidsInSegment(self,seg):
        #build aabb out of segment
        f,t = seg[0], seg[1]
        segAabb = Rect( f, (t[0]-f[0], t[1]-f[1]) )
        segAabb.normalize()
        return self.getCollGidsInAabb(segAabb)

    def fromTsToCollGid(self,tsX,tsY):
        gid = self.fromTsToGid(AcScene.LAYER_COLLISION,tsX,tsY)
        if not gid: return gid
        return self.tile_map.tiledgidmap[gid]-1
        
    def drawLayer(self,layers):
        images = self.tile_map.images        
        tw,th = self.tw, self.th
        vr = self.engine.virtualRes
        tlWsX, tlWsY = self.camWsX-self.vrHalfX, self.camWsY-self.vrHalfY
        startTsX, startTsY = self.fromWsToTs(tlWsX, tlWsY)
        ox, oy = tlWsX % tw, tlWsY % th
        ox = -ox
        oy = -oy
        r = Rect( ox, oy, tw, th )
        tsY = startTsY
        for iY in range(0,self.vrTh):
            tsX = startTsX
            r.x = ox
            for iX in range(0,self.vrTw):
                for layerNdx in layers:
                    gid = self.fromTsToGid(layerNdx,tsX,tsY)
                    if gid:
                        self.engine.SCREEN.blit(images[gid], r)
                r.x += tw
                tsX += 1
            tsY += 1
            r.y += th

# --------------------------------------------------------
class BhSpriteAnim(Behavior):
    def __init__(self,actor,imgName, rects,fps):
        super(BhSpriteAnim,self).__init__(actor)
        self.actor.img = self.actor.engine.loadImage(imgName)
        self.actor.area = rects
        self.actor.areaIndex = 0
        self.period = 1.0/fps
        self.t = self.period

    def update(self,dt):
        self.t -= dt
        if self.t <= 0.0:
            self.actor.areaIndex = (self.actor.areaIndex + 1 ) % len(self.actor.area)
            self.t += self.period

#----------------------------------------------------------------------
class BEHAVIORS:
    engine = None

    @staticmethod
    def createText(text,topleft,fontname="type_writer.ttf",size=14):
        assert BEHAVIORS.engine
        a = Actor(BEHAVIORS.engine)
        a.addBehavior(BhText(a,text,topleft,fontname,size))
        a.addBehavior(BhSequence(a,
          [BhMoveTo(a,(100,200),3.0), 
           BhMoveTo(a,(100,300),3.0), 
           BhDestroyActor(a,10)]))
        a.addBehavior(BhBlit(a,True))
        BEHAVIORS.engine.addActor(a)


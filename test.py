from pygame import Rect
import turtle
from turtle import *

# sparkster
# sfII ending theme
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

def fractionToWs(seg,f):
	d = (seg[1][0] - seg[0][0], seg[1][1] - seg[0][1])
	return (seg[0][0] + d[0] * f, seg[0][1] + d[1] * f)

def segmentVsManySegments(seg,segs):
  i,m = False,10 # t should be always 0-1
  for s in segs:
    c,t = segmentVsSegment(seg,s)
    if c and t < m:
      m = t
      i = True
  return i,m

def segmentVsRect(seg,r):
  rs = getRectSegments(r)
  return segmentVsManySegments(seg,rs)

def getRectSegments(r):
	return [ (r.topleft,r.topright), 
			 (r.topright,r.bottomright), 
			 (r.bottomright,r.bottomleft), 
			 (r.bottomleft, r.topleft) ]

def getRectSweepSegments(src,dst):
	return [ (src.topleft,dst.topleft), 
			 (src.topright, dst.topright),
			 (src.bottomright, dst.bottomright),
			 (src.bottomleft, dst.bottomleft) ]

def getClosestIntersection(src,dirOrDst,r):
  if len(dirOrDst)==2:
    dst = Rect(dirOrDst)
    dst.move_ip(dir)
  else:
    dst = dirOrDst
  sweepSegs = getRectSweepSegments(src,dst)
  tgtSegs = getRectSegments(r)
  isect,closest, cindex = False,10,-1  
  for j in range(0, len(sweepSegs)):
    i,t = segmentVsManySegments(sweepSegs[j],tgtSegs)
    if i and t < closest:
      isect, closest, cindex = True, t, j
  return isect,closest, fractionToWs(sweepSegs[cindex],closest) if isect else (0,0)

def rectVsRect(src,dst,otherRect):
  i,t,p = getClosestIntersection(src,dst,otherRect)
  if not i: return dst
  dx,dy = dst.x-src.x, dst.y-src.y  
  newRect = Rect(src)
  newRect.x += dx*t
  newRect.y += dy*t
  return newRect

def drawRect(r,color):
  pu()
  pencolor(color)
  setpos(r.topleft)
  pd()
  setpos(r.topright)
  setpos(r.bottomright)
  setpos(r.bottomleft)
  setpos(r.topleft)
	
def drawSeg(s,color):
  pu()
  pencolor(color)
  setpos(s[0])
  pd()
  setpos(s[1])

def drawDot(p,color,size=8):
  pu()
  setpos(p)
  dot(size,color)


def testWithTurtle():
  src = Rect(16, 3, 16, 16)
  dst = Rect(26, 13, 16, 16)
  block = Rect(24, 24, 16, 16)
  nr = rectVsRect(src,dst,block)
  
  turtle.screensize(96,96)
  turtle.setworldcoordinates(0,96,96,0)
  turtle.reset()
  drawRect(src,"red")
  drawRect(dst,"red")
  drawRect(block,"black")
  drawRect(nr,"green")

if __name__=="__main__":
  testWithTurtle()
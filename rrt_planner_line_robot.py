import time
import random
import drawSample
import math
import _tkinter
import sys
import imageToRects


visualize = 1
prompt_before_next=1  # ask before re-running sonce solved
SMALLSTEP = 9 # what our "local planner" can handle.
SMALLANGLE = math.pi/12


XMAX=1800
YMAX=1000
G = [  [ 0 ]  , [] ]   # nodes, edges


s,obstacles = imageToRects.imageToRects(sys.argv[1])

XMAX = s[0]
YMAX = s[1]
       


# goal/target
tx = 800
ty = 150
ta = 0
# start
start_x = 100
start_y = 630
start_angle = 0
LENGTH = 21

vertices = [ [start_x,start_y,start_angle] ]

sigmax_for_randgen = XMAX/2.0
sigmay_for_randgen = YMAX/2.0

nodes=0
edges=1
maxvertex = 0

def drawGraph(G):
    global vertices,nodes,edges
    if not visualize: return
    for i in G[edges]:
        if len(vertices)!=1:
            canvas.polyline(  [vertices[i[0]], vertices[i[1]] ]  )


def genPoint():
    x = random.randint(0, XMAX)
    y = random.randint(0, YMAX)
    a = random.uniform(0, math.pi)
    return [x,y,a]

def genvertex():
    vertices.append( genPoint() )
    return len(vertices)-1

def pointToVertex(p):
    vertices.append( p )
    return len(vertices)-1

def pickvertex():
    return random.choice( range(len(vertices) ))

def lineFromPoints(p1,p2):
    line = []
    llsq = 0.0 # line length squared
    for i in range(len(p1)):  # each dimension
        h = p2[i] - p1[i] 
        line.append( h )
        llsq += h*h
    ll = math.sqrt(llsq)  # length
    # normalize line
    if ll <=0: return [0,0]
    for i in range(len(p1)):  # each dimension
        line[i] = line[i]/ll
    return line

def pointPointDistance(p1,p2):
    """ Return the distance between a pair of points (L2 norm). """
    llsq = 0.0 # line length squared
    # faster, only for 2D
    h = p2[0] - p1[0] 
    llsq = llsq + (h*h)
    h = p2[1] - p1[1] 
    llsq = llsq + (h*h)
    return math.sqrt(llsq)

    for i in range(len(p1)):  # each dimension, general case
        h = p2[i] - p1[i] 
        llsq = llsq + (h*h)
    return math.sqrt(llsq)

def closestPointToPoint(G,p2):
    dmin = 999999999
    for v in G[nodes]:
        p1 = vertices [ v ]
        d = pointPointDistance(p1,p2)
        if d <= dmin:
            dmin = d
            close = v
    return close

def returnParent(k):
    """ Return parent note for input node k. """
    for e in G[edges]:
        if e[1]==k: 
            canvas.polyline(  [vertices[e[0]], vertices[e[1]] ], style=3  )
            return e[0]

def pickGvertex():
    try: edge = random.choice( G[edges] )
    except: return pickvertex()
    v = random.choice( edge )
    return v

def redraw():
    canvas.clear()
    canvas.markit(start_x, start_y, r=SMALLSTEP)
    canvas.markit( tx, ty, r=SMALLSTEP )
    drawGraph(G)
    for o in obstacles: canvas.showRect(o, outline='blue', fill='blue')
    canvas.delete("debug")

def ccw(A,B,C):
    """ Determine if three points are listed in a counterclockwise order.
    For three points A, B and C. If the slope of the line AB is less than 
    the slope of the line AC then the three points are in counterclockwise order.
    See:  http://compgeom.cs.uiuc.edu/~jeffe/teaching/373/notes/x06-sweepline.pdf
    """
    return (C[1]-A[1])*(B[0]-A[0]) > (B[1]-A[1])*(C[0]-A[0])

def intersect(A,B,C,D):
        """ do lines AB and CD intersect? """
        i = ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)
       
        return i
        

def lineHitsRect(p1,p2,r):
   rline = ( (r[0],r[1]), (r[0],r[3]) )
   if intersect( p1, p2, rline[0], rline[1] ): return 1
   rline = ( (r[0],r[1]), (r[2],r[1]) )
   if intersect( p1, p2, rline[0], rline[1] ): return 1
   rline = ( (r[0],r[3]), (r[2],r[3]) )
   if intersect( p1, p2, rline[0], rline[1] ): return 1
   rline = ( (r[2],r[1]), (r[2],r[3]) )
   if intersect( p1, p2, rline[0], rline[1] ): return 1

   return 0

def inRect(p,rect,dilation):
   """ Return 1 in p is inside rect, dilated by dilation (for edge cases). """
   if p[0]<rect[0]-dilation: return 0
   if p[1]<rect[1]-dilation: return 0
   if p[0]>rect[2]+dilation: return 0
   if p[1]>rect[3]+dilation: return 0
   return 1
def boldPath(node):
    # display the path from input node to the root
    while node != G[nodes][0]:
        node = returnParent(node)


def obstacleFree(x1, x2):
    for o in obstacles:
        if lineHitsRect(x1,x2,o): return 0
    return 1

def getEndPoints(x):
    dx = int(LENGTH/2*math.cos(x[2]))
    dy = int(LENGTH/2*math.sin(x[2]))

    p1 = [x[0] + dx, x[1] + dy]
    p2 = [x[0] - dx, x[1] - dy]

    return p1, p2

def findAngle(xStart, xGoal):
  
    angle = math.atan2((xGoal[1]-xStart[1]) , (xGoal[0] - xStart[0]))
    return angle

def findRotation(aStart, aGoal):
    aDifference = aGoal - aStart
    if aDifference >= 0 :
        if aDifference > SMALLANGLE:
            return aStart + SMALLANGLE
        else : 
            return aGoal
    else :
        return aStart - SMALLANGLE

def closeEnough(sx,sy,tx,ty):
    if (abs(sx-tx) < SMALLSTEP) & (abs(sy- ty)<SMALLSTEP):
        return 1
    else: return 

def takeStep(xStart, xGoal):
    theta = findAngle(xStart, xGoal)
    rotate = findRotation(xStart[2], xGoal[2])
    xNew = [xStart[0] + SMALLSTEP*math.cos(theta), xStart[1] + SMALLSTEP*math.sin(theta), rotate]
    return xNew
def rrt_search(G, tx, ty, ta):
    counter = 0
    while (1) :
        vRand = genPoint()
        xNearest = closestPointToPoint(G, vRand)
        vNearest = vertices[xNearest]
        vNew = takeStep(vNearest, vRand)
        if (vNew[0]<0) | (vNew[0]>XMAX) | (vNew[1]<0) | (vNew[1]>YMAX):
            continue
        vNearestEndpoints = getEndPoints(vNearest)
        vNewEndpoints = getEndPoints(vNew)
        if (obstacleFree(vNearest, vNew) != 0) and (obstacleFree(vNearestEndpoints[0], vNewEndpoints[0]) != 0) and (obstacleFree(vNearestEndpoints[1], vNewEndpoints[1]) != 0):
            node = pointToVertex(vNew)
            G[nodes].append(node)
            G[edges].append((xNearest, node))
            counter += 1
            if(counter % 100 == 0):
                drawGraph(G)
                canvas.events()
            if (closeEnough(vNew[0], vNew[1],tx,ty) == 1):
                boldPath(node)
                print counter
                drawGraph(G)
                canvas.events()
                break

if visualize:
    canvas = drawSample.SelectRect(xmin=0,ymin=0,xmax=XMAX ,ymax=YMAX, nrects=0, keepcontrol=0)#, rescale=800/1800.)


if 0:  # line intersection testing
        obstacles.append( [ 75,60,125,500 ] )  # tall vertical
        for o in obstacles: canvas.showRect(o, outline='red', fill='blue')
        lines = [
           ( (70,50), (150,150) ),
           ( (50,50), (150,20) ),
           ( (20,20), (200,200) ),
           ( (300,300), (20, 200)  ),
           ( (300,300), (280, 90)  ),
           ]
        for l in lines:
           for o in obstacles:
              lineHitsRect(l[0],l[1],o)
        canvas.mainloop()
    

if 0:
    # random obstacle field
    for nobst in range(0,6000):
        wall_discretization=SMALLSTEP*2  # walls are on a regular grid.
        wall_lengthmax=10.  # fraction of total (1/lengthmax)
        x = wall_discretization*int(random.random()*XMAX/wall_discretization)
        y = wall_discretization*int(random.random()*YMAX/wall_discretization)
        #length = YMAX/wall_lengthmax
        length = SMALLSTEP*2
        if random.choice([0,1]) >0:
            obstacles.append( [ x,y,x+SMALLSTEP,y+10+length ] )  # vertical
        else:
            obstacles.append( [ x,y,x+10+length,y+SMALLSTEP ] )  # horizontal
else:
  if 0:
    # hardcoded simple obstacles
    obstacles.append( [ 300,0,400,95 ] )  # tall vertical
    # slightly hard
    obstacles.append( [ 300,805,400,YMAX ] )  # tall vertical
    #obstacles.append( [ 300,400,1300,430 ] )
    # hard
    obstacles.append( [ 820,220,900,940 ] )
    obstacles.append( [ 300,0,  400,95 ] )  # tall vertical
    obstacles.append( [ 300,100,400,YMAX ] )  # tall vertical
    obstacles.append( [ 200,300,800,400 ] )  # middle horizontal
    obstacles.append( [ 380,500,700,550 ] )
    # very hard
    obstacles.append( [ 705,500,XMAX,550 ] )




if visualize:
    for o in obstacles: canvas.showRect(o, outline='red', fill='blue')


maxvertex += 1

while 1:
    # graph G
    G = [  [ 0 ]  , [] ]   # nodes, edges
    vertices = [[100, 630, 0], [110, 640, 0]]
    redraw()

    G[edges].append( (0,1) )
    G[nodes].append(1)
    if visualize: canvas.markit( tx, ty, r=SMALLSTEP )

    drawGraph(G)
    rrt_search(G, tx, ty, ta)
    break

#canvas.showRect(rect,fill='red')

if visualize:
    canvas.mainloop()

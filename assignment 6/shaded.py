from PIL import Image
import os

canvas_width = 800
canvas_height = 800

img = Image.new("RGB",(canvas_width,canvas_height),"white")
pixels = img.load()

class Color:
    def __init__(self,r,g,b):
        self.r=r
        self.g=g
        self.b=b
    def mul(self,n):
        return Color(self.r*n,self.g*n,self.b*n)

class Pt:
    def __init__(self,x,y,h=0):
        self.x=int(x)
        self.y=int(y)
        self.h=h

class Vertex:
    def __init__(self,x,y,z):
        self.x=x
        self.y=y
        self.z=z

def PutPixel(x,y,color):
    x=int(canvas_width/2+x)
    y=int(canvas_height/2-y-1)
    if x<0 or x>=canvas_width or y<0 or y>=canvas_height:
        return
    pixels[x,y]=(int(color.r),int(color.g),int(color.b))

def Interpolate(i0,d0,i1,d1):
    if i0==i1:
        return [d0]
    values=[]
    a=(d1-d0)/(i1-i0)
    d=d0
    for i in range(i0,i1+1):
        values.append(d)
        d+=a
    return values

def DrawLine(p0,p1,color):
    dx=p1.x-p0.x
    dy=p1.y-p0.y

    if abs(dx)>abs(dy):
        if dx<0:
            p0,p1=p1,p0
        ys=Interpolate(p0.x,p0.y,p1.x,p1.y)
        for x in range(p0.x,p1.x+1):
            PutPixel(x,int(ys[x-p0.x]),color)
    else:
        if dy<0:
            p0,p1=p1,p0
        xs=Interpolate(p0.y,p0.x,p1.y,p1.x)
        for y in range(p0.y,p1.y+1):
            PutPixel(int(xs[y-p0.y]),y,color)

def DrawShadedTriangle(p0,p1,p2,color):

    if p1.y<p0.y:
        p0,p1=p1,p0
    if p2.y<p0.y:
        p0,p2=p2,p0
    if p2.y<p1.y:
        p1,p2=p2,p1

    x01=Interpolate(p0.y,p0.x,p1.y,p1.x)
    h01=Interpolate(p0.y,p0.h,p1.y,p1.h)

    x12=Interpolate(p1.y,p1.x,p2.y,p2.x)
    h12=Interpolate(p1.y,p1.h,p2.y,p2.h)

    x02=Interpolate(p0.y,p0.x,p2.y,p2.x)
    h02=Interpolate(p0.y,p0.h,p2.y,p2.h)

    x01.pop()
    h01.pop()

    x012=x01+x12
    h012=h01+h12

    m=len(x02)//2

    if x02[m]<x012[m]:
        x_left=x02
        x_right=x012
        h_left=h02
        h_right=h012
    else:
        x_left=x012
        x_right=x02
        h_left=h012
        h_right=h02

    for y in range(p0.y,p2.y+1):

        xl=int(x_left[y-p0.y])
        xr=int(x_right[y-p0.y])

        h_segment=Interpolate(xl,h_left[y-p0.y],xr,h_right[y-p0.y])

        for x in range(xl,xr+1):
            h=h_segment[x-xl]
            PutPixel(x,y,color.mul(h))

viewport_size=1
projection_plane_z=1

def ViewportToCanvas(x,y):
    return Pt(x*canvas_width/viewport_size,y*canvas_height/viewport_size)

def ProjectVertex(v):
    x=v.x*projection_plane_z/v.z
    y=v.y*projection_plane_z/v.z
    return ViewportToCanvas(x,y)

vA=Vertex(-2,-0.5,5)
vB=Vertex(-2,0.5,5)
vC=Vertex(-1,0.5,5)
vD=Vertex(-1,-0.5,5)

vAb=Vertex(-2,-0.5,6)
vBb=Vertex(-2,0.5,6)
vCb=Vertex(-1,0.5,6)
vDb=Vertex(-1,-0.5,6)

A=ProjectVertex(vA)
B=ProjectVertex(vB)
C=ProjectVertex(vC)
D=ProjectVertex(vD)

Ab=ProjectVertex(vAb)
Bb=ProjectVertex(vBb)
Cb=ProjectVertex(vCb)
Db=ProjectVertex(vDb)

RED=Color(255,0,0)
GREEN=Color(0,255,0)
BLUE=Color(0,0,255)

DrawLine(A,B,BLUE)
DrawLine(B,C,BLUE)
DrawLine(C,D,BLUE)
DrawLine(D,A,BLUE)

DrawLine(Ab,Bb,RED)
DrawLine(Bb,Cb,RED)
DrawLine(Cb,Db,RED)
DrawLine(Db,Ab,RED)

DrawLine(A,Ab,GREEN)
DrawLine(B,Bb,GREEN)
DrawLine(C,Cb,GREEN)
DrawLine(D,Db,GREEN)

p0 = Pt(-50, -250, 0.3)
p1 = Pt(350, 50, 0.1)
p2 = Pt(170, 250, 1.0)

DrawShadedTriangle(p0,p1,p2,Color(0,255,0))

img.save("shaded_triangle.png")
os.system("code shaded_triangle.png")
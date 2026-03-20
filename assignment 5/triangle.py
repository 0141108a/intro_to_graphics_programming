from PIL import Image
import os

canvas_width = 600
canvas_height = 600

img = Image.new("RGB", (canvas_width, canvas_height), "white")
pixels = img.load()

class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

class Pt:
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)

def PutPixel(x, y, color):
    x = int(canvas_width / 2 + x)
    y = int(canvas_height / 2 - y - 1)
    if x < 0 or x >= canvas_width or y < 0 or y >= canvas_height:
        return
    pixels[x, y] = (int(color.r), int(color.g), int(color.b))

def Interpolate(i0, d0, i1, d1):
    if i0 == i1:
        return [d0]
    values = []
    a = (d1 - d0) / (i1 - i0)
    d = d0
    for i in range(i0, i1 + 1):
        values.append(d)
        d += a
    return values

def DrawLine(p0, p1, color):
    dx = p1.x - p0.x
    dy = p1.y - p0.y
    if abs(dx) > abs(dy):
        if dx < 0:
            p0, p1 = p1, p0
        ys = Interpolate(p0.x, p0.y, p1.x, p1.y)
        for x in range(p0.x, p1.x + 1):
            PutPixel(x, int(ys[x - p0.x]), color)
    else:
        if dy < 0:
            p0, p1 = p1, p0
        xs = Interpolate(p0.y, p0.x, p1.y, p1.x)
        for y in range(p0.y, p1.y + 1):
            PutPixel(int(xs[y - p0.y]), y, color)

def DrawWireframeTriangle(p0, p1, p2, color):
    DrawLine(p0, p1, color)
    DrawLine(p1, p2, color)
    DrawLine(p0, p2, color)

def DrawFilledTriangle(p0, p1, p2, color):
    if p1.y < p0.y:
        p0, p1 = p1, p0
    if p2.y < p0.y:
        p0, p2 = p2, p0
    if p2.y < p1.y:
        p1, p2 = p2, p1

    x01 = Interpolate(p0.y, p0.x, p1.y, p1.x)
    x12 = Interpolate(p1.y, p1.x, p2.y, p2.x)
    x02 = Interpolate(p0.y, p0.x, p2.y, p2.x)

    x01.pop()
    x012 = x01 + x12

    m = len(x02) // 2

    if x02[m] < x012[m]:
        x_left = x02
        x_right = x012
    else:
        x_left = x012
        x_right = x02

    for y in range(p0.y, p2.y + 1):
        xl = int(x_left[y - p0.y])
        xr = int(x_right[y - p0.y])
        for x in range(xl, xr + 1):
            PutPixel(x, y, color)

p0 = Pt(-200, -250)
p1 = Pt(200, 50)
p2 = Pt(20, 250)

DrawFilledTriangle(p0, p1, p2, Color(0, 255, 0))
DrawWireframeTriangle(p0, p1, p2, Color(0, 0, 0))

img.save("triangle.png")
os.system("code triangle.png")

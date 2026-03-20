from PIL import Image

width = 200
height = 200

canvas = Image.new("RGB", (width, height), (255, 255, 255))
pixels = canvas.load()

def PutPixel(x, y, r, g, b):
    if 0 <= x < width and 0 <= y < height:
        pixels[x, y] = (r, g, b)

PutPixel(100, 100, 255, 0, 0)  
PutPixel(101, 100, 0, 255, 0)   
PutPixel(102, 100, 0, 0, 255)   

canvas.save("canvas.png")
from PIL import Image
import math
import os

class Vec:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    def __sub__(self, other):
        return Vec(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def length(self):
        return math.sqrt(self.dot(self))
    
    def normalize(self):
        l = self.length()
        return Vec(self.x/l, self.y/l, self.z/l)

class Color:
    def __init__(self, r, g, b):
        self.r = int(max(0, min(255, r)))
        self.g = int(max(0, min(255, g)))
        self.b = int(max(0, min(255, b)))

class Sphere:
    def __init__(self, center, radius, color):
        self.center = center
        self.radius = radius
        self.color = color

def intersect_ray_sphere(origin, direction, sphere):
    oc = origin - sphere.center
    k1 = direction.dot(direction)
    k2 = 2 * oc.dot(direction)
    k3 = oc.dot(oc) - sphere.radius * sphere.radius
    discriminant = k2 * k2 - 4 * k1 * k3
    
    if discriminant < 0:
        return (float('inf'), float('inf'))
    
    t1 = (-k2 + math.sqrt(discriminant)) / (2 * k1)
    t2 = (-k2 - math.sqrt(discriminant)) / (2 * k1)
    return (t1, t2)

def trace_ray(origin, direction, min_t, max_t, spheres):
    closest_t = float('inf')
    closest_sphere = None
    
    for sphere in spheres:
        ts = intersect_ray_sphere(origin, direction, sphere)
        
        if ts[0] < closest_t and min_t < ts[0] < max_t:
            closest_t = ts[0]
            closest_sphere = sphere
        
        if ts[1] < closest_t and min_t < ts[1] < max_t:
            closest_t = ts[1]
            closest_sphere = sphere
    
    if closest_sphere is None:
        return Color(255, 255, 255)
    
    return closest_sphere.color

def canvas_to_viewport(x, y, canvas_width, canvas_height, viewport_size, projection_plane_z):
    return Vec(
        x * viewport_size / canvas_width,
        y * viewport_size / canvas_height,
        projection_plane_z
    )

canvas_width = 600
canvas_height = 600
viewport_size = 1
projection_plane_z = 1
camera_position = Vec(0, 0, 0)

spheres = [
    Sphere(Vec(0, -1, 3), 1, Color(255, 0, 0)),
    Sphere(Vec(-2, 0, 4), 1, Color(0, 255, 0)),
    Sphere(Vec(2, 0, 4), 1, Color(0, 0, 255))
]

def render():
    img = Image.new('RGB', (canvas_width, canvas_height), 'white')
    pixels = img.load()
    
    for x in range(-canvas_width//2, canvas_width//2):
        for y in range(-canvas_height//2, canvas_height//2):
            direction = canvas_to_viewport(
                x, y, 
                canvas_width, canvas_height, 
                viewport_size, projection_plane_z
            )
            direction = direction.normalize()
            color = trace_ray(camera_position, direction, 1, float('inf'), spheres)
            
            px = x + canvas_width//2
            py = canvas_height//2 - y - 1
            
            if 0 <= px < canvas_width and 0 <= py < canvas_height:
                pixels[px, py] = (color.r, color.g, color.b)
    
    return img

if __name__ == "__main__":
    image = render()
    filename = "raytracer.png"
    image.save(filename)
    os.system(f"code {filename}")
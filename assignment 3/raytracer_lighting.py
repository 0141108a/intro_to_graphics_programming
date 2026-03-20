from PIL import Image
import math
import os

class Vec:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    def __add__(self, other):
        return Vec(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vec(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar):
        return Vec(self.x * scalar, self.y * scalar, self.z * scalar)
    
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
    
    def __add__(self, other):
        return Color(self.r + other.r, self.g + other.g, self.b + other.b)
    
    def __mul__(self, scalar):
        return Color(self.r * scalar, self.g * scalar, self.b * scalar)

class Sphere:
    def __init__(self, center, radius, color, specular=-1):
        self.center = center
        self.radius = radius
        self.color = color
        self.specular = specular

class Light:
    AMBIENT = "ambient"
    POINT = "point"
    DIRECTIONAL = "directional"
    
    def __init__(self, type, intensity, position=None, direction=None):
        self.type = type
        self.intensity = intensity
        self.position = position
        self.direction = direction

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

def compute_lighting(point, normal, view, specular, lights):
    intensity = 0.0
    
    for light in lights:
        if light.type == Light.AMBIENT:
            intensity += light.intensity
        else:
            if light.type == Light.POINT:
                L = light.position - point
                t_max = 1
            else:
                L = light.direction.normalize()
                t_max = float('inf')
            
            n_dot_l = normal.dot(L)
            if n_dot_l > 0:
                intensity += light.intensity * n_dot_l / (normal.length() * L.length())
            
            if specular != -1:
                R = normal * (2 * normal.dot(L)) - L
                r_dot_v = R.dot(view)
                if r_dot_v > 0:
                    intensity += light.intensity * math.pow(r_dot_v / (R.length() * view.length()), specular)
    
    return intensity

def trace_ray(origin, direction, min_t, max_t, spheres, lights):
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
    
    point = origin + direction * closest_t
    normal = point - closest_sphere.center
    normal = normal.normalize()
    view = direction * -1
    
    lighting = compute_lighting(point, normal, view, closest_sphere.specular, lights)
    
    return closest_sphere.color * lighting

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
    Sphere(Vec(0, -1, 3), 1, Color(255, 0, 0), 500),
    Sphere(Vec(-2, 0, 4), 1, Color(0, 255, 0), 10),
    Sphere(Vec(2, 0, 4), 1, Color(0, 0, 255), 500)
]

lights = [
    Light(Light.AMBIENT, 0.2),
    Light(Light.POINT, 0.6, Vec(2, 1, 0)),
    Light(Light.DIRECTIONAL, 0.2, None, Vec(1, 4, 4))
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
            color = trace_ray(camera_position, direction, 1, float('inf'), spheres, lights)
            
            px = x + canvas_width//2
            py = canvas_height//2 - y - 1
            
            if 0 <= px < canvas_width and 0 <= py < canvas_height:
                pixels[px, py] = (color.r, color.g, color.b)
    
    return img

if __name__ == "__main__":
    image = render()
    filename = "raytracer_lighting.png"
    image.save(filename)
    os.system(f"code {filename}")
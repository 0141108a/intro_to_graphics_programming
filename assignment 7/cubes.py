from PIL import Image
import math
import os

canvas_width = 800
canvas_height = 800

img = Image.new("RGB", (canvas_width, canvas_height), "white")
pixels = img.load()


class Color:
    def __init__(self, r, g, b):
        self.r = int(r)
        self.g = int(g)
        self.b = int(b)

    def mul(self, n):
        return Color(self.r * n, self.g * n, self.b * n)


class Pt:
    def __init__(self, x, y, h=0):
        self.x = int(x)
        self.y = int(y)
        self.h = h


class Vertex:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def mul(self, n):
        return Vertex(self.x * n, self.y * n, self.z * n)


class Vertex4:
    def __init__(self, x, y, z, w):
        self.x = x
        self.y = y
        self.z = z
        self.w = w


class Mat4x4:
    def __init__(self, data):
        self.data = data


Identity4x4 = Mat4x4([
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1]
])


class Triangle:
    def __init__(self, v0, v1, v2, color):
        self.v0 = v0
        self.v1 = v1
        self.v2 = v2
        self.color = color


class Model:
    def __init__(self, vertices, triangles):
        self.vertices = vertices
        self.triangles = triangles


class Instance:
    def __init__(self, model, position, orientation=None, scale=1.0):
        self.model = model
        self.position = position
        self.orientation = orientation if orientation else Identity4x4
        self.scale = scale

        self.transform = MultiplyMM4(
            MakeTranslationMatrix(self.position),
            MultiplyMM4(self.orientation, MakeScalingMatrix(self.scale))
        )


class Camera:
    def __init__(self, position, orientation):
        self.position = position
        self.orientation = orientation


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


viewport_size = 1
projection_plane_z = 1


def ViewportToCanvas(x, y):
    return Pt(
        x * canvas_width / viewport_size,
        y * canvas_height / viewport_size
    )


def ProjectVertex(v):
    return ViewportToCanvas(
        v.x * projection_plane_z / v.z,
        v.y * projection_plane_z / v.z
    )


def MakeOYRotationMatrix(degrees):
    cos_v = math.cos(math.radians(degrees))
    sin_v = math.sin(math.radians(degrees))

    return Mat4x4([
        [cos_v, 0, -sin_v, 0],
        [0,     1, 0,      0],
        [sin_v, 0, cos_v,  0],
        [0,     0, 0,      1]
    ])


def MakeTranslationMatrix(translation):
    return Mat4x4([
        [1, 0, 0, translation.x],
        [0, 1, 0, translation.y],
        [0, 0, 1, translation.z],
        [0, 0, 0, 1]
    ])


def MakeScalingMatrix(s):
    return Mat4x4([
        [s, 0, 0, 0],
        [0, s, 0, 0],
        [0, 0, s, 0],
        [0, 0, 0, 1]
    ])


def MultiplyMV(mat, vec):
    result = [0, 0, 0, 0]
    v = [vec.x, vec.y, vec.z, vec.w]

    for i in range(4):
        for j in range(4):
            result[i] += mat.data[i][j] * v[j]

    return Vertex4(result[0], result[1], result[2], result[3])


def MultiplyMM4(a, b):
    result = Mat4x4([
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ])

    for i in range(4):
        for j in range(4):
            for k in range(4):
                result.data[i][j] += a.data[i][k] * b.data[k][j]

    return result


def Transposed(mat):
    result = Mat4x4([
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ])

    for i in range(4):
        for j in range(4):
            result.data[i][j] = mat.data[j][i]

    return result


def RenderTriangle(triangle, projected):
    DrawWireframeTriangle(
        projected[triangle.v0],
        projected[triangle.v1],
        projected[triangle.v2],
        triangle.color
    )


def RenderModel(model, transform):
    projected = []

    for vertex in model.vertices:
        vertex_h = Vertex4(vertex.x, vertex.y, vertex.z, 1)
        transformed = MultiplyMV(transform, vertex_h)
        projected.append(ProjectVertex(transformed))

    for triangle in model.triangles:
        RenderTriangle(triangle, projected)


def RenderScene(camera, instances):
    camera_matrix = MultiplyMM4(
        Transposed(camera.orientation),
        MakeTranslationMatrix(camera.position.mul(-1))
    )

    for instance in instances:
        transform = MultiplyMM4(camera_matrix, instance.transform)
        RenderModel(instance.model, transform)


RED = Color(255, 0, 0)
GREEN = Color(0, 255, 0)
BLUE = Color(0, 0, 255)
YELLOW = Color(255, 255, 0)
PURPLE = Color(255, 0, 255)
CYAN = Color(0, 255, 255)

vertices = [
    Vertex(1, 1, 1),
    Vertex(-1, 1, 1),
    Vertex(-1, -1, 1),
    Vertex(1, -1, 1),
    Vertex(1, 1, -1),
    Vertex(-1, 1, -1),
    Vertex(-1, -1, -1),
    Vertex(1, -1, -1)
]

triangles = [
    Triangle(0, 1, 2, RED),
    Triangle(0, 2, 3, RED),
    Triangle(4, 0, 3, GREEN),
    Triangle(4, 3, 7, GREEN),
    Triangle(5, 4, 7, BLUE),
    Triangle(5, 7, 6, BLUE),
    Triangle(1, 5, 6, YELLOW),
    Triangle(1, 6, 2, YELLOW),
    Triangle(4, 5, 1, PURPLE),
    Triangle(4, 1, 0, PURPLE),
    Triangle(2, 6, 7, CYAN),
    Triangle(2, 7, 3, CYAN)
]

cube = Model(vertices, triangles)

instances = [
    Instance(cube, Vertex(-1.5, 0, 7), Identity4x4, 0.75),
    Instance(cube, Vertex(1.25, 2.5, 7.5), MakeOYRotationMatrix(195), 1.0)
]

camera = Camera(Vertex(-3, 1, 2), MakeOYRotationMatrix(-30))

RenderScene(camera, instances)

img.save("cubes.png")
os.system("code cubes.png")
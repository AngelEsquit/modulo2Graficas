import numpy as np
from math import tan, pi
from camera import Camera
import random
import pygame
from figure import Sphere, Material, Light

class Renderer:
    def __init__(self, screen):
        # Pantalla y dimensiones
        self.screen = screen
        _, _, self.width, self.height = screen.get_rect()

        # Cámara
        self.camera = Camera()

        # Configuración de proyección / viewport
        self.glViewport(0, 0, self.width, self.height)
        self.glProjection()

        # Colores base
        self.glColor(1, 1, 1)
        self.glClearColor(0, 0, 0)

        # Framebuffer para exportar a BMP (width x height x [r,g,b])
        self.frameBuffer = [[(0, 0, 0) for _ in range(self.height)] for _ in range(self.width)]

        # Escena y luces
        self.scene = []
        self.lights = []
        self.ambientLight = (0.15, 0.15, 0.15)

        # Configuración de cámara inicial alejada mirando al centro
        self.camera.position = [0, 0, 5]

        # Crear modelo (oso) usando solo esferas
        self._build_bear_scene()
        self.glClear()
        # Preparar render progresivo aleatorio
        self._init_progressive_render()

    def glViewport(self, x, y, width, height):
        self.vpX = round(x)
        self.vpY = round(y)
        self.vpWidth = round(width)
        self.vpHeight = round(height)

        self.viewportMatrix = np.matrix([[width/2, 0, 0, x + width/2],
                                          [0, height/2, 0, y + height/2],
                                          [0, 0, 0, 1]])

    def glProjection(self, n = 0.1, f = 1000, fov = 60):
        aspectRatio = self.vpWidth / self.vpHeight
        fov *= pi/180
        self.topEdge = tan(fov / 2) * n
        self.rightEdge = self.topEdge * aspectRatio

        self.nearPlane = n
        self.farPlane = f

        self.projectionMatrix = np.matrix([[n/self.rightEdge, 0, 0, 0],
                                           [0, n/self.topEdge, 0, 0],
                                           [0, 0, (f + n) / (n - f), -(2 * f * n) / (f - n)],
                                           [0, 0, -1, 0]])
        
    def glClearColor(self, r, g, b):
        self.clearColor = (r, g, b)

    def glColor(self, r, g, b):
        self.color = (r, g, b)

    def glClear(self):
        # Limpia pantalla y framebuffer con el color de fondo
        clear_rgb = tuple(int(c*255) for c in self.clearColor)
        self.screen.fill(clear_rgb)
        for x in range(self.width):
            col = self.frameBuffer[x]
            for y in range(self.height):
                col[y] = clear_rgb

    def glPoint(self, x, y, color = None):
        x = round(x)
        y = round(y)

        if (0 <= x < self.width) and (0 <= y < self.height):
            if color is None:
                color = self.color
            rgb = tuple(max(0, min(255, int(c*255))) for c in color)
            self.screen.set_at((x, self.height - y - 1), rgb)
            self.frameBuffer[x][y] = rgb

    def glLine(self, p0, p1, color = None):
        x0 = p0[0]
        y0 = p0[1]
        x1 = p1[0]
        y1 = p1[1]

        if x0 == x1 and y0 == y1:
            self.glPoint(x0, y0)
            return
        
        dy = abs(y1 - y0)
        dx = abs(x1 - x0)

        steep = dy > dx

        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1
        
        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        dy = abs(y1 - y0)
        dx = abs(x1 - x0)

        offset = 0
        limit = 0.75
        m = dy / dx if dx != 0 else 0
        y = y0

        for x in range(round(x0), round(x1) + 1):
            if steep:
                self.glPoint(y, x, self.color)
            else:
                self.glPoint(x, y, self.color)

            offset += m

            if offset >= limit:
                if y0 < y1:
                    y += 1
                else:
                    y -= 1
                
                limit += 1

    def glRender(self):
        """Render progresivo en lotes de pixeles aleatorios.
        Llamar cada frame; cuando finaliza self.render_done = True."""
        if self.render_done:
            return True

        batch = self.pixels_per_frame
        origin = np.array(self.camera.position, dtype=float)
        processed = 0
        while self.random_pixels and processed < batch:
            x, y = self.random_pixels.pop()  # pop desde el final (lista ya mezclada)
            pX = ((x + 0.5 - self.vpX) / self.vpWidth) * 2 - 1
            pY = ((y + 0.5 - self.vpY) / self.vpHeight) * 2 - 1
            pX *= self.rightEdge
            pY *= self.topEdge
            pZ = -self.nearPlane
            direction = np.array([pX, pY, pZ], dtype=float)
            direction /= np.linalg.norm(direction) or 1
            hit = self.glCastRay(origin, direction)
            if hit:
                t = hit['t']
                if t < self.zbuffer[x][y]:
                    color = self._phong(hit, origin, direction)
                    self.glPoint(x, y, color)
                    self.zbuffer[x][y] = t
            processed += 1

        if not self.random_pixels:
            self.render_done = True
            return True
        return False

    def _phong(self, hit, origin, direction):
        material = hit['material']
        point = hit['point']
        normal = hit['normal']
        view_dir = -direction
        # Ambiente
        r,g,b = material.color
        amb = np.array(self.ambientLight) * material.ka * np.array(material.color)
        result = amb
        for light in self.lights:
            L = light.position - point
            dist = np.linalg.norm(L) or 1
            L /= dist
            # Sombra simple (shadow ray)
            shadow_hit = self.glCastRay(point + normal * 1e-4, L, max_distance=dist-1e-3)
            if shadow_hit:
                continue
            diff = max(0, np.dot(normal, L))
            reflect_dir = 2 * np.dot(normal, L) * normal - L
            spec = max(0, np.dot(reflect_dir, view_dir)) ** material.shininess
            light_color = light.color * light.intensity / (dist*dist)
            result += light_color * (material.kd * diff * np.array(material.color) + material.ks * spec)
        return tuple(float(c) for c in np.clip(result, 0, 1))

    def glCastRay(self, origin, direction, max_distance=float('inf')):
        closest_t = float('inf')
        closest_hit = None
        for obj in self.scene:
            h = obj.ray_intersect(origin, direction)
            if h and 0 < h['t'] < closest_t and h['t'] < max_distance:
                closest_t = h['t']
                closest_hit = h
        return closest_hit

    def _build_default_scene(self):
        # Materiales distintos
        red = Material((1,0.2,0.2), ka=0.15, kd=0.6, ks=0.4, shininess=32)
        green = Material((0.2,1,0.2), ka=0.1, kd=0.7, ks=0.2, shininess=16)
        blue = Material((0.2,0.2,1), ka=0.2, kd=0.5, ks=0.3, shininess=64)
        yellow = Material((1,1,0.2), ka=0.1, kd=0.8, ks=0.3, shininess=8)

        self.scene = [
            Sphere(( -1.2, 0.0, 0), 0.8, red),
            Sphere((  1.2, 0.0, 0), 0.8, green),
            Sphere((  0.0, -1.0, -1.0), 0.5, blue),
            Sphere((  0.0,  1.0, -1.5), 0.5, yellow),
        ]
        self.lights = [
            Light((2,2,3), (1,1,1), 25),
            Light((-3,1,2), (1,0.95,0.9), 15)
        ]

    def _build_bear_scene(self):
        # Materiales base para el oso
        brown = Material((0.55, 0.32, 0.18), ka=0.2, kd=0.6, ks=0.2, shininess=32)
        dark_brown = Material((0.35, 0.2, 0.1), ka=0.2, kd=0.6, ks=0.3, shininess=32)
        beige = Material((0.9, 0.8, 0.7), ka=0.25, kd=0.6, ks=0.2, shininess=16)
        black = Material((0.05, 0.05, 0.05), ka=0.15, kd=0.5, ks=0.4, shininess=64)
        white = Material((0.95, 0.95, 0.95), ka=0.3, kd=0.6, ks=0.2, shininess=8)

        spheres = []
        add = spheres.append

        # Cuerpo principal
        add(Sphere((0, -0.2, 0), 1.0, brown))
        # Barriga clara (ligeramente al frente)
        add(Sphere((0, -0.3, 0.55), 0.55, beige))
        # Cabeza
        add(Sphere((0, 0.95, 0.1), 0.55, brown))
        # Hocico
        add(Sphere((0, 0.80, 0.5), 0.25, beige))
        # Nariz
        add(Sphere((0, 0.85, 0.62), 0.08, black))
        # Orejas
        add(Sphere((-0.35, 1.38, 0.0), 0.20, brown))
        add(Sphere(( 0.35, 1.38, 0.0), 0.20, brown))
        # Orejas internas
        add(Sphere((-0.35, 1.40, 0.15), 0.11, beige))
        add(Sphere(( 0.35, 1.40, 0.15), 0.11, beige))
        # Brazos
        add(Sphere((-0.95, 0.15, 0), 0.35, brown))
        add(Sphere(( 0.95, 0.15, 0), 0.35, brown))
        # Piernas
        add(Sphere((-0.5, -1.05, 0.15), 0.45, dark_brown))
        add(Sphere(( 0.5, -1.05, 0.15), 0.45, dark_brown))
        # Plantas (pies) claros
        add(Sphere((-0.5, -1.10, 0.45), 0.25, beige))
        add(Sphere(( 0.5, -1.10, 0.45), 0.25, beige))
        # Ojos (blanco + pupila)
        add(Sphere((-0.15, 1.05, 0.45), 0.09, white))
        add(Sphere(( 0.15, 1.05, 0.45), 0.09, white))
        add(Sphere((-0.15, 1.05, 0.52), 0.04, black))
        add(Sphere(( 0.15, 1.05, 0.52), 0.04, black))

        self.scene = spheres
        # Luces ajustadas para iluminar frontal y arriba
        self.lights = [
            Light((2.5, 3.0, 4.0), (1,1,1), 40),
            Light((-3.0, 2.0, 3.0), (1,0.95,0.9), 25)
        ]

    # -------------------- Render progresivo helpers --------------------
    def _init_progressive_render(self, pixels_per_frame=4000):
        self.random_pixels = [(x, y) for x in range(self.vpX, self.vpX + self.vpWidth) for y in range(self.vpY, self.vpY + self.vpHeight)]
        random.shuffle(self.random_pixels)
        self.zbuffer = [[float('inf') for _ in range(self.height)] for _ in range(self.width)]
        self.render_done = False
        self.pixels_per_frame = pixels_per_frame

    def restart_render(self):
        self.glClear()
        self._init_progressive_render(self.pixels_per_frame)

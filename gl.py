import numpy as np
from math import tan, pi, sqrt
import struct
from camera import Camera
import random
import pygame
from figure import Sphere, Material, Light, Mesh, Plane, Disk, Triangle, Cube, Cylinder
from pathlib import Path

class Renderer:
    def __init__(self, screen):
        # Pantalla y dimensiones
        self.screen = screen
        _, _, self.width, self.height = screen.get_rect()

        # Cámara
        self.camera = Camera()

        # Viewport y proyección
        self.glViewport(0, 0, self.width, self.height)
        self.glProjection()

        # Colores
        self.glColor(1, 1, 1)
        self.glClearColor(0, 0, 0)

        # Framebuffer (lista 2D)
        self.frameBuffer = [[(0, 0, 0) for _ in range(self.height)] for _ in range(self.width)]

        # Escena / luces / ambiente
        self.scene = []
        self.lights = []
        self.ambientLight = (0.15, 0.15, 1.5)

        # Cámara inicial
        self.camera.position = [0, 1, 5]

        # Parámetros ray tracing
        self.max_depth = 3
        self.environment = None
        self.env_intensity = 1.0
        self.light_intensity_scale = 5

        # Construcción de escena (cilindros de demostración)
        self._build_cylinder_scene()

        # Intento automático de cargar un environment map si existe un archivo común
        for candidate in ["environment.jpg", "environment.png", "env.jpg", "env.png"]:
            try:
                if Path(candidate).exists():
                    if self.load_environment(candidate):
                        break
            except Exception:
                pass

        # Inicializar render progresivo
        self.glClear()
        self._init_progressive_render()

    # Construcción de escena desde modelos en config
    def build_scene_from_models(self, models: list[dict]):
        self.scene = []
        for m in models:
            try:
                path = m.get('path')
                if path is None:
                    continue
                mat_cfg = m.get('material', {})
                mat = Material(
                    color=tuple(mat_cfg.get('color', (0.8,0.8,0.8))),
                    ka=float(mat_cfg.get('ka', 0.1)),
                    kd=float(mat_cfg.get('kd', 0.7)),
                    ks=float(mat_cfg.get('ks', 0.2)),
                    shininess=float(mat_cfg.get('shininess', 32)),
                    reflectivity=float(mat_cfg.get('reflectivity', 0.0)),
                    transparency=float(mat_cfg.get('transparency', 0.0)),
                    ior=float(mat_cfg.get('ior', 1.5)),
                    mtype='opaque' if (mat_cfg.get('transparency', 0.0) <= 0 and mat_cfg.get('reflectivity', 0.0) <= 0) else (
                        'transparent' if mat_cfg.get('transparency', 0.0) > 0 else 'reflective')
                )
                pos = tuple(m.get('position', (0,0,0)))
                rot = tuple(m.get('rotation', (0,0,0)))
                scl = tuple(m.get('scale', (1,1,1)))
                mesh = Mesh.from_obj(path, material=mat, position=pos, rotation=rot, scale=scl)
                self.scene.append(mesh)
            except Exception:
                continue
        # Luces por defecto si no se configuran externamente
        if not self.lights:
            self.lights = [
                Light((3,5,5), (1,1,1), 45),
                Light((-4,3,4), (1,0.95,0.9), 25)
            ]
        self.restart_render()

    def _build_room_scene(self):
        # Materiales base
        white = Material((0.85,0.85,0.85), ka=0.2, kd=0.7, ks=0.2, shininess=32)
        bone = Material((0.94,0.92,0.86), ka=0.2, kd=0.7, ks=0.2, shininess=32)  # blanco hueso
        red = Material((0.9,0.3,0.3), ka=0.15, kd=0.7, ks=0.2, shininess=32)
        green = Material((0.3,0.9,0.3), ka=0.15, kd=0.7, ks=0.2, shininess=32)
        blue = Material((0.3,0.3,0.9), ka=0.15, kd=0.7, ks=0.2, shininess=32)
        metal = Material((0.8,0.8,0.85), ka=0.05, kd=0.2, ks=0.9, shininess=128, reflectivity=0.3, mtype='reflective')
        mirror = Material((1.0,1.0,1.0), ka=0.0, kd=0.0, ks=1.0, shininess=256, reflectivity=1.0, mtype='reflective')
        polished_floor = Material((0.88,0.88,0.88), ka=0.15, kd=0.58, ks=0.42, shininess=160, reflectivity=0.20, mtype='reflective')

        # Habitación con 5 planos (suelo, techo, fondo, izquierda, derecha)
        self.scene = [
            Plane((0,-2,0), (0,1,0), polished_floor),     # Suelo (pulido)
            Plane((0, 2,0), (0,-1,0), white),    # Techo
            Plane((0,0,-4), (0,0,1), white),     # Pared de fondo
            Plane((-3,0,0), (1,0,0), red),       # Pared izquierda
            Plane(( 3,0,0), (-1,0,0), green),    # Pared derecha
            Plane((0,0, 6), (0,0,-1), bone),     # Pared detrás de la cámara (blanco hueso)
        ]

        # Dos cubos dentro del cuarto
        self.scene += [
            Cube((-1.2,-1.3,-1.5), 1.0, metal),
            Cube(( 1.0,-1.2,-2.2), 1.2, blue),
        ]

        # Un triángulo equilátero más grande, centrado a la izquierda de la pared de fondo (espejo)
        s = 1.5
        h = s * sqrt(3) / 2.0
        # Centro del triángulo: a la izquierda, centrado verticalmente; cerca del plano de la pared
        cx, cy, cz = (-1.2, 0.0, -3.92)
        v1 = (cx, cy + (2.0*h/3.0), cz)
        v2 = (cx - s/2.0, cy - (h/3.0), cz)
        v3 = (cx + s/2.0, cy - (h/3.0), cz)
        self.scene += [
            Triangle(v1, v2, v3, mirror)
        ]

        # Un disco centrado a la derecha, simétrico al triángulo con respecto al centro de la pared (espejo)
        self.scene += [
            Disk((1.2, 0.0, -3.92), (0.0, 0.0, 1.0), 0.6, mirror)
        ]

        # Espejos rectangulares verticales en paredes laterales (~65% de alto), 10% más anchos,
        # movidos hacia las esquinas y rotados levemente para que queden en diagonal.
        # Altura pared: 4 (y=-2..2) -> 65% ≈ 2.6
        h = 2.6
        y0 = -h/2
        y1 = h/2
        # Ancho base 0.8 -> +10% = 0.88 -> +10% adicional = 0.968
        w = 0.968
        # Centrar cerca de la esquina trasera (z ~ -3.2)
        zc = -3.2
        z0 = zc - w/2
        z1 = zc + w/2
        # ángulo de rotación alrededor de Y
        theta = np.deg2rad(38.0)

        # Helper para rotación Y alrededor de un pivote C (mantiene y)
        def rotY(p, C, ang):
            px, py, pz = p
            cx, cy, cz = C
            dx = px - cx
            dz = pz - cz
            cosA = np.cos(ang)
            sinA = np.sin(ang)
            rx = cx + dx * cosA + dz * sinA
            rz = cz + (-dx * sinA + dz * cosA)
            return (float(rx), float(py), float(rz))

        # Pared izquierda (x = -3). Offset del centro para permitir rotación sin penetrar pared.
        # Offset mínimo recomendado: (w/2)*sin(theta) + margen
        offset_l = (w/2) * float(np.sin(theta)) + 0.02
        xl_center = -3 + offset_l
        Cl = (xl_center, 0.0, zc)
        # Cuatro esquinas antes de rotar
        lp0 = (xl_center, y0, z0)
        lp1 = (xl_center, y1, z0)
        lp2 = (xl_center, y1, z1)
        lp3 = (xl_center, y0, z1)
        # Rotar hacia +z (mirando hacia el centro de la habitación)
        angL = -theta
        p0 = rotY(lp0, Cl, angL)
        p1 = rotY(lp1, Cl, angL)
        p2 = rotY(lp2, Cl, angL)
        p3 = rotY(lp3, Cl, angL)
        self.scene += [
            Triangle(p0, p1, p2, mirror),
            Triangle(p0, p2, p3, mirror)
        ]

        # Pared derecha (x = 3). Offset del centro simétrico y rotación hacia +z.
        offset_r = (w/2) * float(np.sin(theta)) + 0.02
        xr_center = 3 - offset_r
        Cr = (xr_center, 0.0, zc)
        rq0 = (xr_center, y0, z0)
        rq1 = (xr_center, y1, z0)
        rq2 = (xr_center, y1, z1)
        rq3 = (xr_center, y0, z1)
        angR = +theta
        q0 = rotY(rq0, Cr, angR)
        q1 = rotY(rq1, Cr, angR)
        q2 = rotY(rq2, Cr, angR)
        q3 = rotY(rq3, Cr, angR)
        self.scene += [
            Triangle(q0, q1, q2, mirror),
            Triangle(q0, q2, q3, mirror)
        ]

        # Luces
        self.lights = [
            Light((0,1.8,-1.0), (1,1,1), 60),
            Light((-2,1.0,-0.5), (1,0.95,0.9), 25)
        ]
        self.restart_render()

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
                    color = self._shade(hit, origin, direction, 0)
                    self.glPoint(x, y, color)
                    self.zbuffer[x][y] = t
            else:
                if self.environment is not None:
                    self.glPoint(x, y, self._environment_lookup(direction))
            processed += 1

        if not self.random_pixels:
            self.render_done = True
            return True
        return False

    def _shade(self, hit, origin, direction, depth):
        material = hit['material']
        point = hit['point']
        normal = hit['normal']
        view_dir = -direction

        # Componente base (ambiental)
        base_color = np.array(material.color)
        ambient = np.array(self.ambientLight) * material.ka * base_color
        local = ambient

        # Iluminación directa (Phong)
        for light in self.lights:
            L = light.position - point
            dist = np.linalg.norm(L) or 1
            L /= dist
            # Sombra (ocluido si hay intersección antes de la luz)
            shadow_hit = self.glCastRay(point + normal * 1e-4, L, max_distance=dist - 1e-3)
            if shadow_hit:
                continue
            diff = max(0.0, np.dot(normal, L))
            reflect_dir = 2 * np.dot(normal, L) * normal - L
            spec = max(0.0, np.dot(reflect_dir, view_dir)) ** material.shininess
            light_color = (light.color * light.intensity * self.light_intensity_scale) / (dist * dist)
            local += light_color * (material.kd * diff * base_color + material.ks * spec)

        local = np.clip(local, 0, 1)

        # Reflexión / Refracción con Fresnel (Schlick) y conservación de energía
        kr = float(material.reflectivity)
        kt = float(material.transparency)
        reflect_col = np.zeros(3)
        refract_col = np.zeros(3)
        Rw = 0.0
        Tw = 0.0
        if depth < self.max_depth and (kr > 0 or kt > 0):
            rdir = direction - 2 * np.dot(direction, normal) * normal
            if getattr(material, 'mtype', 'opaque') == 'reflective' and kt <= 0.0:
                # Espejo ideal: usa reflectividad directa sin Fresnel
                Rw = max(0.0, min(1.0, kr))
                base_weight = max(0.0, 1.0 - Rw)
                if Rw > 0.0:
                    reflect_col = self._trace_ray(point + normal * 1e-4, rdir, depth + 1)
            else:
                # Dielectrico: usa Fresnel de Schlick
                n = normal
                n1 = 1.0
                n2 = float(material.ior) if material.ior else 1.0
                cosi = -max(-1.0, min(1.0, np.dot(direction, n)))
                if cosi < 0:  # Dentro del objeto
                    cosi = -cosi
                    n1, n2 = n2, n1
                    n = -n
                eta = n1 / n2
                k = 1.0 - eta * eta * (1.0 - cosi * cosi)
                F0 = ((n2 - n1) / (n2 + n1)) ** 2 if (n2 + n1) != 0 else 0.0
                F = F0 + (1.0 - F0) * ((1.0 - cosi) ** 5)
                if k < 0.0:
                    F = 1.0
                Rw = kr * F
                Tw = kt * (1.0 - F) if k >= 0.0 else 0.0
                base_weight = max(0.0, 1.0 - (Rw + Tw))
                if Rw > 0.0:
                    reflect_col = self._trace_ray(point + normal * 1e-4, rdir, depth + 1)
                if Tw > 0.0:
                    tdir = eta * direction + (eta * cosi - sqrt(k)) * n
                    refract_col = self._trace_ray(point - n * 1e-4, tdir, depth + 1)
                    refract_col = refract_col * base_color
        else:
            base_weight = 1.0

        out_color = base_weight * local + Rw * reflect_col + Tw * refract_col
        return tuple(float(c) for c in np.clip(out_color, 0, 1))

    def glCastRay(self, origin, direction, max_distance=float('inf')):
        closest_t = float('inf')
        closest_hit = None
        for obj in self.scene:
            h = obj.ray_intersect(origin, direction)
            if h and 0 < h['t'] < closest_t and h['t'] < max_distance:
                closest_t = h['t']
                closest_hit = h
        return closest_hit

    def _trace_ray(self, origin, direction, depth=0):
        hit = self.glCastRay(origin, direction)
        if hit:
            return np.array(self._shade(hit, origin, direction, depth))
        if self.environment is not None:
            return np.array(self._environment_lookup(direction))
        return np.array((0,0,0))

    def load_environment(self, filepath):
        path = Path(filepath)
        if not path.exists():
            return False
        if path.suffix.lower() == '.hdr':
            try:
                data = self._load_hdr_environment(path)
            except Exception:
                return False
            self.environment = data
            self.env_h, self.env_w = data.shape[0], data.shape[1]
            return True
        # LDR via pygame (PNG/JPG)
        try:
            surf = pygame.image.load(str(path)).convert()
        except Exception:
            return False
        w, h = surf.get_size()
        data = np.zeros((h, w, 3), dtype=float)
        for y in range(h):
            for x in range(w):
                r, g, b, *_ = surf.get_at((x, y))
                # Convert from approximate sRGB to linear for better filtering
                sr = r / 255.0
                sg = g / 255.0
                sb = b / 255.0
                data[y, x] = (sr ** 2.2, sg ** 2.2, sb ** 2.2)
        self.environment = data
        self.env_w = w
        self.env_h = h
        return True

    # Simple Radiance .hdr (RGBE) loader with RLE support
    def _load_hdr_environment(self, path: Path):
        with open(path, 'rb') as f:
            header = []
            while True:
                line = f.readline()
                if not line:
                    break
                line_str = line.decode('latin-1').strip()
                if line_str == '':
                    # Fin del bloque de encabezado; la siguiente línea contiene la resolución
                    break
                header.append(line_str)
            # La línea de resolución viene inmediatamente después del header
            res_line = f.readline().decode('latin-1').strip()
            tokens = res_line.split()
            if len(tokens) != 4 or tokens[0] not in ('-Y','+Y') or tokens[2] not in ('-X','+X'):
                # Intento de búsqueda resiliente por si hay líneas extra vacías
                while tokens == []:
                    res_line = f.readline().decode('latin-1').strip()
                    tokens = res_line.split()
                if len(tokens) != 4 or tokens[0] not in ('-Y','+Y') or tokens[2] not in ('-X','+X'):
                    raise ValueError('HDR: resolución no encontrada')
            height = int(tokens[1])
            width = int(tokens[3])
            data = np.zeros((height, width, 3), dtype=np.float32)
            # Read scanlines
            for y in range(height):
                # Peek first 4 bytes to check RLE marker
                pos = f.tell()
                scan_header = f.read(4)
                if len(scan_header) < 4:
                    raise ValueError('Unexpected EOF in HDR file')
                if scan_header[0] == 2 and scan_header[1] == 2 and (scan_header[2] << 8 | scan_header[3]) == width:
                    # New RLE format
                    channels = []
                    for c in range(4):
                        channel = []
                        x = 0
                        while x < width:
                            val = f.read(1)
                            if not val:
                                raise ValueError('EOF in RLE channel')
                            count = val[0]
                            if count > 128:
                                run = count - 128
                                value = f.read(1)[0]
                                channel.extend([value] * run)
                                x += run
                            else:
                                run = count
                                raw = f.read(run)
                                channel.extend(raw)
                                x += run
                        channels.append(channel)
                    R, G, B, E = channels
                    for x in range(width):
                        e = E[x]
                        if e:
                            fexp = 2.0 ** (e - 128)
                            data[y, x, 0] = (R[x] / 256.0) * fexp
                            data[y, x, 1] = (G[x] / 256.0) * fexp
                            data[y, x, 2] = (B[x] / 256.0) * fexp
                else:
                    # Old non-RLE fallback: revert and read width*4 bytes
                    f.seek(pos)
                    raw = f.read(width * 4)
                    if len(raw) < width * 4:
                        raise ValueError('EOF in flat scanline')
                    for x in range(width):
                        R = raw[4*x]
                        G = raw[4*x + 1]
                        B = raw[4*x + 2]
                        E = raw[4*x + 3]
                        if E:
                            fexp = 2.0 ** (E - 128)
                            data[y, x, 0] = (R / 256.0) * fexp
                            data[y, x, 1] = (G / 256.0) * fexp
                            data[y, x, 2] = (B / 256.0) * fexp
            # Optional tone-map to avoid extreme values (simple clamp)
            # data = np.clip(data, 0, 50.0)
            return data

    def _environment_lookup(self, direction):
        # Normalize direction
        d = direction / (np.linalg.norm(direction) or 1)
        # Equirect mapping to [0,1]
        u = 0.5 + (np.arctan2(d[2], d[0]) / (2*pi))
        v = 0.5 - (np.arcsin(np.clip(d[1], -1, 1)) / pi)
        # Nearest neighbor sampling with horizontal wrap
        x = int(round(u * (self.env_w - 1))) % self.env_w
        y = int(round(v * (self.env_h - 1)))
        y = max(0, min(self.env_h - 1, y))
        col = self.environment[y, x]
        # Ajuste de intensidad del environment antes del tone-mapping
        col = col * float(self.env_intensity)
        # Tone mapping (Reinhard simple)
        tm = col / (1.0 + col)
        # Gamma to display
        gamma = 1/2.2
        tm = np.clip(tm, 0, 1) ** gamma
        return tuple(float(c) for c in tm)

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

    def _build_cylinder_scene(self):
        # Materiales
        white = Material((0.85,0.85,0.85), ka=0.2, kd=0.7, ks=0.2, shininess=32)
        bone = Material((0.94,0.92,0.86), ka=0.2, kd=0.7, ks=0.2, shininess=32)
        red = Material((0.9,0.3,0.3), ka=0.15, kd=0.7, ks=0.2, shininess=32)
        green = Material((0.3,0.9,0.3), ka=0.15, kd=0.7, ks=0.2, shininess=32)
        mirror = Material((1.0,1.0,1.0), ka=0.0, kd=0.0, ks=1.0, shininess=256, reflectivity=1.0, mtype='reflective')
        polished_floor = Material((0.88,0.88,0.88), ka=0.15, kd=0.58, ks=0.42, shininess=160, reflectivity=0.20, mtype='reflective')
        # Cilindros
        opaque = Material((0.9,0.4,0.2), ka=0.2, kd=0.7, ks=0.25, shininess=48, mtype='opaque')
        glass  = Material((0.7,0.95,1.0), ka=0.05, kd=0.05, ks=0.9, shininess=128, transparency=0.8, ior=1.5, mtype='transparent')

        # Habitación con paredes y piso (y techo y pared trasera de cámara)
        self.scene = [
            Plane((0,-2,0), (0,1,0), polished_floor),   # Piso
            Plane((0, 2,0), (0,-1,0), white),           # Techo
            Plane((0,0,-4), (0,0,1), white),            # Pared de fondo
            Plane((-3,0,0), (1,0,0), red),              # Pared izquierda
            Plane(( 3,0,0), (-1,0,0), green),           # Pared derecha
            Plane((0,0, 6), (0,0,-1), bone),            # Pared detrás de la cámara
        ]

        # Espejos rectangulares en paredes laterales (dos triángulos por panel)
        h = 2.6
        y0 = -h/2
        y1 = h/2
        w = 0.968
        zc = -3.2
        z0 = zc - w/2
        z1 = zc + w/2
        theta = np.deg2rad(38.0)

        def rotY(p, C, ang):
            px, py, pz = p
            cx, cy, cz = C
            dx = px - cx
            dz = pz - cz
            cosA = np.cos(ang)
            sinA = np.sin(ang)
            rx = cx + dx * cosA + dz * sinA
            rz = cz + (-dx * sinA + dz * cosA)
            return (float(rx), float(py), float(rz))

        # Panel espejo en pared izquierda
        offset_l = (w/2) * float(np.sin(theta)) + 0.02
        xl_center = -3 + offset_l
        Cl = (xl_center, 0.0, zc)
        lp0 = (xl_center, y0, z0)
        lp1 = (xl_center, y1, z0)
        lp2 = (xl_center, y1, z1)
        lp3 = (xl_center, y0, z1)
        angL = -theta
        p0 = rotY(lp0, Cl, angL)
        p1 = rotY(lp1, Cl, angL)
        p2 = rotY(lp2, Cl, angL)
        p3 = rotY(lp3, Cl, angL)
        self.scene += [
            Triangle(p0, p1, p2, mirror),
            Triangle(p0, p2, p3, mirror)
        ]

        # Panel espejo en pared derecha
        offset_r = (w/2) * float(np.sin(theta)) + 0.02
        xr_center = 3 - offset_r
        Cr = (xr_center, 0.0, zc)
        rq0 = (xr_center, y0, z0)
        rq1 = (xr_center, y1, z0)
        rq2 = (xr_center, y1, z1)
        rq3 = (xr_center, y0, z1)
        angR = +theta
        q0 = rotY(rq0, Cr, angR)
        q1 = rotY(rq1, Cr, angR)
        q2 = rotY(rq2, Cr, angR)
        q3 = rotY(rq3, Cr, angR)
        self.scene += [
            Triangle(q0, q1, q2, mirror),
            Triangle(q0, q2, q3, mirror)
        ]

        # Tres cilindros dentro del cuarto
        self.scene += [
            Cylinder((-1.4, -1.0, -1.2), 0.35, 1.2, opaque),
            Cylinder(( 0.0, -1.2, -1.8), 0.40, 1.4, mirror),
            Cylinder(( 1.4, -0.9, -1.0), 0.30, 1.0, glass),
        ]

        # Luces
        self.lights = [
            Light((0,1.8,-1.0), (1,1,1), 60),
            Light((-2,1.0,-0.5), (1,0.95,0.9), 25)
        ]
        # No llamar restart_render aquí; __init__ o el preset lo harán

    def _build_materials_scene(self):
        opaque_red = Material((0.9,0.2,0.2), ka=0.2, kd=0.7, ks=0.3, shininess=32, mtype='opaque')
        opaque_green = Material((0.2,0.9,0.2), ka=0.2, kd=0.7, ks=0.3, shininess=16, mtype='opaque')
        refl_chrome = Material((0.8,0.8,0.85), ka=0.05, kd=0.1, ks=0.9, shininess=128, reflectivity=0.8, mtype='reflective')
        refl_gold = Material((0.9,0.75,0.3), ka=0.05, kd=0.25, ks=0.8, shininess=96, reflectivity=0.6, mtype='reflective')
        # Transparent materials with distinct tint colors
        transp_glass = Material((0.15,0.85,0.75), ka=0.05, kd=0.05, ks=0.9, shininess=128, transparency=0.8, ior=1.5, mtype='transparent')  # teal
        transp_blue = Material((0.85,0.25,0.7), ka=0.05, kd=0.05, ks=0.8, shininess=96, transparency=0.7, ior=1.33, mtype='transparent')   # magenta
        # Ajustadas posiciones y radios para dejar espacios y permitir ver el HDR entre esferas
        self.scene = [
            Sphere((-2.4,  0.9, -1.2), 0.45, opaque_red),      # Opaque 1
            Sphere(( 2.4,  0.9, -1.2), 0.45, opaque_green),    # Opaque 2
            Sphere((-1.4, -0.5,  0.2), 0.55, refl_chrome),     # Reflective 1
            Sphere(( 1.4, -0.5,  0.2), 0.55, refl_gold),       # Reflective 2
            Sphere((-0.45, 0.15, -0.9), 0.42, transp_glass),   # Transparent 1
            Sphere(( 0.55, -0.05, -0.4), 0.42, transp_blue),   # Transparent 2
        ]
        self.lights = [
            Light((3,5,5), (1,1,1), 45),
            Light((-4,3,4), (1,0.95,0.9), 25)
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

import numpy as np

class Material:
    """Material con soporte para opaco, reflectivo y transparente.
    color: tuple rgb (0-1)
    ka, kd, ks: componentes Phong
    shininess: exponente especular
    reflectivity: 0..1 proporción de color de reflexión
    transparency: 0..1 proporción de color refractado
    ior: índice de refracción (solo si transparency > 0)
    mtype: 'opaque' | 'reflective' | 'transparent'
    Nota: Se normaliza para que (local + reflect + refract) no exceda 1.
    """
    __slots__ = ("color","ka","kd","ks","shininess","reflectivity","transparency","ior","mtype","tint_strength")
    def __init__(self, color=(1,1,1), ka=0.1, kd=0.7, ks=0.2, shininess=32,
                 reflectivity=0.0, transparency=0.0, ior=1.5, mtype="opaque", tint_strength=1.0):
        self.color = color
        self.ka = ka
        self.kd = kd
        self.ks = ks
        self.shininess = shininess
        self.reflectivity = reflectivity
        self.transparency = transparency
        self.ior = ior
        self.mtype = mtype
        # 0.0 = sin tinte en transmisión, 1.0 = tinte completo por color
        self.tint_strength = float(tint_strength)

class Light:
    __slots__ = ("position","color","intensity")
    def __init__(self, position=(0,0,0), color=(1,1,1), intensity=1.0):
        self.position = np.array(position, dtype=float)
        self.color = np.array(color, dtype=float)
        self.intensity = intensity

class Shape(object):
    def __init__(self, position, material=None):
        self.position = np.array(position, dtype=float)
        self.type = "None"
        self.material = material or Material()

    def ray_intersect(self, origin, direction):
        return None
    
class Sphere(Shape):
    def __init__(self, position, radius, material=None):
        super().__init__(position, material)
        self.radius = radius
        self.type = "Sphere"

    def ray_intersect(self, origin, direction):
        """Calcula intersección rayo-esfera.
        origin, direction: np.array(3)
        Retorna dict con: t, point, normal, material; o None
        """
        L = self.position - origin
        tca = np.dot(L, direction)
        d2 = np.dot(L, L) - tca * tca
        r2 = self.radius * self.radius
        if d2 > r2:
            return None
        thc = np.sqrt(r2 - d2)
        t0 = tca - thc
        t1 = tca + thc
        if t1 < 0:  # ambos detrás
            return None
        t = t0 if t0 > 0 else t1
        point = origin + direction * t
        normal = (point - self.position) / self.radius
        return {
            "t": t,
            "point": point,
            "normal": normal / (np.linalg.norm(normal) or 1),
            "material": self.material
        }

class Mesh(Shape):
    """Malla de triángulos con material uniforme. Carga básica de OBJ y ray-triangle."""
    def __init__(self, vertices: np.ndarray, faces: list[tuple[int,int,int]], material: Material, position=(0,0,0)):
        super().__init__(position, material)
        self.type = "Mesh"
        self.vertices = np.asarray(vertices, dtype=float)
        self.faces = faces

    @staticmethod
    def from_obj(path, material=None, position=(0,0,0), rotation=(0,0,0), scale=(1,1,1)):
        from pathlib import Path
        from MathLib import TranslationMatrix, RotationMatrix, ScaleMatrix
        path = Path(path)
        verts = []
        faces = []
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if not line or line.startswith('#'):
                    continue
                parts = line.strip().split()
                if not parts:
                    continue
                if parts[0] == 'v' and len(parts) >= 4:
                    verts.append((float(parts[1]), float(parts[2]), float(parts[3])))
                elif parts[0] == 'f' and len(parts) >= 4:
                    idxs = []
                    for p in parts[1:]:
                        tok = p.split('/')
                        v_idx = int(tok[0])
                        if v_idx < 0:
                            v_idx = len(verts) + 1 + v_idx
                        idxs.append(v_idx - 1)
                    for i in range(1, len(idxs) - 1):
                        faces.append((idxs[0], idxs[i], idxs[i+1]))
        V = np.array(verts, dtype=float)
        ones = np.ones((V.shape[0], 1), dtype=float)
        Vh = np.hstack([V, ones])
        M = TranslationMatrix(*position) * RotationMatrix(*rotation) * ScaleMatrix(*scale)
        Vt = (M @ Vh.T).T[:, :3]
        return Mesh(Vt, faces, material or Material())

    def ray_intersect(self, origin, direction):
        closest_t = float('inf')
        hit_info = None
        V = self.vertices
        for a, b, c in self.faces:
            v0, v1, v2 = V[a], V[b], V[c]
            hit = self._intersect_triangle(origin, direction, v0, v1, v2)
            if hit and 0 < hit['t'] < closest_t:
                closest_t = hit['t']
                hit_info = hit
                hit_info['material'] = self.material
        return hit_info

    @staticmethod
    def _intersect_triangle(origin, direction, v0, v1, v2):
        eps = 1e-8
        edge1 = v1 - v0
        edge2 = v2 - v0
        h = np.cross(direction, edge2)
        a = np.dot(edge1, h)
        if -eps < a < eps:
            return None
        f = 1.0 / a
        s = origin - v0
        u = f * np.dot(s, h)
        if u < 0.0 or u > 1.0:
            return None
        q = np.cross(s, edge1)
        v = f * np.dot(direction, q)
        if v < 0.0 or u + v > 1.0:
            return None
        t = f * np.dot(edge2, q)
        if t <= eps:
            return None
        point = origin + direction * t
        n = np.cross(edge1, edge2)
        nn = np.linalg.norm(n) or 1.0
        normal = n / nn
        return {"t": t, "point": point, "normal": normal}


class Plane(Shape):
    """Plano infinito definido por un punto y una normal."""
    def __init__(self, point, normal, material=None):
        super().__init__(point, material)
        n = np.array(normal, dtype=float)
        self.normal = n / (np.linalg.norm(n) or 1.0)
        self.type = "Plane"

    def ray_intersect(self, origin, direction):
        denom = float(np.dot(self.normal, direction))
        if abs(denom) < 1e-6:
            return None
        t = float(np.dot(self.position - origin, self.normal) / denom)
        if t <= 1e-6:
            return None
        point = origin + direction * t
        n = self.normal if denom < 0 else -self.normal  # lado visible
        return {"t": t, "point": point, "normal": n, "material": self.material}


class Disk(Shape):
    """Disco finito en un plano, por centro, normal y radio."""
    def __init__(self, center, normal, radius, material=None):
        super().__init__(center, material)
        n = np.array(normal, dtype=float)
        self.normal = n / (np.linalg.norm(n) or 1.0)
        self.radius = float(radius)
        self.type = "Disk"

    def ray_intersect(self, origin, direction):
        denom = float(np.dot(self.normal, direction))
        if abs(denom) < 1e-6:
            return None
        t = float(np.dot(self.position - origin, self.normal) / denom)
        if t <= 1e-6:
            return None
        point = origin + direction * t
        if np.linalg.norm(point - self.position) > self.radius:
            return None
        n = self.normal if denom < 0 else -self.normal
        return {"t": t, "point": point, "normal": n, "material": self.material}


class Ring(Shape):
    """Anillo plano (contorno circular grueso) definido por centro, normal, radio externo y radio interno.
    Si el punto intersecta el plano dentro del radio externo pero fuera del interno => hit.
    """
    def __init__(self, center, normal, outer_radius, inner_radius, material=None):
        super().__init__(center, material)
        n = np.array(normal, dtype=float)
        self.normal = n / (np.linalg.norm(n) or 1.0)
        self.outer_radius = float(outer_radius)
        self.inner_radius = float(inner_radius)
        if self.inner_radius < 0:
            self.inner_radius = 0.0
        if self.inner_radius >= self.outer_radius:
            self.inner_radius = max(0.0, self.outer_radius * 0.5)
        self.type = "Ring"

    def ray_intersect(self, origin, direction):
        denom = float(np.dot(self.normal, direction))
        if abs(denom) < 1e-6:
            return None
        t = float(np.dot(self.position - origin, self.normal) / denom)
        if t <= 1e-6:
            return None
        point = origin + direction * t
        v = point - self.position
        # Distancia al centro proyectada sobre el plano (normal ya eliminó componente perpendicular)
        dist = np.linalg.norm(v - np.dot(v, self.normal) * self.normal)
        if dist > self.outer_radius or dist < self.inner_radius:
            return None
        n = self.normal if denom < 0 else -self.normal
        return {"t": t, "point": point, "normal": n, "material": self.material}


class ArcRing(Shape):
    """Arco circular plano (segmento de un anillo) definido por:
    - center, normal: plano del arco
    - outer_radius / inner_radius: límites radial externo e interno (para grosor de línea)
    - start_angle, end_angle (radianes) medidos en el plano respecto al eje +X local (cuando normal=(0,1,0))
      El ángulo se calcula con atan2(z-cz, x-cx) y se normaliza a [0, 2π).
      Si end_angle < start_angle se asume envoltura (wrap) atravesando 2π.
    Nota: Pensado para dibujar líneas de cancha (semicírculos de triple, etc.)
    """
    def __init__(self, center, normal, outer_radius, inner_radius, start_angle, end_angle, material=None):
        super().__init__(center, material)
        n = np.array(normal, dtype=float)
        self.normal = n / (np.linalg.norm(n) or 1.0)
        self.outer_radius = float(outer_radius)
        self.inner_radius = float(inner_radius)
        if self.inner_radius < 0:
            self.inner_radius = 0.0
        if self.inner_radius >= self.outer_radius:
            self.inner_radius = max(0.0, self.outer_radius * 0.5)
        self.start_angle = float(start_angle)
        self.end_angle = float(end_angle)
        self.type = "ArcRing"

    @staticmethod
    def _normalize_angle(a):
        twopi = 2.0 * np.pi
        a = a % twopi
        if a < 0:
            a += twopi
        return a

    def ray_intersect(self, origin, direction):
        denom = float(np.dot(self.normal, direction))
        if abs(denom) < 1e-6:
            return None
        t = float(np.dot(self.position - origin, self.normal) / denom)
        if t <= 1e-6:
            return None
        point = origin + direction * t
        v = point - self.position
        # Eliminar componente perpendicular para medir radio en el plano
        v_proj = v - np.dot(v, self.normal) * self.normal
        dist = np.linalg.norm(v_proj)
        if dist > self.outer_radius or dist < self.inner_radius:
            return None
        # Definir ejes locales para el ángulo: si el plano es horizontal, forzar u=+X, w=+Z para que 0 rad apunte en +X.
        if abs(self.normal[1]) > 0.9 and abs(self.normal[0]) < 0.2 and abs(self.normal[2]) < 0.2:
            u = np.array([1.0, 0.0, 0.0])  # eje de referencia (ángulo 0)
            w = np.array([0.0, 0.0, 1.0])  # 90°
            x_local = v_proj[0]
            z_local = v_proj[2]
        else:
            # General: construir base ortonormal en el plano
            aux = np.array([1.0, 0.0, 0.0])
            if abs(np.dot(aux, self.normal)) > 0.9:
                aux = np.array([0.0, 0.0, 1.0])
            u = np.cross(self.normal, aux)
            u /= (np.linalg.norm(u) or 1.0)
            w = np.cross(self.normal, u)
            x_local = np.dot(v_proj, u)
            z_local = np.dot(v_proj, w)
        angle = np.arctan2(z_local, x_local)
        angle = self._normalize_angle(angle)
        start = self._normalize_angle(self.start_angle)
        end = self._normalize_angle(self.end_angle)
        if start <= end:
            inside = (start - 1e-6) <= angle <= (end + 1e-6)
        else:  # wrap-around
            inside = angle >= (start - 1e-6) or angle <= (end + 1e-6)
        if not inside:
            return None
        n = self.normal if denom < 0 else -self.normal
        return {"t": t, "point": point, "normal": n, "material": self.material}


class Triangle(Shape):
    """Triángulo definido por tres vértices en espacio mundial."""
    def __init__(self, a, b, c, material=None):
        super().__init__((0,0,0), material)
        self.a = np.array(a, dtype=float)
        self.b = np.array(b, dtype=float)
        self.c = np.array(c, dtype=float)
        self.type = "Triangle"

    def ray_intersect(self, origin, direction):
        eps = 1e-8
        edge1 = self.b - self.a
        edge2 = self.c - self.a
        h = np.cross(direction, edge2)
        a = np.dot(edge1, h)
        if -eps < a < eps:
            return None
        f = 1.0 / a
        s = origin - self.a
        u = f * np.dot(s, h)
        if u < 0.0 or u > 1.0:
            return None
        q = np.cross(s, edge1)
        v = f * np.dot(direction, q)
        if v < 0.0 or u + v > 1.0:
            return None
        t = f * np.dot(edge2, q)
        if t <= eps:
            return None
        point = origin + direction * t
        n = np.cross(edge1, edge2)
        nn = np.linalg.norm(n) or 1.0
        normal = n / nn
        if np.dot(normal, direction) > 0:
            normal = -normal
        return {"t": t, "point": point, "normal": normal, "material": self.material}


class Cube(Shape):
    """Cubo axis-aligned (AABB) por centro y tamaño (lado)."""
    def __init__(self, center, size, material=None):
        super().__init__(center, material)
        self.type = "Cube"
        h = float(size) / 2.0
        c = self.position
        self.min = np.array([c[0]-h, c[1]-h, c[2]-h], dtype=float)
        self.max = np.array([c[0]+h, c[1]+h, c[2]+h], dtype=float)

    def ray_intersect(self, origin, direction):
        tmin = -np.inf
        tmax = np.inf
        hit_axis = -1
        for i in range(3):
            if abs(direction[i]) < 1e-8:
                if origin[i] < self.min[i] or origin[i] > self.max[i]:
                    return None
            else:
                invD = 1.0 / direction[i]
                t0 = (self.min[i] - origin[i]) * invD
                t1 = (self.max[i] - origin[i]) * invD
                sign = 1
                if t0 > t1:
                    t0, t1 = t1, t0
                    sign = -1
                if t0 > tmin:
                    tmin = t0
                    hit_axis = i * sign
                tmax = min(tmax, t1)
                if tmax <= tmin:
                    return None
        if tmin <= 1e-6:
            return None
        point = origin + direction * tmin
        # Normal según el axis que limitó tmin
        normal = np.array([0.0, 0.0, 0.0])
        axis = abs(hit_axis) // 1
        axis = int(abs(hit_axis)) // 1
        if abs(hit_axis) == 0:
            normal = np.array([np.sign(hit_axis) or 1.0, 0.0, 0.0])
        elif abs(hit_axis) == 1:
            normal = np.array([0.0, np.sign(hit_axis) or 1.0, 0.0])
        else:
            normal = np.array([0.0, 0.0, np.sign(hit_axis) or 1.0])
        if np.dot(normal, direction) > 0:
            normal = -normal
        return {"t": float(tmin), "point": point, "normal": normal, "material": self.material}


class Box(Shape):
    """Paralelepípedo axis-aligned (AABB) con dimensiones independientes.
    center: (cx, cy, cz)
    size: (sx, sy, sz) longitudes en cada eje (si se pasa un escalar se asume cubo)
    """
    def __init__(self, center, size, material=None):
        super().__init__(center, material)
        self.type = "Box"
        if isinstance(size, (int, float)):
            sx = sy = sz = float(size)
        else:
            sx, sy, sz = [float(s) for s in size]
        self.half = np.array([sx/2.0, sy/2.0, sz/2.0], dtype=float)
        c = self.position
        self.min = c - self.half
        self.max = c + self.half

    def ray_intersect(self, origin, direction):
        tmin = -np.inf
        tmax = np.inf
        hit_axis = -1  # 0->x,1->y,2->z con signo
        for i in range(3):
            if abs(direction[i]) < 1e-8:
                # Rayo paralelo a planos de este eje: fuera del rango => no hay intersección
                if origin[i] < self.min[i] or origin[i] > self.max[i]:
                    return None
                continue
            invD = 1.0 / direction[i]
            t0 = (self.min[i] - origin[i]) * invD
            t1 = (self.max[i] - origin[i]) * invD
            sign = 1
            if t0 > t1:
                t0, t1 = t1, t0
                sign = -1
            if t0 > tmin:
                tmin = t0
                hit_axis = i * sign
            tmax = min(tmax, t1)
            if tmax <= tmin:
                return None
        if tmin <= 1e-6:
            return None
        point = origin + direction * tmin
        # Determinar normal según el eje que definió tmin
        normal = np.array([0.0, 0.0, 0.0])
        axis = int(abs(hit_axis))  # 0,1,2
        s = np.sign(hit_axis) or 1.0
        if axis == 0:
            normal = np.array([s, 0.0, 0.0])
        elif axis == 1:
            normal = np.array([0.0, s, 0.0])
        else:
            normal = np.array([0.0, 0.0, s])
        if np.dot(normal, direction) > 0:
            normal = -normal
        # Calcular coordenadas UV basadas en la cara golpeada (mapeo planar por cara)
        # Coordenadas locales centradas
        local = point - self.position
        # Normalizar a [0,1] en los dos ejes de la cara
        if axis == 1:  # caras superior/inferior (Y): usar X-Z
            u = (local[0] / (self.half[0] + 1e-12) + 1.0) * 0.5
            v = (local[2] / (self.half[2] + 1e-12) + 1.0) * 0.5
        elif axis == 0:  # caras en X: usar Z-Y
            u = (local[2] / (self.half[2] + 1e-12) + 1.0) * 0.5
            v = (local[1] / (self.half[1] + 1e-12) + 1.0) * 0.5
        else:  # axis == 2, caras en Z: usar X-Y
            u = (local[0] / (self.half[0] + 1e-12) + 1.0) * 0.5
            v = (local[1] / (self.half[1] + 1e-12) + 1.0) * 0.5

        # Transformaciones UV opcionales por objeto
        # 1) Rotación alrededor del centro (0.5, 0.5)
        rot_deg = getattr(self, 'uv_rotation_deg', None)
        if rot_deg not in (None, 0, 0.0):
            try:
                ang = np.deg2rad(float(rot_deg))
                cu, su = np.cos(ang), np.sin(ang)
                # trasladar al centro, rotar, regresar
                uu = u - 0.5
                vv = v - 0.5
                ur = uu * cu - vv * su
                vr = uu * su + vv * cu
                u = ur + 0.5
                v = vr + 0.5
            except Exception:
                pass

        # 2) Offset
        uv_off = getattr(self, 'uv_offset', None)
        if uv_off and len(uv_off) >= 2:
            try:
                u += float(uv_off[0])
                v += float(uv_off[1])
            except Exception:
                pass

        # 3) Tiling por objeto (para texturas procedurales normalmente)
        tiles = getattr(self, 'uv_tiles', None)
        if tiles and len(tiles) >= 2:
            try:
                u *= float(tiles[0])
                v *= float(tiles[1])
            except Exception:
                pass

        return {"t": float(tmin), "point": point, "normal": normal, "material": self.material, "u": float(u), "v": float(v)}


class Cylinder(Shape):
    """Cilindro finito alineado al eje Y, con tapas.
    center: (x,y,z), radius: r, height: h
    """
    def __init__(self, center, radius, height, material=None):
        super().__init__(center, material)
        self.type = "Cylinder"
        self.radius = float(radius)
        self.half_height = float(height) / 2.0

    def ray_intersect(self, origin, direction):
        eps = 1e-6
        # Transformar a coords locales del cilindro (centro en 0,0,0; eje Y)
        o = origin - self.position
        d = direction

        t_min = np.inf
        hit = None

        # Intersección con la superficie lateral: x^2 + z^2 = r^2
        a = d[0]*d[0] + d[2]*d[2]
        if a > eps:
            b = 2.0 * (o[0]*d[0] + o[2]*d[2])
            c = o[0]*o[0] + o[2]*o[2] - self.radius*self.radius
            disc = b*b - 4.0*a*c
            if disc >= 0.0:
                sqrt_disc = np.sqrt(disc)
                t0 = (-b - sqrt_disc) / (2.0*a)
                t1 = (-b + sqrt_disc) / (2.0*a)
                for t in (t0, t1):
                    if t > eps:
                        y = o[1] + t*d[1]
                        if -self.half_height <= y <= self.half_height:
                            if t < t_min:
                                p = origin + direction * t
                                # Normal lateral en local (x,0,z)
                                n_local = np.array([p[0]-self.position[0], 0.0, p[2]-self.position[2]], dtype=float)
                                n = n_local / (np.linalg.norm(n_local) or 1.0)
                                if np.dot(n, direction) > 0:
                                    n = -n
                                hit = {"t": float(t), "point": p, "normal": n, "material": self.material}
                                t_min = t

        # Intersección con tapas (planos y = ±half_height) si el rayo no es paralelo al eje Y
        if abs(d[1]) > eps:
            for ycap, n_sign in ((self.half_height, 1.0), (-self.half_height, -1.0)):
                t = (ycap - o[1]) / d[1]
                if t > eps and t < t_min:
                    x = o[0] + t*d[0]
                    z = o[2] + t*d[2]
                    if x*x + z*z <= self.radius*self.radius + 1e-8:
                        p = origin + direction * t
                        n = np.array([0.0, n_sign, 0.0], dtype=float)
                        if np.dot(n, direction) > 0:
                            n = -n
                        hit = {"t": float(t), "point": p, "normal": n, "material": self.material}
                        t_min = t

        return hit


class AxisCylinder(Shape):
    """Cilindro finito alineado a uno de los ejes principales (x, y, z) con tapas.
    axis: 'x' | 'y' | 'z'
    center: centro del cilindro
    radius: radio
    height: longitud a lo largo del eje
    """
    def __init__(self, center, radius, height, axis='y', material=None):
        super().__init__(center, material)
        self.type = "AxisCylinder"
        self.radius = float(radius)
        self.half_height = float(height) / 2.0
        if axis not in ('x','y','z'):
            axis = 'y'
        self.axis = axis

    def _to_local(self, v):
        # Reordenar componentes para que el eje elegido pase a ser Y.
        if self.axis == 'y':
            return v
        if self.axis == 'x':  # X -> Y
            return np.array([v[1], v[0], v[2]], dtype=float)
        # axis == 'z': Z -> Y
        return np.array([v[0], v[2], v[1]], dtype=float)

    def _to_world_normal(self, n):
        if self.axis == 'y':
            return n
        if self.axis == 'x':
            return np.array([n[1], n[0], n[2]], dtype=float)
        # z
            
        return np.array([n[0], n[2], n[1]], dtype=float)

    def ray_intersect(self, origin, direction):
        eps = 1e-6
        # Transformar a coords locales donde el eje del cilindro es Y
        o_world = origin - self.position
        d_world = direction
        o = self._to_local(o_world)
        d = self._to_local(d_world)

        t_min = np.inf
        hit = None

        # Lateral: x^2 + z^2 = r^2
        a = d[0]*d[0] + d[2]*d[2]
        if a > eps:
            b = 2.0 * (o[0]*d[0] + o[2]*d[2])
            c = o[0]*o[0] + o[2]*o[2] - self.radius*self.radius
            disc = b*b - 4.0*a*c
            if disc >= 0.0:
                sqrt_disc = np.sqrt(disc)
                for t in ((-b - sqrt_disc)/(2.0*a), (-b + sqrt_disc)/(2.0*a)):
                    if t > eps:
                        y = o[1] + t*d[1]
                        if -self.half_height <= y <= self.half_height and t < t_min:
                            p_world = origin + direction * t
                            # Normal lateral en local (x,0,z)
                            # Recuperar punto local para normal
                            pl = o + d * t
                            n_local = np.array([pl[0], 0.0, pl[2]], dtype=float)
                            n_local /= (np.linalg.norm(n_local) or 1.0)
                            n_world = self._to_world_normal(n_local)
                            if np.dot(n_world, direction) > 0:
                                n_world = -n_world
                            hit = {"t": float(t), "point": p_world, "normal": n_world, "material": self.material}
                            t_min = t

        # Tapas (planos y = ±half_height) en espacio local
        if abs(d[1]) > eps:
            for ycap, n_sign in ((self.half_height, 1.0), (-self.half_height, -1.0)):
                t = (ycap - o[1]) / d[1]
                if t > eps and t < t_min:
                    x = o[0] + t*d[0]
                    z = o[2] + t*d[2]
                    if x*x + z*z <= self.radius*self.radius + 1e-8:
                        p_world = origin + direction * t
                        n_local = np.array([0.0, n_sign, 0.0], dtype=float)
                        n_world = self._to_world_normal(n_local)
                        if np.dot(n_world, direction) > 0:
                            n_world = -n_world
                        hit = {"t": float(t), "point": p_world, "normal": n_world, "material": self.material}
                        t_min = t

        return hit


class Cone(Shape):
    """Cono finito alineado al eje Y, con base.
    center: (x,y,z), base radius: r en y = -h/2, apex en y = +h/2.
    height: h
    """
    def __init__(self, center, radius, height, material=None):
        super().__init__(center, material)
        self.type = "Cone"
        self.radius = float(radius)
        self.half_height = float(height) / 2.0

    def ray_intersect(self, origin, direction):
        eps = 1e-6
        # Coordenadas locales (centro en 0, eje Y)
        o = origin - self.position
        d = direction

        hh = self.half_height
        h = 2.0 * hh
        k = self.radius / h  # radio por unidad de altura

        t_min = np.inf
        hit = None

        # Intersección con la superficie lateral: x^2 + z^2 = (k*(hh - y))^2
        A = d[0]*d[0] + d[2]*d[2] - (k*k) * (d[1]*d[1])
        B = 2.0 * (o[0]*d[0] + o[2]*d[2] + (k*k) * (hh - o[1]) * d[1])
        C = o[0]*o[0] + o[2]*o[2] - (k*k) * (hh - o[1])*(hh - o[1])

        if abs(A) > eps:
            disc = B*B - 4.0*A*C
            if disc >= 0.0:
                sqrt_disc = np.sqrt(disc)
                for t in ((-B - sqrt_disc)/(2.0*A), (-B + sqrt_disc)/(2.0*A)):
                    if t > eps and t < t_min:
                        y = o[1] + t*d[1]
                        # Entre la base y el ápice
                        if -hh <= y <= hh:
                            # Evitar el ápice exacto si numéricamente cae ahí
                            if abs(y - hh) < 1e-5:
                                continue
                            p = origin + direction * t
                            # Normal de la superficie lateral via gradiente de F
                            pl = p - self.position
                            nx = pl[0]
                            ny = (k*k) * (hh - pl[1])
                            nz = pl[2]
                            n = np.array([nx, ny, nz], dtype=float)
                            n /= (np.linalg.norm(n) or 1.0)
                            if np.dot(n, direction) > 0:
                                n = -n
                            hit = {"t": float(t), "point": p, "normal": n, "material": self.material}
                            t_min = t

        # Intersección con la base (plano y = -hh)
        if abs(d[1]) > eps:
            t = (-hh - o[1]) / d[1]
            if t > eps and t < t_min:
                x = o[0] + t*d[0]
                z = o[2] + t*d[2]
                if x*x + z*z <= self.radius*self.radius + 1e-8:
                    p = origin + direction * t
                    n = np.array([0.0, -1.0, 0.0], dtype=float)
                    if np.dot(n, direction) > 0:
                        n = -n
                    hit = {"t": float(t), "point": p, "normal": n, "material": self.material}
                    t_min = t

        return hit


class Torus(Shape):
    """Toroide (torus) con orientación opcional.
    Alineado por defecto al eje Y; se puede rotar con Euler (grados) para apuntar el agujero.
    Implícita local: (x^2 + y^2 + z^2 + R^2 - r^2)^2 - 4 R^2 (x^2 + z^2) = 0
    """
    def __init__(self, center, major_radius, minor_radius, material=None, rotation_euler=(0.0, 0.0, 0.0)):
        super().__init__(center, material)
        self.type = "Torus"
        self.R = float(major_radius)
        self.r = float(minor_radius)
        # Matriz de rotación local->mundo a partir de Euler (Rx, Ry, Rz)
        rx, ry, rz = rotation_euler
        rx = float(rx); ry = float(ry); rz = float(rz)
        def rotX(a):
            rad = np.deg2rad(a)
            c, s = np.cos(rad), np.sin(rad)
            return np.array([[1,0,0],[0,c,-s],[0,s,c]], dtype=float)
        def rotY(a):
            rad = np.deg2rad(a)
            c, s = np.cos(rad), np.sin(rad)
            return np.array([[c,0,s],[0,1,0],[-s,0,c]], dtype=float)
        def rotZ(a):
            rad = np.deg2rad(a)
            c, s = np.cos(rad), np.sin(rad)
            return np.array([[c,-s,0],[s,c,0],[0,0,1]], dtype=float)
        # Orden: R = Rz * Ry * Rx
        self.Rmat = rotZ(rz) @ rotY(ry) @ rotX(rx)
        self.Rinv = self.Rmat.T  # ortonormal

    def ray_intersect(self, origin, direction):
        eps = 1e-6
        # Transformar a coordenadas locales del torus
        o_world = origin - self.position
        d_world = direction
        o = self.Rinv @ o_world
        d = self.Rinv @ d_world
        ox, oy, oz = float(o[0]), float(o[1]), float(o[2])
        dx, dy, dz = float(d[0]), float(d[1]), float(d[2])

        R2 = self.R * self.R
        r2 = self.r * self.r

        # Polinomios x^2, y^2, z^2: c0 + c1 t + c2 t^2
        c0x, c1x, c2x = ox*ox, 2.0*ox*dx, dx*dx
        c0y, c1y, c2y = oy*oy, 2.0*oy*dy, dy*dy
        c0z, c1z, c2z = oz*oz, 2.0*oz*dz, dz*dz

        # Suma x^2 + y^2 + z^2
        s0 = c0x + c0y + c0z
        s1 = c1x + c1y + c1z
        s2 = c2x + c2y + c2z

        # Q(t) = (x^2 + y^2 + z^2) + (R^2 - r^2)
        q0 = s0 + (R2 - r2)
        q1 = s1
        q2 = s2

        # Q(t)^2 -> coeficientes hasta grado 4
        S0 = q0*q0
        S1 = 2.0*q0*q1
        S2 = 2.0*q0*q2 + q1*q1
        S3 = 2.0*q1*q2
        S4 = q2*q2

        # 4 R^2 (x^2 + z^2)
        xz0 = c0x + c0z
        xz1 = c1x + c1z
        xz2 = c2x + c2z
        k = 4.0 * R2

        # F(t) = Q^2 - 4 R^2 (x^2 + z^2) -> coeficientes A0..A4
        A0 = S0 - k * xz0
        A1 = S1 - k * xz1
        A2 = S2 - k * xz2
        A3 = S3
        A4 = S4

        # Resolver raíces reales positivas del cuártico
        coeffs = [A4, A3, A2, A1, A0]
        try:
            roots = np.roots(coeffs)
        except Exception:
            return None
        t_candidates = [float(r.real) for r in roots if abs(r.imag) < 1e-6 and float(r.real) > eps]
        if not t_candidates:
            return None
        t = min(t_candidates)

        # Punto mundo y normal (gradiente local rotada a mundo)
        p_world = origin + direction * t
        pl = (self.Rinv @ (p_world - self.position))  # punto local
        x, y, z = float(pl[0]), float(pl[1]), float(pl[2])
        Qval = (x*x + y*y + z*z) + (R2 - r2)
        nx = 4.0 * Qval * x - 8.0 * R2 * x
        ny = 4.0 * Qval * y
        nz = 4.0 * Qval * z - 8.0 * R2 * z
        n_local = np.array([nx, ny, nz], dtype=float)
        n_world = self.Rmat @ n_local
        n_world /= (np.linalg.norm(n_world) or 1.0)
        if np.dot(n_world, direction) > 0:
            n_world = -n_world
        return {"t": float(t), "point": p_world, "normal": n_world, "material": self.material}
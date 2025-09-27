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
    __slots__ = ("color","ka","kd","ks","shininess","reflectivity","transparency","ior","mtype")
    def __init__(self, color=(1,1,1), ka=0.1, kd=0.7, ks=0.2, shininess=32,
                 reflectivity=0.0, transparency=0.0, ior=1.5, mtype="opaque"):
        self.color = color
        self.ka = ka
        self.kd = kd
        self.ks = ks
        self.shininess = shininess
        self.reflectivity = reflectivity
        self.transparency = transparency
        self.ior = ior
        self.mtype = mtype

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
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
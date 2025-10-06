"""
Figuras geométricas adicionales para el raytracer.
Incluye formas más complejas no vistas en clase básica.
"""
import numpy as np
from math import sqrt, cos, sin, pi, atan2

class Shape:
    """Clase base para todas las formas geométricas"""
    def __init__(self, position, material=None):
        self.position = np.array(position, dtype=float)
        self.type = "Shape"
        self.material = material
    
    def ray_intersect(self, origin, direction):
        """Debe ser implementado por cada forma específica"""
        return None
    
    def get_uv_coordinates(self, point):
        """Obtiene coordenadas UV para el punto de intersección"""
        return 0.5, 0.5

class Ellipsoid(Shape):
    """Elipsoide con radios diferentes en cada eje"""
    def __init__(self, position, radii, material=None):
        super().__init__(position, material)
        self.radii = np.array(radii, dtype=float)  # [rx, ry, rz]
        self.type = "Ellipsoid"
    
    def ray_intersect(self, origin, direction):
        # Transformar el rayo al espacio del elipsoide unitario
        oc = origin - self.position
        
        # Escalar por los radios inversos
        scaled_oc = oc / self.radii
        scaled_dir = direction / self.radii
        
        # Resolver ecuación cuadrática en el espacio transformado
        a = np.dot(scaled_dir, scaled_dir)
        b = 2.0 * np.dot(scaled_oc, scaled_dir)
        c = np.dot(scaled_oc, scaled_oc) - 1.0
        
        discriminant = b * b - 4 * a * c
        if discriminant < 0:
            return None
        
        sqrt_discriminant = sqrt(discriminant)
        t1 = (-b - sqrt_discriminant) / (2 * a)
        t2 = (-b + sqrt_discriminant) / (2 * a)
        
        t = t1 if t1 > 0 else t2
        if t <= 0:
            return None
        
        point = origin + direction * t
        
        # Normal en el espacio transformado, luego escalado de vuelta
        local_point = point - self.position
        normal = 2 * local_point / (self.radii * self.radii)
        normal = normal / (np.linalg.norm(normal) + 1e-8)
        
        u, v = self.get_uv_coordinates(point)
        
        return {
            "t": t,
            "point": point,
            "normal": normal,
            "material": self.material,
            "u": u,
            "v": v
        }
    
    def get_uv_coordinates(self, point):
        # Convertir a coordenadas esféricas
        local_point = (point - self.position) / self.radii
        
        # Normalizar para obtener coordenadas esféricas
        r = np.linalg.norm(local_point)
        if r < 1e-8:
            return 0.5, 0.5
        
        local_point = local_point / r
        
        u = (atan2(local_point[0], local_point[2]) + pi) / (2 * pi)
        v = (np.arcsin(np.clip(local_point[1], -1, 1)) + pi/2) / pi
        
        return u, v

class Capsule(Shape):
    """Cápsula (cilindro con hemisferios en los extremos)"""
    def __init__(self, position, height, radius, material=None):
        super().__init__(position, material)
        self.height = height
        self.radius = radius
        self.type = "Capsule"
    
    def ray_intersect(self, origin, direction):
        # La cápsula está alineada con el eje Y
        oc = origin - self.position
        
        # Verificar intersección con cilindro central
        cylinder_result = self._intersect_cylinder(oc, direction)
        
        # Verificar intersección con hemisferios
        top_sphere_result = self._intersect_hemisphere(oc, direction, self.height/2, 1)
        bottom_sphere_result = self._intersect_hemisphere(oc, direction, -self.height/2, -1)
        
        # Encontrar la intersección más cercana válida
        candidates = [r for r in [cylinder_result, top_sphere_result, bottom_sphere_result] if r is not None]
        
        if not candidates:
            return None
        
        closest = min(candidates, key=lambda x: x["t"])
        return closest
    
    def _intersect_cylinder(self, oc, direction):
        # Cilindro infinito en Y, luego cortamos por altura
        a = direction[0]**2 + direction[2]**2
        b = 2 * (oc[0] * direction[0] + oc[2] * direction[2])
        c = oc[0]**2 + oc[2]**2 - self.radius**2
        
        if a < 1e-8:  # Rayo paralelo al eje Y
            if c > 0:  # No intersecta
                return None
            # Verificar intersección en Y
            t1 = (-self.height/2 - oc[1]) / (direction[1] + 1e-8)
            t2 = (self.height/2 - oc[1]) / (direction[1] + 1e-8)
            t = min(t1, t2) if min(t1, t2) > 0 else max(t1, t2)
            if t <= 0:
                return None
        else:
            discriminant = b**2 - 4*a*c
            if discriminant < 0:
                return None
            
            sqrt_d = sqrt(discriminant)
            t1 = (-b - sqrt_d) / (2*a)
            t2 = (-b + sqrt_d) / (2*a)
            t = t1 if t1 > 0 else t2
            if t <= 0:
                return None
        
        point = oc + direction * t + self.position
        
        # Verificar si está dentro de la altura del cilindro
        local_y = point[1] - self.position[1]
        if abs(local_y) > self.height/2:
            return None
        
        # Normal del cilindro
        normal = np.array([point[0] - self.position[0], 0, point[2] - self.position[2]])
        normal = normal / (np.linalg.norm(normal) + 1e-8)
        
        u, v = self.get_uv_coordinates(point)
        
        return {
            "t": t,
            "point": point,
            "normal": normal,
            "material": self.material,
            "u": u,
            "v": v
        }
    
    def _intersect_hemisphere(self, oc, direction, y_offset, hemisphere_sign):
        # Esfera centrada en (0, y_offset, 0)
        sphere_center = np.array([0, y_offset, 0])
        oc_sphere = oc - sphere_center
        
        a = np.dot(direction, direction)
        b = 2 * np.dot(oc_sphere, direction)
        c = np.dot(oc_sphere, oc_sphere) - self.radius**2
        
        discriminant = b**2 - 4*a*c
        if discriminant < 0:
            return None
        
        sqrt_d = sqrt(discriminant)
        t1 = (-b - sqrt_d) / (2*a)
        t2 = (-b + sqrt_d) / (2*a)
        t = t1 if t1 > 0 else t2
        if t <= 0:
            return None
        
        point = oc + direction * t + self.position
        local_point = point - (self.position + sphere_center)
        
        # Verificar si está en el hemisferio correcto
        if local_point[1] * hemisphere_sign < 0:
            return None
        
        normal = local_point / (np.linalg.norm(local_point) + 1e-8)
        
        u, v = self.get_uv_coordinates(point)
        
        return {
            "t": t,
            "point": point,
            "normal": normal,
            "material": self.material,
            "u": u,
            "v": v
        }

class Octahedron(Shape):
    """Octaedro regular"""
    def __init__(self, position, size, material=None):
        super().__init__(position, material)
        self.size = size
        self.type = "Octahedron"
        
        # Definir las 8 caras del octaedro como planos
        self.faces = [
            # Pirámide superior (4 caras)
            ([1, 1, 1], size),    # +x+y+z
            ([-1, 1, 1], size),   # -x+y+z
            ([1, 1, -1], size),   # +x+y-z
            ([-1, 1, -1], size),  # -x+y-z
            # Pirámide inferior (4 caras)
            ([1, -1, 1], size),   # +x-y+z
            ([-1, -1, 1], size),  # -x-y+z
            ([1, -1, -1], size),  # +x-y-z
            ([-1, -1, -1], size), # -x-y-z
        ]
    
    def ray_intersect(self, origin, direction):
        # Transformar al espacio local
        local_origin = origin - self.position
        
        closest_t = float('inf')
        closest_normal = None
        
        # Probar intersección con cada cara
        for normal, d in self.faces:
            normal = np.array(normal, dtype=float)
            
            # Ecuación del plano: normal · (point - position) = d
            denom = np.dot(normal, direction)
            
            if abs(denom) < 1e-8:
                continue  # Rayo paralelo al plano
            
            t = (d - np.dot(normal, local_origin)) / denom
            
            if t <= 0 or t >= closest_t:
                continue
            
            # Punto de intersección
            point = local_origin + direction * t
            
            # Verificar si el punto está dentro del octaedro
            if self._point_inside_octahedron(point):
                closest_t = t
                closest_normal = normal
        
        if closest_t == float('inf'):
            return None
        
        point = origin + direction * closest_t
        u, v = self.get_uv_coordinates(point)
        
        return {
            "t": closest_t,
            "point": point,
            "normal": closest_normal,
            "material": self.material,
            "u": u,
            "v": v
        }
    
    def _point_inside_octahedron(self, point):
        # Un punto está dentro del octaedro si satisface todas las desigualdades de los planos
        for normal, d in self.faces:
            normal = np.array(normal, dtype=float)
            if np.dot(normal, point) > d + 1e-6:
                return False
        return True

class Hyperboloid(Shape):
    """Hiperboloide de una hoja"""
    def __init__(self, position, a=1.0, b=1.0, c=1.0, material=None):
        super().__init__(position, material)
        self.a = a  # Radio en X
        self.b = b  # Radio en Z  
        self.c = c  # Parámetro en Y
        self.type = "Hyperboloid"
    
    def ray_intersect(self, origin, direction):
        # Ecuación: (x²/a²) + (z²/b²) - (y²/c²) = 1
        # Transformar al espacio local
        oc = origin - self.position
        
        # Coeficientes de la ecuación cuadrática
        dx, dy, dz = direction
        ox, oy, oz = oc
        
        a_coeff = (dx/self.a)**2 + (dz/self.b)**2 - (dy/self.c)**2
        b_coeff = 2 * ((ox*dx)/(self.a**2) + (oz*dz)/(self.b**2) - (oy*dy)/(self.c**2))
        c_coeff = (ox/self.a)**2 + (oz/self.b)**2 - (oy/self.c)**2 - 1
        
        discriminant = b_coeff**2 - 4*a_coeff*c_coeff
        
        if discriminant < 0 or abs(a_coeff) < 1e-8:
            return None
        
        sqrt_d = sqrt(discriminant)
        t1 = (-b_coeff - sqrt_d) / (2*a_coeff)
        t2 = (-b_coeff + sqrt_d) / (2*a_coeff)
        
        t = t1 if t1 > 0 else t2
        if t <= 0:
            return None
        
        point = origin + direction * t
        local_point = point - self.position
        
        # Calcular normal: ∇f donde f(x,y,z) = x²/a² + z²/b² - y²/c² - 1
        normal = np.array([
            2 * local_point[0] / (self.a**2),
            -2 * local_point[1] / (self.c**2),
            2 * local_point[2] / (self.b**2)
        ])
        normal = normal / (np.linalg.norm(normal) + 1e-8)
        
        u, v = self.get_uv_coordinates(point)
        
        return {
            "t": t,
            "point": point,
            "normal": normal,
            "material": self.material,
            "u": u,
            "v": v
        }

class Paraboloid(Shape):
    """Paraboloide"""
    def __init__(self, position, a=1.0, b=1.0, height=2.0, material=None):
        super().__init__(position, material)
        self.a = a  # Escala en X
        self.b = b  # Escala en Z
        self.height = height
        self.type = "Paraboloid"
    
    def ray_intersect(self, origin, direction):
        # Ecuación: y = (x²/a²) + (z²/b²)
        # Limitado por altura
        oc = origin - self.position
        
        dx, dy, dz = direction
        ox, oy, oz = oc
        
        # Sustituir en la ecuación paramétrica del rayo
        # y = oy + dy*t = (ox + dx*t)²/a² + (oz + dz*t)²/b²
        
        # Expandir y reorganizar en forma cuadrática
        a_coeff = (dx/self.a)**2 + (dz/self.b)**2
        b_coeff = 2*((ox*dx)/(self.a**2) + (oz*dz)/(self.b**2)) - dy
        c_coeff = (ox/self.a)**2 + (oz/self.b)**2 - oy
        
        if abs(a_coeff) < 1e-8:
            # Caso lineal
            if abs(b_coeff) < 1e-8:
                return None
            t = -c_coeff / b_coeff
        else:
            # Caso cuadrático
            discriminant = b_coeff**2 - 4*a_coeff*c_coeff
            if discriminant < 0:
                return None
            
            sqrt_d = sqrt(discriminant)
            t1 = (-b_coeff - sqrt_d) / (2*a_coeff)
            t2 = (-b_coeff + sqrt_d) / (2*a_coeff)
            
            t = t1 if t1 > 0 else t2
        
        if t <= 0:
            return None
        
        point = origin + direction * t
        local_point = point - self.position
        
        # Verificar límites de altura
        if local_point[1] < 0 or local_point[1] > self.height:
            return None
        
        # Calcular normal: ∇f donde f(x,y,z) = x²/a² + z²/b² - y
        normal = np.array([
            2 * local_point[0] / (self.a**2),
            -1,
            2 * local_point[2] / (self.b**2)
        ])
        normal = normal / (np.linalg.norm(normal) + 1e-8)
        
        u, v = self.get_uv_coordinates(point)
        
        return {
            "t": t,
            "point": point,
            "normal": normal,
            "material": self.material,
            "u": u,
            "v": v
        }
    
    def get_uv_coordinates(self, point):
        local_point = point - self.position
        
        # Coordenadas polares en el plano XZ
        x, y, z = local_point
        r = sqrt(x**2 + z**2)
        
        if r > 1e-8:
            u = (atan2(z, x) + pi) / (2 * pi)
        else:
            u = 0.5
        
        v = y / self.height if self.height > 0 else 0.5
        
        return u, v

class Dodecahedron(Shape):
    """Dodecaedro regular (12 caras pentagonales)"""
    def __init__(self, position, size, material=None):
        super().__init__(position, material)
        self.size = size
        self.type = "Dodecahedron"
        
        # Generar las 12 caras del dodecahedron
        phi = (1 + sqrt(5)) / 2  # Razón áurea
        
        # Normales de las caras del dodecahedron
        self.face_normals = []
        
        # 6 caras principales (basadas en cubos)
        for i in [-1, 1]:
            for j in [-1, 1]:
                for k in [-1, 1]:
                    self.face_normals.append(np.array([i, j, k]))
        
        # 6 caras adicionales (basadas en la razón áurea)
        coords = []
        for i in [-1, 1]:
            coords.extend([
                [0, i/phi, i*phi], 
                [i/phi, i*phi, 0], 
                [i*phi, 0, i/phi]
            ])
        
        for coord in coords:
            self.face_normals.append(np.array(coord))
        
        # Normalizar todas las normales
        for i in range(len(self.face_normals)):
            norm = np.linalg.norm(self.face_normals[i])
            if norm > 0:
                self.face_normals[i] = self.face_normals[i] / norm
    
    def ray_intersect(self, origin, direction):
        # Transformar al espacio local
        local_origin = origin - self.position
        
        closest_t = float('inf')
        closest_normal = None
        
        # Distancia desde el centro a cualquier cara
        face_distance = self.size * (3 + sqrt(5)) / 4
        
        # Probar intersección con cada cara
        for normal in self.face_normals:
            # Ecuación del plano: normal · (point - center) = face_distance
            denom = np.dot(normal, direction)
            
            if abs(denom) < 1e-8:
                continue  # Rayo paralelo al plano
            
            t = (face_distance - np.dot(normal, local_origin)) / denom
            
            if t <= 0 or t >= closest_t:
                continue
            
            # Punto de intersección
            point = local_origin + direction * t
            
            # Verificar si el punto está dentro del dodecaedro
            # (debe estar del lado correcto de todas las caras)
            inside = True
            for other_normal in self.face_normals:
                if np.dot(other_normal, point) > face_distance + 1e-6:
                    inside = False
                    break
            
            if inside:
                closest_t = t
                closest_normal = normal
        
        if closest_t == float('inf'):
            return None
        
        point = origin + direction * closest_t
        u, v = self.get_uv_coordinates(point)
        
        return {
            "t": closest_t,
            "point": point,
            "normal": closest_normal,
            "material": self.material,
            "u": u,
            "v": v
        }
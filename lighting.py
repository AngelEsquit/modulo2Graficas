"""
Sistema de iluminación avanzado para el raytracer.
Incluye diferentes tipos de luces: point light, directional light, spot light.
"""
import numpy as np
from math import cos, sin, radians, pi

class Light:
    """Clase base para luces"""
    def __init__(self, color=(1, 1, 1), intensity=1.0):
        self.color = np.array(color, dtype=float)
        self.intensity = intensity
        self.type = "base"
    
    def get_light_direction(self, point):
        """Obtiene la dirección de la luz hacia un punto"""
        return np.array([0, 1, 0])  # Default hacia arriba
    
    def get_light_intensity(self, point):
        """Obtiene la intensidad de la luz en un punto"""
        return self.color * self.intensity
    
    def get_distance(self, point):
        """Obtiene la distancia desde la luz hasta el punto"""
        return float('inf')

class PointLight(Light):
    """Luz puntual - emite luz en todas las direcciones desde un punto"""
    def __init__(self, position=(0, 0, 0), color=(1, 1, 1), intensity=1.0, 
                 attenuation_constant=1.0, attenuation_linear=0.1, attenuation_quadratic=0.01):
        super().__init__(color, intensity)
        self.position = np.array(position, dtype=float)
        self.type = "point"
        
        # Parámetros de atenuación: I = I0 / (kc + kl*d + kq*d²)
        self.attenuation_constant = attenuation_constant
        self.attenuation_linear = attenuation_linear
        self.attenuation_quadratic = attenuation_quadratic
    
    def get_light_direction(self, point):
        """Dirección desde el punto hacia la luz"""
        direction = self.position - point
        return direction / (np.linalg.norm(direction) + 1e-8)
    
    def get_light_intensity(self, point):
        """Intensidad con atenuación por distancia"""
        distance = self.get_distance(point)
        attenuation = (self.attenuation_constant + 
                      self.attenuation_linear * distance + 
                      self.attenuation_quadratic * distance * distance)
        attenuation = max(attenuation, 0.001)  # Evitar división por cero
        return (self.color * self.intensity) / attenuation
    
    def get_distance(self, point):
        """Distancia desde la luz hasta el punto"""
        return np.linalg.norm(self.position - point)

class DirectionalLight(Light):
    """Luz direccional - luz paralela como el sol"""
    def __init__(self, direction=(0, -1, 0), color=(1, 1, 1), intensity=1.0):
        super().__init__(color, intensity)
        self.direction = np.array(direction, dtype=float)
        self.direction = self.direction / (np.linalg.norm(self.direction) + 1e-8)
        self.type = "directional"
    
    def get_light_direction(self, point):
        """Dirección constante de la luz (hacia la fuente)"""
        return -self.direction
    
    def get_light_intensity(self, point):
        """Intensidad constante (no hay atenuación)"""
        return self.color * self.intensity
    
    def get_distance(self, point):
        """Distancia infinita para luz direccional"""
        return float('inf')

class SpotLight(Light):
    """Luz spot - cono de luz con ángulo limitado"""
    def __init__(self, position=(0, 0, 0), direction=(0, -1, 0), 
                 color=(1, 1, 1), intensity=1.0,
                 inner_angle=30.0, outer_angle=45.0,
                 attenuation_constant=1.0, attenuation_linear=0.1, attenuation_quadratic=0.01):
        super().__init__(color, intensity)
        self.position = np.array(position, dtype=float)
        self.direction = np.array(direction, dtype=float)
        self.direction = self.direction / (np.linalg.norm(self.direction) + 1e-8)
        self.type = "spot"
        
        # Ángulos en radianes
        self.inner_angle = radians(inner_angle)
        self.outer_angle = radians(outer_angle)
        
        # Atenuación por distancia
        self.attenuation_constant = attenuation_constant
        self.attenuation_linear = attenuation_linear
        self.attenuation_quadratic = attenuation_quadratic
    
    def get_light_direction(self, point):
        """Dirección desde el punto hacia la luz"""
        direction = self.position - point
        return direction / (np.linalg.norm(direction) + 1e-8)
    
    def get_light_intensity(self, point):
        """Intensidad con atenuación por distancia y ángulo"""
        # Dirección desde la luz hacia el punto
        to_point = point - self.position
        distance = np.linalg.norm(to_point)
        
        if distance < 1e-8:
            return self.color * self.intensity
        
        to_point_normalized = to_point / distance
        
        # Ángulo entre la dirección de la luz y la dirección al punto
        cos_angle = np.dot(self.direction, to_point_normalized)
        angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
        
        # Factor de spot (falloff suave entre inner y outer angle)
        if angle <= self.inner_angle:
            spot_factor = 1.0
        elif angle <= self.outer_angle:
            # Interpolación suave entre inner y outer
            t = (angle - self.inner_angle) / (self.outer_angle - self.inner_angle)
            spot_factor = 1.0 - (t * t * (3.0 - 2.0 * t))  # Smoothstep
        else:
            spot_factor = 0.0
        
        # Atenuación por distancia
        distance_attenuation = (self.attenuation_constant + 
                               self.attenuation_linear * distance + 
                               self.attenuation_quadratic * distance * distance)
        distance_attenuation = max(distance_attenuation, 0.001)
        
        total_intensity = (self.color * self.intensity * spot_factor) / distance_attenuation
        return total_intensity
    
    def get_distance(self, point):
        """Distancia desde la luz hasta el punto"""
        return np.linalg.norm(self.position - point)

class AreaLight(Light):
    """Luz de área - simula una fuente de luz extendida"""
    def __init__(self, center=(0, 0, 0), normal=(0, -1, 0), 
                 width=2.0, height=2.0, color=(1, 1, 1), intensity=1.0,
                 samples=4):
        super().__init__(color, intensity)
        self.center = np.array(center, dtype=float)
        self.normal = np.array(normal, dtype=float)
        self.normal = self.normal / (np.linalg.norm(self.normal) + 1e-8)
        self.width = width
        self.height = height
        self.samples = samples
        self.type = "area"
        
        # Crear vectores tangente y bitangente
        if abs(self.normal[1]) < 0.9:
            self.tangent = np.cross(self.normal, np.array([0, 1, 0]))
        else:
            self.tangent = np.cross(self.normal, np.array([1, 0, 0]))
        self.tangent = self.tangent / (np.linalg.norm(self.tangent) + 1e-8)
        self.bitangent = np.cross(self.normal, self.tangent)
    
    def get_sample_positions(self):
        """Genera posiciones de muestreo en la superficie de la luz"""
        positions = []
        step = 1.0 / self.samples
        
        for i in range(self.samples):
            for j in range(self.samples):
                # Coordenadas normalizadas con jitter
                u = (i + 0.5) * step - 0.5  # -0.5 a 0.5
                v = (j + 0.5) * step - 0.5  # -0.5 a 0.5
                
                # Añadir jitter aleatorio para anti-aliasing
                import random
                u += (random.random() - 0.5) * step * 0.5
                v += (random.random() - 0.5) * step * 0.5
                
                # Convertir a posición mundial
                position = (self.center + 
                           u * self.width * self.tangent + 
                           v * self.height * self.bitangent)
                positions.append(position)
        
        return positions
    
    def get_light_direction(self, point):
        """Dirección promedio desde el punto hacia la luz"""
        # Para compatibilidad, usar el centro
        direction = self.center - point
        return direction / (np.linalg.norm(direction) + 1e-8)
    
    def get_light_intensity(self, point):
        """Intensidad promedio"""
        distance = self.get_distance(point)
        attenuation = max(distance * distance, 1.0)
        return (self.color * self.intensity) / attenuation
    
    def get_distance(self, point):
        """Distancia al centro de la luz"""
        return np.linalg.norm(self.center - point)

class LightManager:
    """Administrador de luces para la escena"""
    def __init__(self):
        self.lights = []
        self.ambient_light = np.array([0.1, 0.1, 0.1])
    
    def add_light(self, light):
        """Añade una luz a la escena"""
        self.lights.append(light)
    
    def set_ambient_light(self, color, intensity=1.0):
        """Establece la luz ambiental"""
        self.ambient_light = np.array(color) * intensity
    
    def get_all_lights(self):
        """Obtiene todas las luces"""
        return self.lights
    
    def clear_lights(self):
        """Elimina todas las luces"""
        self.lights.clear()
    
    def create_three_point_setup(self, target=(0, 0, 0), distance=5.0):
        """Crea un setup clásico de 3 luces"""
        self.clear_lights()
        
        # Key light (luz principal)
        key_pos = np.array(target) + np.array([distance * 0.7, distance * 0.7, distance])
        self.add_light(PointLight(
            position=key_pos,
            color=(1.0, 0.95, 0.8),
            intensity=2.0,
            attenuation_linear=0.05,
            attenuation_quadratic=0.005
        ))
        
        # Fill light (luz de relleno)
        fill_pos = np.array(target) + np.array([-distance * 0.5, distance * 0.3, distance * 0.8])
        self.add_light(PointLight(
            position=fill_pos,
            color=(0.8, 0.9, 1.0),
            intensity=1.0,
            attenuation_linear=0.05,
            attenuation_quadratic=0.005
        ))
        
        # Back light (luz trasera)
        back_pos = np.array(target) + np.array([0, distance * 0.5, -distance * 0.8])
        self.add_light(PointLight(
            position=back_pos,
            color=(1.0, 1.0, 0.9),
            intensity=0.8,
            attenuation_linear=0.08,
            attenuation_quadratic=0.01
        ))
    
    def create_studio_setup(self, target=(0, 0, 0)):
        """Crea un setup de estudio con múltiples luces"""
        self.clear_lights()
        
        # Luz principal suave (area light simulada con spot)
        self.add_light(SpotLight(
            position=np.array(target) + [2, 3, 3],
            direction=np.array(target) - np.array([2, 3, 3]),
            color=(1.0, 0.95, 0.85),
            intensity=2.5,
            inner_angle=20,
            outer_angle=35
        ))
        
        # Luces de relleno
        for i, offset in enumerate([[-3, 1, 2], [3, 1, 2], [0, 4, -2]]):
            pos = np.array(target) + np.array(offset)
            self.add_light(PointLight(
                position=pos,
                color=(0.9, 0.95, 1.0),
                intensity=0.8,
                attenuation_linear=0.1,
                attenuation_quadratic=0.02
            ))
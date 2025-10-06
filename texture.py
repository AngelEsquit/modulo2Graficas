"""
Sistema de texturas para el raytracer.
Soporte para imágenes PNG, JPG y BMP.
"""
import numpy as np
from PIL import Image
from pathlib import Path

class Texture:
    """Clase base para texturas"""
    def __init__(self):
        self.width = 0
        self.height = 0
        self.data = None
    
    def get_color(self, u, v):
        """Obtiene color en coordenadas UV (0-1)"""
        return (1.0, 1.0, 1.0)

class ImageTexture(Texture):
    """Textura cargada desde imagen"""
    def __init__(self, filepath):
        super().__init__()
        self.load_image(filepath)
    
    def load_image(self, filepath):
        """Carga imagen desde archivo"""
        try:
            path = Path(filepath)
            if not path.exists():
                print(f"Warning: Texture file {filepath} not found")
                return
            
            # Cargar imagen con PIL
            img = Image.open(path)
            img = img.convert('RGB')  # Asegurar formato RGB
            
            self.width = img.width
            self.height = img.height
            
            # Convertir a numpy array normalizado (0-1)
            self.data = np.array(img, dtype=np.float32) / 255.0
            
        except Exception as e:
            print(f"Error loading texture {filepath}: {e}")
            # Crear textura por defecto (damero)
            self.create_checkerboard()
    
    def create_checkerboard(self, size=64):
        """Crea textura de damero por defecto"""
        self.width = size
        self.height = size
        self.data = np.zeros((size, size, 3), dtype=np.float32)
        
        for i in range(size):
            for j in range(size):
                if (i // 8 + j // 8) % 2:
                    self.data[i, j] = [1.0, 1.0, 1.0]  # Blanco
                else:
                    self.data[i, j] = [0.0, 0.0, 0.0]  # Negro
    
    def get_color(self, u, v):
        """Obtiene color en coordenadas UV"""
        if self.data is None:
            return (1.0, 1.0, 1.0)
        
        # Envolver coordenadas UV
        u = u % 1.0
        v = v % 1.0
        
        # Convertir a coordenadas de pixel
        x = int(u * (self.width - 1))
        y = int(v * (self.height - 1))
        
        # Asegurar límites
        x = max(0, min(x, self.width - 1))
        y = max(0, min(y, self.height - 1))
        
        color = self.data[y, x]
        return tuple(color)

class ProceduralTexture(Texture):
    """Texturas procedurales"""
    def __init__(self, texture_type="checkerboard"):
        super().__init__()
        self.texture_type = texture_type
    
    def get_color(self, u, v):
        """Genera color procedural"""
        if self.texture_type == "checkerboard":
            return self._checkerboard(u, v)
        elif self.texture_type == "stripes":
            return self._stripes(u, v)
        elif self.texture_type == "dots":
            return self._dots(u, v)
        elif self.texture_type == "wood":
            return self._wood(u, v)
        elif self.texture_type == "court_lines":
            return self._court_lines(u, v)
        else:
            return (1.0, 1.0, 1.0)
    
    def _checkerboard(self, u, v, scale=8):
        """Patrón de damero"""
        check_u = int(u * scale) % 2
        check_v = int(v * scale) % 2
        if check_u ^ check_v:
            return (1.0, 1.0, 1.0)  # Blanco
        else:
            return (0.2, 0.2, 0.2)  # Gris oscuro
    
    def _stripes(self, u, v, scale=10):
        """Rayas verticales"""
        stripe = int(u * scale) % 2
        if stripe:
            return (0.8, 0.2, 0.2)  # Rojo
        else:
            return (0.2, 0.2, 0.8)  # Azul
    
    def _dots(self, u, v, scale=8):
        """Puntos"""
        dot_u = (u * scale) % 1.0
        dot_v = (v * scale) % 1.0
        
        # Distancia al centro del "cuadrado"
        center_u = 0.5
        center_v = 0.5
        dist = np.sqrt((dot_u - center_u)**2 + (dot_v - center_v)**2)
        
        if dist < 0.3:
            return (1.0, 1.0, 0.0)  # Amarillo
        else:
            return (0.1, 0.1, 0.5)  # Azul oscuro
    
    def _wood(self, u, v):
        """Patrón de madera"""
        # Anillos concéntricos con algo de ruido
        dist = np.sqrt((u - 0.5)**2 + (v - 0.5)**2)
        rings = np.sin(dist * 20 + u * 5 + v * 3) * 0.5 + 0.5
        
        # Colores de madera
        dark_wood = (0.4, 0.2, 0.1)
        light_wood = (0.8, 0.6, 0.3)
        
        # Interpolar entre colores
        r = dark_wood[0] + (light_wood[0] - dark_wood[0]) * rings
        g = dark_wood[1] + (light_wood[1] - dark_wood[1]) * rings
        b = dark_wood[2] + (light_wood[2] - dark_wood[2]) * rings
        
        return (r, g, b)
    
    def _court_lines(self, u, v):
        """Líneas de cancha de basketball"""
        # Color base de la madera
        wood_color = (0.8, 0.6, 0.3)
        line_color = (0.95, 0.95, 0.95)  # Blanco para las líneas
        
        # Normalizar coordenadas UV para que cubran toda la cancha
        # Escalar para simular una cancha completa
        court_u = (u - 0.5) * 2  # -1 a 1
        court_v = (v - 0.5) * 2  # -1 a 1
        
        # Grosor de las líneas
        line_thickness = 0.05
        
        # Línea central vertical (centro de la cancha)
        if abs(court_u) < line_thickness:
            return line_color
        
        # Líneas horizontales (líneas de fondo)
        if abs(court_v - 0.8) < line_thickness or abs(court_v + 0.8) < line_thickness:
            return line_color
        
        # Círculo central (simplificado como líneas circulares)
        center_distance = np.sqrt(court_u**2 + court_v**2)
        if abs(center_distance - 0.3) < line_thickness/2:  # Círculo central
            return line_color
        
        # Área de 3 puntos (arcos simplificados)
        # Lado izquierdo
        left_arc_distance = np.sqrt((court_u + 0.6)**2 + court_v**2)
        if abs(left_arc_distance - 0.4) < line_thickness/2 and court_u < -0.3:
            return line_color
        
        # Lado derecho  
        right_arc_distance = np.sqrt((court_u - 0.6)**2 + court_v**2)
        if abs(right_arc_distance - 0.4) < line_thickness/2 and court_u > 0.3:
            return line_color
        
        # Líneas laterales
        if abs(court_v - 0.9) < line_thickness or abs(court_v + 0.9) < line_thickness:
            return line_color
        
        # Áreas de tiros libres (rectángulos)
        # Izquierda
        if (abs(court_u + 0.7) < 0.15) and (abs(court_v) < 0.2) and \
           (abs(abs(court_u + 0.7) - 0.15) < line_thickness or abs(abs(court_v) - 0.2) < line_thickness):
            return line_color
        
        # Derecha
        if (abs(court_u - 0.7) < 0.15) and (abs(court_v) < 0.2) and \
           (abs(abs(court_u - 0.7) - 0.15) < line_thickness or abs(abs(court_v) - 0.2) < line_thickness):
            return line_color
        
        # Color de la madera por defecto
        return wood_color

class NormalMap(Texture):
    """Mapa de normales para bump mapping"""
    def __init__(self, filepath=None):
        super().__init__()
        if filepath:
            self.load_normal_map(filepath)
        else:
            self.create_default_normal()
    
    def load_normal_map(self, filepath):
        """Carga mapa de normales desde imagen"""
        try:
            path = Path(filepath)
            if not path.exists():
                self.create_default_normal()
                return
            
            img = Image.open(path)
            img = img.convert('RGB')
            
            self.width = img.width
            self.height = img.height
            
            # Convertir RGB a normal (0-255 -> -1 a 1)
            self.data = (np.array(img, dtype=np.float32) / 255.0) * 2.0 - 1.0
            
        except Exception as e:
            print(f"Error loading normal map {filepath}: {e}")
            self.create_default_normal()
    
    def create_default_normal(self):
        """Crea mapa de normales plano por defecto"""
        self.width = 1
        self.height = 1
        self.data = np.array([[[0.0, 0.0, 1.0]]], dtype=np.float32)
    
    def get_normal(self, u, v):
        """Obtiene normal perturbada en coordenadas UV"""
        if self.data is None:
            return np.array([0.0, 0.0, 1.0])
        
        u = u % 1.0
        v = v % 1.0
        
        x = int(u * (self.width - 1))
        y = int(v * (self.height - 1))
        
        x = max(0, min(x, self.width - 1))
        y = max(0, min(y, self.height - 1))
        
        return self.data[y, x]
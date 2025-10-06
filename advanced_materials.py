"""
Sistema de materiales avanzados para el raytracer.
Incluye soporte para texturas, mapas de normales y materiales procedurales.
"""
import numpy as np
from pathlib import Path

class AdvancedMaterial:
    """Material avanzado con soporte para texturas y efectos especiales"""
    
    def __init__(self, 
                 # Propiedades básicas
                 color=(1, 1, 1),
                 ka=0.1, kd=0.7, ks=0.2, 
                 shininess=32,
                 
                 # Propiedades ópticas
                 reflectivity=0.0,
                 transparency=0.0,
                 ior=1.5,
                 
                 # Texturas
                 diffuse_texture=None,
                 normal_map=None,
                 specular_map=None,
                 emission_map=None,
                 
                 # Efectos especiales
                 emission_color=(0, 0, 0),
                 emission_strength=0.0,
                 roughness=0.1,
                 metallic=0.0,
                 
                 # Tipo de material
                 material_type="standard"):
        
        self.color = np.array(color)
        self.ka = ka  # Componente ambiental
        self.kd = kd  # Componente difusa
        self.ks = ks  # Componente especular
        self.shininess = shininess
        
        self.reflectivity = reflectivity
        self.transparency = transparency
        self.ior = ior
        
        # Texturas
        self.diffuse_texture = diffuse_texture
        self.normal_map = normal_map
        self.specular_map = specular_map
        self.emission_map = emission_map
        
        # Emisión
        self.emission_color = np.array(emission_color)
        self.emission_strength = emission_strength
        
        # PBR properties
        self.roughness = roughness
        self.metallic = metallic
        
        self.material_type = material_type
    
    def get_diffuse_color(self, u=0.5, v=0.5):
        """Obtiene color difuso en coordenadas UV"""
        if self.diffuse_texture:
            tex_color = self.diffuse_texture.get_color(u, v)
            return np.array(tex_color) * self.color
        return self.color
    
    def get_specular_intensity(self, u=0.5, v=0.5):
        """Obtiene intensidad especular en coordenadas UV"""
        if self.specular_map:
            spec_color = self.specular_map.get_color(u, v)
            # Usar el canal rojo como intensidad especular
            return spec_color[0] * self.ks
        return self.ks
    
    def get_normal(self, surface_normal, u=0.5, v=0.5, tangent=None, bitangent=None):
        """Obtiene normal perturbada por normal map"""
        if not self.normal_map or tangent is None or bitangent is None:
            return surface_normal
        
        # Obtener normal del mapa
        normal_sample = self.normal_map.get_normal(u, v)
        
        # Crear matriz TBN (Tangent-Bitangent-Normal)
        tbn = np.column_stack([tangent, bitangent, surface_normal])
        
        # Transformar normal del espacio tangente al espacio mundo
        world_normal = tbn @ normal_sample
        
        # Normalizar
        return world_normal / (np.linalg.norm(world_normal) + 1e-8)
    
    def get_emission(self, u=0.5, v=0.5):
        """Obtiene color de emisión"""
        if self.emission_map:
            emission_tex = self.emission_map.get_color(u, v)
            return np.array(emission_tex) * self.emission_color * self.emission_strength
        return self.emission_color * self.emission_strength
    
    def is_emissive(self):
        """Verifica si el material emite luz"""
        return self.emission_strength > 0.0

# Materiales predefinidos
class MaterialPresets:
    """Materiales predefinidos comunes"""
    
    @staticmethod
    def create_glass(color=(0.9, 0.9, 1.0), ior=1.5):
        """Material de vidrio transparente"""
        return AdvancedMaterial(
            color=color,
            ka=0.05, kd=0.1, ks=0.9,
            shininess=128,
            reflectivity=0.1,
            transparency=0.8,
            ior=ior,
            material_type="glass"
        )
    
    @staticmethod
    def create_mirror(tint=(0.95, 0.95, 0.95)):
        """Material de espejo"""
        return AdvancedMaterial(
            color=tint,
            ka=0.02, kd=0.1, ks=0.1,
            shininess=256,
            reflectivity=0.9,
            material_type="mirror"
        )
    
    @staticmethod
    def create_metal(color=(0.7, 0.7, 0.8), roughness=0.1):
        """Material metálico"""
        return AdvancedMaterial(
            color=color,
            ka=0.05, kd=0.3, ks=0.7,
            shininess=int(256 * (1.0 - roughness)),
            reflectivity=0.6,
            metallic=1.0,
            roughness=roughness,
            material_type="metal"
        )
    
    @staticmethod
    def create_plastic(color=(1.0, 0.2, 0.2)):
        """Material plástico"""
        return AdvancedMaterial(
            color=color,
            ka=0.1, kd=0.8, ks=0.3,
            shininess=64,
            reflectivity=0.1,
            material_type="plastic"
        )
    
    @staticmethod
    def create_emissive(color=(1.0, 1.0, 1.0), strength=2.0):
        """Material emisivo (luz)"""
        return AdvancedMaterial(
            color=color,
            ka=0.0, kd=0.1, ks=0.0,
            shininess=1,
            emission_color=color,
            emission_strength=strength,
            material_type="emissive"
        )
    
    @staticmethod
    def create_textured(diffuse_texture, normal_map=None, base_color=(1, 1, 1)):
        """Material con textura"""
        return AdvancedMaterial(
            color=base_color,
            ka=0.1, kd=0.8, ks=0.2,
            shininess=32,
            diffuse_texture=diffuse_texture,
            normal_map=normal_map,
            material_type="textured"
        )

# Clase para compatibilidad con el sistema existente
class Material:
    """Material simple compatible con el sistema existente"""
    def __init__(self, color=(1,1,1), ka=0.1, kd=0.7, ks=0.2, shininess=32,
                 reflectivity=0.0, transparency=0.0, ior=1.5, mtype="opaque", 
                 tint_strength=1.0, texture=None):
        self.color = color
        self.ka = ka
        self.kd = kd
        self.ks = ks
        self.shininess = shininess
        self.reflectivity = reflectivity
        self.transparency = transparency
        self.ior = ior
        self.mtype = mtype
        self.tint_strength = float(tint_strength)
        
        # Añadir soporte básico para texturas
        self.texture = texture
    
    def get_color_at_uv(self, u, v):
        """Obtiene color en coordenadas UV"""
        if self.texture:
            tex_color = self.texture.get_color(u, v)
            return tuple(np.array(tex_color) * np.array(self.color))
        return self.color
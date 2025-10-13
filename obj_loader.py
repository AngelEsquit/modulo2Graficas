"""
Sistema avanzado de carga de modelos OBJ para el raytracer.
Incluye soporte para normales, coordenadas UV y materiales MTL.
"""
import numpy as np
from pathlib import Path
import re

class OBJLoader:
    """Cargador avanzado de archivos OBJ"""
    
    def __init__(self):
        self.vertices = []
        self.normals = []
        self.uvs = []
        self.faces = []
        self.materials = {}
        self.current_material = None
    
    def load_obj(self, filepath, scale=1.0, position=(0, 0, 0), rotation=(0, 0, 0), align_min_y_to=None):
        """Carga un archivo OBJ con soporte completo
        
        Params:
        - filepath: ruta del archivo OBJ
        - scale: factor de escala uniforme
        - position: traslación (x,y,z)
        - rotation: rotación Euler en grados (rx, ry, rz)
        - align_min_y_to: si no es None, ajusta el modelo para que su Y mínima coincida con este valor
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"OBJ file not found: {filepath}")
        
        # Resetear datos
        self.vertices = []
        self.normals = []
        self.uvs = []
        self.faces = []
        
        # Cargar materiales si existe archivo MTL
        mtl_path = filepath.with_suffix('.mtl')
        if mtl_path.exists():
            # Record base dir to resolve relative texture paths later
            self._base_dir = mtl_path.parent
            self.load_mtl(mtl_path)
        
        # Cargar geometría
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                if not line or line.startswith('#'):
                    continue
                
                try:
                    self._parse_obj_line(line)
                except Exception as e:
                    print(f"Warning: Error parsing line {line_num} in {filepath}: {e}")
        
        # Transformar vértices
        if self.vertices:
            vertices_array = np.array(self.vertices)
            
            # Aplicar escala
            vertices_array *= scale
            
            # Aplicar rotación
            if any(rotation):
                rotation_matrix = self._create_rotation_matrix(*rotation)
                vertices_array = (rotation_matrix @ vertices_array.T).T
            
            # Aplicar traslación
            vertices_array += np.array(position)
            
            # Alinear Y mínima al valor indicado (por ejemplo, al piso)
            if align_min_y_to is not None:
                min_y = float(vertices_array[:, 1].min())
                delta_y = float(align_min_y_to) - min_y
                vertices_array[:, 1] += delta_y

            self.vertices = vertices_array.tolist()
        
        return self._create_mesh_objects(base_path=filepath.parent)
    
    def _parse_obj_line(self, line):
        """Parsea una línea del archivo OBJ"""
        parts = line.split()
        if not parts:
            return
        
        command = parts[0]
        
        if command == 'v':  # Vértice
            if len(parts) >= 4:
                x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                self.vertices.append([x, y, z])
        
        elif command == 'vn':  # Normal
            if len(parts) >= 4:
                nx, ny, nz = float(parts[1]), float(parts[2]), float(parts[3])
                # Normalizar la normal
                normal = np.array([nx, ny, nz])
                normal = normal / (np.linalg.norm(normal) + 1e-8)
                self.normals.append(normal.tolist())
        
        elif command == 'vt':  # Coordenada UV
            if len(parts) >= 3:
                u, v = float(parts[1]), float(parts[2])
                # Algunos archivos OBJ tienen V invertido
                self.uvs.append([u, 1.0 - v])
        
        elif command == 'f':  # Cara
            self._parse_face(parts[1:])
        
        elif command == 'usemtl':  # Usar material
            if len(parts) >= 2:
                self.current_material = parts[1]
    
    def _parse_face(self, face_data):
        """Parsea una cara (puede ser triángulo, quad, etc.)"""
        indices = []
        
        for vertex_data in face_data:
            # Formato: v/vt/vn o v//vn o v/vt o v
            parts = vertex_data.split('/')
            
            # Índice del vértice (obligatorio)
            v_idx = int(parts[0]) - 1 if parts[0] else 0
            
            # Índice de UV (opcional)
            uv_idx = int(parts[1]) - 1 if len(parts) > 1 and parts[1] else None
            
            # Índice de normal (opcional)
            n_idx = int(parts[2]) - 1 if len(parts) > 2 and parts[2] else None
            
            indices.append({
                'vertex': v_idx,
                'uv': uv_idx,
                'normal': n_idx,
                'material': self.current_material
            })
        
        # Triangular caras con más de 3 vértices
        if len(indices) == 3:
            self.faces.append(indices)
        elif len(indices) == 4:  # Quad -> 2 triángulos
            # Triángulo 1: 0, 1, 2
            self.faces.append([indices[0], indices[1], indices[2]])
            # Triángulo 2: 0, 2, 3
            self.faces.append([indices[0], indices[2], indices[3]])
        elif len(indices) > 4:  # Polígono -> ventilador de triángulos
            for i in range(1, len(indices) - 1):
                self.faces.append([indices[0], indices[i], indices[i + 1]])
    
    def load_mtl(self, filepath):
        """Carga archivo de materiales MTL"""
        current_material = None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split()
                if not parts:
                    continue
                
                command = parts[0]
                
                if command == 'newmtl':  # Nuevo material
                    current_material = parts[1]
                    self.materials[current_material] = {
                        'diffuse': [0.8, 0.8, 0.8],
                        'specular': [0.0, 0.0, 0.0],
                        'ambient': [0.2, 0.2, 0.2],
                        'shininess': 32,
                        'transparency': 0.0,
                        'ior': 1.0,
                        'diffuse_map': None,
                        'normal_map': None,
                        'specular_map': None
                    }
                
                elif current_material and len(parts) >= 4:
                    if command == 'Kd':  # Diffuse color
                        r, g, b = float(parts[1]), float(parts[2]), float(parts[3])
                        self.materials[current_material]['diffuse'] = [r, g, b]
                    
                    elif command == 'Ks':  # Specular color
                        r, g, b = float(parts[1]), float(parts[2]), float(parts[3])
                        self.materials[current_material]['specular'] = [r, g, b]
                    
                    elif command == 'Ka':  # Ambient color
                        r, g, b = float(parts[1]), float(parts[2]), float(parts[3])
                        self.materials[current_material]['ambient'] = [r, g, b]
                
                elif current_material and len(parts) >= 2:
                    if command == 'Ns':  # Shininess
                        self.materials[current_material]['shininess'] = float(parts[1])
                    
                    elif command == 'd' or command == 'Tr':  # Transparency
                        alpha = float(parts[1])
                        self.materials[current_material]['transparency'] = 1.0 - alpha
                    
                    elif command == 'Ni':  # Index of refraction
                        self.materials[current_material]['ior'] = float(parts[1])
                    
                    elif command == 'map_Kd':  # Diffuse texture map
                        texture_path = ' '.join(parts[1:])
                        self.materials[current_material]['diffuse_map'] = texture_path
                    
                    elif command == 'map_Bump' or command == 'bump':  # Normal map
                        normal_path = ' '.join(parts[1:])
                        self.materials[current_material]['normal_map'] = normal_path
                    
                    elif command == 'map_Ks':  # Specular map
                        specular_path = ' '.join(parts[1:])
                        self.materials[current_material]['specular_map'] = specular_path
    
    def _create_rotation_matrix(self, rx, ry, rz):
        """Crea matriz de rotación desde ángulos de Euler (grados)"""
        rx, ry, rz = np.radians([rx, ry, rz])
        
        # Matriz de rotación en X
        Rx = np.array([
            [1, 0, 0],
            [0, np.cos(rx), -np.sin(rx)],
            [0, np.sin(rx), np.cos(rx)]
        ])
        
        # Matriz de rotación en Y
        Ry = np.array([
            [np.cos(ry), 0, np.sin(ry)],
            [0, 1, 0],
            [-np.sin(ry), 0, np.cos(ry)]
        ])
        
        # Matriz de rotación en Z
        Rz = np.array([
            [np.cos(rz), -np.sin(rz), 0],
            [np.sin(rz), np.cos(rz), 0],
            [0, 0, 1]
        ])
        
        # Combinar rotaciones: Rz * Ry * Rx
        return Rz @ Ry @ Rx
    
    def _create_mesh_objects(self, base_path: Path | None = None):
        """Crea objetos de malla a partir de los datos cargados"""
        if not self.faces or not self.vertices:
            return []
        
        # Agrupar caras por material
        material_groups = {}
        
        for face in self.faces:
            material_name = face[0].get('material', 'default')
            if material_name not in material_groups:
                material_groups[material_name] = []
            material_groups[material_name].append(face)
        
        # Crear un objeto de malla por material
        mesh_objects = []
        
        for material_name, faces in material_groups.items():
            # Crear material
            if material_name in self.materials:
                mat_data = self.materials[material_name]
                from advanced_materials import AdvancedMaterial
                
                material = AdvancedMaterial(
                    color=mat_data['diffuse'],
                    ka=0.1, 
                    kd=0.7,
                    ks=np.linalg.norm(mat_data['specular']),
                    shininess=max(1, int(mat_data['shininess'])),
                    transparency=mat_data['transparency'],
                    ior=mat_data['ior']
                )
                
                # Cargar texturas si están especificadas
                if mat_data['diffuse_map']:
                    try:
                        from texture import ImageTexture
                        texture_path = Path(mat_data['diffuse_map'])
                        if not texture_path.is_absolute():
                            # Resolver relativo al .mtl/.obj
                            if hasattr(self, '_base_dir') and self._base_dir:
                                texture_path = self._base_dir / texture_path
                            elif base_path:
                                texture_path = base_path / texture_path
                        else:
                            # Si es absoluto pero no existe (caso exportado con ruta local), intentar por nombre en carpeta del MTL/OBJ
                            if not texture_path.exists():
                                fname = texture_path.name
                                if hasattr(self, '_base_dir') and self._base_dir and (self._base_dir / fname).exists():
                                    texture_path = self._base_dir / fname
                                elif base_path and (base_path / fname).exists():
                                    texture_path = base_path / fname
                        material.diffuse_texture = ImageTexture(str(texture_path))
                    except Exception as e:
                        print(f"Warning: Could not load texture {mat_data['diffuse_map']}: {e}")
            else:
                from advanced_materials import AdvancedMaterial
                material = AdvancedMaterial()
            
            # Crear malla
            mesh = AdvancedMesh(
                vertices=np.array(self.vertices),
                faces=faces,
                normals=self.normals,
                uvs=self.uvs,
                material=material
            )
            
            mesh_objects.append(mesh)
        
        return mesh_objects

class AdvancedMesh:
    """Malla avanzada con soporte para normales, UVs y materiales"""
    
    def __init__(self, vertices, faces, normals=None, uvs=None, material=None, position=(0, 0, 0)):
        self.vertices = np.array(vertices, dtype=float)
        self.faces = faces
        self.normals = normals or []
        self.uvs = uvs or []
        self.material = material
        self.position = np.array(position, dtype=float)
        self.type = "AdvancedMesh"
        
        # Construir estructura de aceleración si hay muchas caras
        if len(faces) > 100:
            self._build_bvh()
    
    def _build_bvh(self):
        """Construye una jerarquía de volúmenes delimitadores (BVH) para acelerar intersecciones"""
        # Implementación básica - calcular bounding box de cada triángulo
        self.triangle_boxes = []
        
        for face in self.faces:
            v0_idx = face[0]['vertex']
            v1_idx = face[1]['vertex'] 
            v2_idx = face[2]['vertex']
            
            if (v0_idx < len(self.vertices) and 
                v1_idx < len(self.vertices) and 
                v2_idx < len(self.vertices)):
                
                v0 = self.vertices[v0_idx] + self.position
                v1 = self.vertices[v1_idx] + self.position
                v2 = self.vertices[v2_idx] + self.position
                
                min_coord = np.minimum(np.minimum(v0, v1), v2)
                max_coord = np.maximum(np.maximum(v0, v1), v2)
                
                self.triangle_boxes.append((min_coord, max_coord))
            else:
                # Triángulo inválido
                self.triangle_boxes.append((np.array([0, 0, 0]), np.array([0, 0, 0])))
    
    def ray_intersect(self, origin, direction):
        """Encuentra intersección rayo-malla"""
        closest_t = float('inf')
        closest_result = None
        
        # Usar BVH si está disponible para optimizar
        face_indices = range(len(self.faces))
        if hasattr(self, 'triangle_boxes'):
            face_indices = self._get_potential_faces(origin, direction)
        
        for i in face_indices:
            if i >= len(self.faces):
                continue
                
            face = self.faces[i]
            result = self._intersect_triangle(origin, direction, face)
            
            if result and result['t'] < closest_t and result['t'] > 1e-6:
                closest_t = result['t']
                closest_result = result
        
        return closest_result
    
    def _get_potential_faces(self, origin, direction):
        """Obtiene caras que podrían intersectar usando BVH básico"""
        # Implementación simple - verificar intersección rayo-caja para cada triángulo
        potential_faces = []
        
        for i, (min_coord, max_coord) in enumerate(self.triangle_boxes):
            if self._ray_box_intersect(origin, direction, min_coord, max_coord):
                potential_faces.append(i)
        
        return potential_faces if potential_faces else range(len(self.faces))
    
    def _ray_box_intersect(self, origin, direction, box_min, box_max):
        """Verifica intersección rayo-caja"""
        inv_direction = 1.0 / (direction + 1e-8)
        
        t1 = (box_min - origin) * inv_direction
        t2 = (box_max - origin) * inv_direction
        
        t_min = np.minimum(t1, t2)
        t_max = np.maximum(t1, t2)
        
        t_near = np.max(t_min)
        t_far = np.min(t_max)
        
        return t_near <= t_far and t_far > 0
    
    def _intersect_triangle(self, origin, direction, face):
        """Intersección rayo-triángulo usando algoritmo de Möller-Trumbore"""
        # Obtener índices de vértices
        v0_idx = face[0]['vertex']
        v1_idx = face[1]['vertex']
        v2_idx = face[2]['vertex']
        
        # Verificar índices válidos
        if (v0_idx >= len(self.vertices) or 
            v1_idx >= len(self.vertices) or 
            v2_idx >= len(self.vertices)):
            return None
        
        # Obtener vértices en espacio mundial
        v0 = self.vertices[v0_idx] + self.position
        v1 = self.vertices[v1_idx] + self.position
        v2 = self.vertices[v2_idx] + self.position
        
        # Algoritmo de Möller-Trumbore
        edge1 = v1 - v0
        edge2 = v2 - v0
        h = np.cross(direction, edge2)
        a = np.dot(edge1, h)
        
        if abs(a) < 1e-8:  # Rayo paralelo al triángulo
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
        
        if t <= 1e-6:
            return None
        
        # Punto de intersección
        point = origin + direction * t
        
        # Calcular normal
        normal = self._get_normal_at_face(face, u, v)
        
        # Calcular coordenadas UV
        uv_u, uv_v = self._get_uv_at_face(face, u, v)
        
        return {
            "t": t,
            "point": point,
            "normal": normal,
            "material": self.material,
            "u": uv_u,
            "v": uv_v
        }
    
    def _get_normal_at_face(self, face, u, v):
        """Obtiene normal interpolada o calculada para la cara"""
        # Si hay normales por vértice, interpolar
        if (self.normals and 
            all('normal' in vertex and vertex['normal'] is not None for vertex in face)):
            
            n0_idx = face[0]['normal']
            n1_idx = face[1]['normal']
            n2_idx = face[2]['normal']
            
            if (n0_idx < len(self.normals) and 
                n1_idx < len(self.normals) and 
                n2_idx < len(self.normals)):
                
                n0 = np.array(self.normals[n0_idx])
                n1 = np.array(self.normals[n1_idx])
                n2 = np.array(self.normals[n2_idx])
                
                # Interpolación baricéntrica
                normal = n0 * (1 - u - v) + n1 * u + n2 * v
                return normal / (np.linalg.norm(normal) + 1e-8)
        
        # Calcular normal de la cara
        v0_idx = face[0]['vertex']
        v1_idx = face[1]['vertex']
        v2_idx = face[2]['vertex']
        
        v0 = self.vertices[v0_idx]
        v1 = self.vertices[v1_idx]
        v2 = self.vertices[v2_idx]
        
        edge1 = v1 - v0
        edge2 = v2 - v0
        normal = np.cross(edge1, edge2)
        
        return normal / (np.linalg.norm(normal) + 1e-8)
    
    def _get_uv_at_face(self, face, u, v):
        """Obtiene coordenadas UV interpoladas"""
        # Si hay coordenadas UV, interpolar
        if (self.uvs and 
            all('uv' in vertex and vertex['uv'] is not None for vertex in face)):
            
            uv0_idx = face[0]['uv']
            uv1_idx = face[1]['uv']
            uv2_idx = face[2]['uv']
            
            if (uv0_idx < len(self.uvs) and 
                uv1_idx < len(self.uvs) and 
                uv2_idx < len(self.uvs)):
                
                uv0 = np.array(self.uvs[uv0_idx])
                uv1 = np.array(self.uvs[uv1_idx])
                uv2 = np.array(self.uvs[uv2_idx])
                
                # Interpolación baricéntrica
                uv = uv0 * (1 - u - v) + uv1 * u + uv2 * v
                return uv[0], uv[1]
        
        # UVs por defecto
        return 0.5, 0.5
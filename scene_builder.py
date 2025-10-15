"""
Sistema de construcción de escenas avanzadas para demostrar todas las capacidades del raytracer.
Incluye escenas prediseñadas que cumplen con los requisitos del proyecto.
"""
import numpy as np
from pathlib import Path

def create_materials_showcase_scene(renderer):
    """Crea una escena que demuestra diferentes tipos de materiales (20 puntos)"""
    from advanced_materials import AdvancedMaterial, MaterialPresets
    from texture import ImageTexture, ProceduralTexture
    from figure import Sphere, Plane
    from advanced_shapes import Ellipsoid, Capsule, Octahedron, Hyperboloid
    from lighting import PointLight, SpotLight, DirectionalLight
    
    # Limpiar escena
    renderer.scene.clear()
    renderer.lights.clear()
    
    print("Creating materials showcase scene...")
    
    # 1. Material con textura (OBLIGATORIO - al menos uno debe usar textura)
    try:
        # Intentar cargar una textura de imagen
        wood_texture = ImageTexture("textures/wood.jpg")  # Si existe
    except:
        # Usar textura procedimental si no hay imagen
        wood_texture = ProceduralTexture("wood")
    
    textured_material = MaterialPresets.create_textured(
        diffuse_texture=wood_texture,
        base_color=(0.8, 0.6, 0.4)
    )
    
    # Esfera con textura de madera en el centro
    textured_sphere = Sphere(
        position=(-2, 0, -5),
        radius=1.0,
        material=textured_material
    )
    renderer.scene.append(textured_sphere)
    
    # 2. Material de vidrio transparente
    glass_material = MaterialPresets.create_glass(
        color=(0.9, 0.95, 1.0),
        ior=1.5
    )
    
    glass_sphere = Sphere(
        position=(0, 0, -5),
        radius=1.0,
        material=glass_material
    )
    renderer.scene.append(glass_sphere)
    
    # 3. Material metálico reflectivo
    metal_material = MaterialPresets.create_metal(
        color=(0.8, 0.8, 0.9),
        roughness=0.1
    )
    
    metal_ellipsoid = Ellipsoid(
        position=(2, 0, -5),
        radii=[0.8, 1.2, 0.8],
        material=metal_material
    )
    renderer.scene.append(metal_ellipsoid)
    
    # 4. Material emisivo (luz)
    emissive_material = MaterialPresets.create_emissive(
        color=(1.0, 0.6, 0.2),
        strength=3.0
    )
    
    light_orb = Sphere(
        position=(0, 3, -3),
        radius=0.3,
        material=emissive_material
    )
    renderer.scene.append(light_orb)
    
    # Suelo con textura de damero
    checkerboard_texture = ProceduralTexture("checkerboard")
    floor_material = AdvancedMaterial(
        color=(1.0, 1.0, 1.0),
        ka=0.1, kd=0.8, ks=0.1,
        shininess=16,
        diffuse_texture=checkerboard_texture
    )
    
    floor = Plane(
        point=(0, -2, 0),
        normal=(0, 1, 0),
        material=floor_material
    )
    renderer.scene.append(floor)
    
    # Iluminación
    renderer.lights.append(PointLight(
        position=(5, 5, 0),
        color=(1.0, 0.95, 0.8),
        intensity=2.0
    ))
    
    renderer.lights.append(PointLight(
        position=(-3, 3, -2),
        color=(0.8, 0.9, 1.0),
        intensity=1.5
    ))
    
    print("Materials showcase scene created successfully!")

def create_geometry_showcase_scene(renderer):
    """Crea una escena con figuras geométricas avanzadas (20 puntos)"""
    from advanced_materials import AdvancedMaterial, MaterialPresets
    from texture import ProceduralTexture
    from advanced_shapes import Ellipsoid, Capsule, Octahedron, Hyperboloid, Paraboloid, Dodecahedron
    from figure import Sphere, Plane
    from lighting import PointLight, SpotLight
    
    renderer.scene.clear()
    renderer.lights.clear()
    
    print("Creating geometry showcase scene...")
    
    # Materiales variados
    red_plastic = MaterialPresets.create_plastic((0.8, 0.2, 0.2))
    blue_metal = MaterialPresets.create_metal((0.2, 0.4, 0.8))
    green_glass = MaterialPresets.create_glass((0.7, 1.0, 0.7))
    gold_metal = MaterialPresets.create_metal((1.0, 0.8, 0.2))
    
    # 1. Elipsoide
    ellipsoid = Ellipsoid(
        position=(-4, 0, -6),
        radii=[0.8, 1.2, 0.6],
        material=red_plastic
    )
    renderer.scene.append(ellipsoid)
    
    # 2. Cápsula
    capsule = Capsule(
        position=(-2, 0, -6),
        height=2.0,
        radius=0.5,
        material=blue_metal
    )
    renderer.scene.append(capsule)
    
    # 3. Octaedro
    octahedron = Octahedron(
        position=(0, 0, -6),
        size=1.0,
        material=green_glass
    )
    renderer.scene.append(octahedron)
    
    # 4. Hiperboloide
    hyperboloid = Hyperboloid(
        position=(2, 0, -6),
        a=0.8, b=0.8, c=1.2,
        material=gold_metal
    )
    renderer.scene.append(hyperboloid)
    
    # 5. Paraboloide (figura adicional)
    paraboloid = Paraboloid(
        position=(4, -1, -6),
        a=1.0, b=1.0, height=2.0,
        material=MaterialPresets.create_plastic((0.6, 0.2, 0.8))
    )
    renderer.scene.append(paraboloid)
    
    # 6. Dodecaedro (figura compleja adicional)
    dodecahedron = Dodecahedron(
        position=(0, 2.5, -4),
        size=0.8,
        material=MaterialPresets.create_glass((1.0, 0.9, 0.7), ior=1.8)
    )
    renderer.scene.append(dodecahedron)
    
    # Suelo
    stripes_texture = ProceduralTexture("stripes")
    floor_material = AdvancedMaterial(
        color=(0.9, 0.9, 0.9),
        ka=0.1, kd=0.7, ks=0.2,
        diffuse_texture=stripes_texture
    )
    
    floor = Plane(
        point=(0, -2, 0),
        normal=(0, 1, 0),
        material=floor_material
    )
    renderer.scene.append(floor)
    
    # Iluminación múltiple (10 puntos adicionales)
    # Luz principal
    main_light = PointLight(
        position=(0, 5, 0),
        color=(1.0, 0.95, 0.8),
        intensity=3.0
    )
    renderer.lights.append(main_light)
    
    # Spot light para destacar el dodecaedro
    spot = SpotLight(
        position=(3, 4, -2),
        direction=np.array([0, 2.5, -4]) - np.array([3, 4, -2]),
        color=(0.8, 0.6, 1.0),
        intensity=2.0,
        inner_angle=15,
        outer_angle=30
    )
    renderer.lights.append(spot)
    
    # Luces de relleno
    fill_lights = [
        PointLight((-5, 2, -3), (1.0, 0.7, 0.7), 1.0),
        PointLight((5, 2, -3), (0.7, 0.7, 1.0), 1.0),
        PointLight((0, 1, -10), (0.9, 1.0, 0.9), 0.8)
    ]
    
    for light in fill_lights:
        renderer.lights.append(light)
    
    print("Geometry showcase scene created successfully!")

def create_complex_scene_with_obj(renderer):
    """Crea una escena compleja con modelos OBJ y más de 10 figuras (30 puntos de complejidad + 20 de OBJ)"""
    from advanced_materials import AdvancedMaterial, MaterialPresets
    from texture import ProceduralTexture, ImageTexture
    from figure import Sphere, Plane, Cube, Cylinder, Cone
    from advanced_shapes import Ellipsoid, Capsule, Octahedron
    from obj_loader import OBJLoader
    from lighting import PointLight, DirectionalLight, SpotLight
    
    renderer.scene.clear()
    renderer.lights.clear()
    
    print("Creating complex scene with OBJ models...")
    
    # Intentar cargar modelos OBJ (si existen)
    obj_loader = OBJLoader()
    
    # Lista de posibles archivos OBJ para probar
    obj_candidates = [
        "models/teapot.obj",
        "models/suzanne.obj", 
        "models/cube.obj",
        "models/sphere.obj",
        "teapot.obj",
        "suzanne.obj"
    ]
    
    obj_loaded = False
    for obj_file in obj_candidates:
        try:
            obj_path = Path(obj_file)
            if obj_path.exists():
                print(f"Loading OBJ model: {obj_file}")
                meshes = obj_loader.load_obj(
                    obj_file,
                    scale=2.0,
                    position=(0, 1, -8),
                    rotation=(0, 45, 0)
                )
                
                for mesh in meshes:
                    renderer.scene.append(mesh)
                
                obj_loaded = True
                break
        except Exception as e:
            print(f"Could not load {obj_file}: {e}")
    
    if not obj_loaded:
        print("No OBJ models found, creating procedural centerpiece...")
        # Crear una figura compleja como sustituto
        centerpiece = Octahedron(
            position=(0, 1, -8),
            size=1.5,
            material=MaterialPresets.create_glass((0.9, 0.9, 1.0))
        )
        renderer.scene.append(centerpiece)
    
    # Crear más de 10 figuras para conseguir 30 puntos de complejidad
    
    # Fila de esferas con diferentes materiales
    sphere_materials = [
        MaterialPresets.create_metal((0.8, 0.2, 0.2)),
        MaterialPresets.create_plastic((0.2, 0.8, 0.2)),
        MaterialPresets.create_glass((0.2, 0.2, 0.8)),
        MaterialPresets.create_metal((0.8, 0.8, 0.2)),
        MaterialPresets.create_plastic((0.8, 0.2, 0.8))
    ]
    
    for i, material in enumerate(sphere_materials):
        sphere = Sphere(
            position=(-6 + i * 3, 0, -3),
            radius=0.6,
            material=material
        )
        renderer.scene.append(sphere)  # 5 esferas
    
    # Figuras geométricas variadas
    shapes = [
        Cube((-4, -1, -12), 1.0, MaterialPresets.create_plastic((0.6, 0.4, 0.2))),
        Cylinder((-2, -1, -12), 0.5, 2.0, MaterialPresets.create_metal((0.7, 0.7, 0.8))),
        Cone((0, -1, -12), 0.7, 1.8, MaterialPresets.create_glass((0.9, 0.7, 0.9))),
        Capsule((2, 0, -12), 1.5, 0.4, MaterialPresets.create_plastic((0.3, 0.7, 0.8))),
        Ellipsoid((4, 0, -12), [0.6, 1.0, 0.8], MaterialPresets.create_metal((0.9, 0.6, 0.3)))
    ]  # 5 figuras más
    
    for shape in shapes:
        renderer.scene.append(shape)
    
    # Torres de cubos apilados
    for tower in range(3):
        x_pos = -3 + tower * 3
        for level in range(3):
            cube = Cube(
                (x_pos, -2 + level * 0.8, -15),
                0.6,
                MaterialPresets.create_plastic((0.5 + tower * 0.2, 0.3, 0.7 - tower * 0.1))
            )
            renderer.scene.append(cube)  # 9 cubos más
    
    # Total hasta ahora: 1 (OBJ/centerpiece) + 5 (esferas) + 5 (formas) + 9 (cubos) = 20 figuras
    
    # Suelo con textura
    dots_texture = ProceduralTexture("dots")
    floor_material = AdvancedMaterial(
        color=(0.8, 0.8, 0.9),
        ka=0.1, kd=0.7, ks=0.3,
        shininess=64,
        diffuse_texture=dots_texture
    )
    
    floor = Plane(
        point=(0, -3, 0),
        normal=(0, 1, 0),
        material=floor_material
    )
    renderer.scene.append(floor)
    
    # Paredes para crear ambiente
    wall_material = AdvancedMaterial(
        color=(0.9, 0.9, 0.8),
        ka=0.2, kd=0.6, ks=0.2,
        shininess=32
    )
    
    # Pared trasera
    back_wall = Plane(
        point=(0, 0, -20),
        normal=(0, 0, 1),
        material=wall_material
    )
    renderer.scene.append(back_wall)
    
    # Sistema de iluminación complejo (10 puntos por múltiples luces)
    
    # Luz direccional (sol)
    sun = DirectionalLight(
        direction=(0.3, -1, 0.5),
        color=(1.0, 0.95, 0.8),
        intensity=1.5
    )
    renderer.lights.append(sun)
    
    # Luces puntuales principales
    key_lights = [
        PointLight((-5, 4, -5), (1.0, 0.8, 0.6), 2.5),
        PointLight((5, 4, -5), (0.6, 0.8, 1.0), 2.5),
        PointLight((0, 6, -10), (0.9, 0.9, 0.9), 3.0)
    ]
    
    for light in key_lights:
        renderer.lights.append(light)
    
    # Spot lights para efectos dramáticos
    spots = [
        SpotLight(
            position=(0, 5, -3),
            direction=(0, 1, -8) - np.array([0, 5, -3]),  # Hacia el centro
            color=(1.0, 0.9, 0.7),
            intensity=2.0,
            inner_angle=20,
            outer_angle=40
        ),
        SpotLight(
            position=(-8, 3, -8),
            direction=(0, 0, -12) - np.array([-8, 3, -8]),  # Hacia las formas
            color=(0.8, 0.6, 1.0),
            intensity=1.8,
            inner_angle=25,
            outer_angle=45
        )
    ]
    
    for spot in spots:
        renderer.lights.append(spot)
    
    # Luces de ambiente/relleno
    ambient_lights = [
        PointLight((8, 2, -8), (0.7, 0.9, 0.8), 1.0),
        PointLight((-8, 2, -12), (0.9, 0.7, 0.8), 1.0),
        PointLight((0, 1, 2), (0.8, 0.8, 1.0), 0.8)  # Luz frontal suave
    ]
    
    for light in ambient_lights:
        renderer.lights.append(light)
    
    print(f"Complex scene created with {len(renderer.scene)} objects and {len(renderer.lights)} lights!")
    print("This scene targets maximum points:")
    print("- 30 points: >10 figures complexity")
    print("- 20 points: 4 different materials with textures")
    print("- 20 points: 4+ new geometric shapes") 
    print("- 20 points: OBJ model rendering")
    print("- 10 points: Multiple light types")
    print("- 5 points: Environment map integration")

def create_artistic_scene(renderer):
    """Crea una escena artística para demostrar la estética (20 puntos estéticos)"""
    from advanced_materials import AdvancedMaterial, MaterialPresets
    from texture import ProceduralTexture
    from figure import Sphere, Plane
    from advanced_shapes import Ellipsoid, Capsule, Dodecahedron
    from lighting import PointLight, SpotLight, AreaLight
    
    renderer.scene.clear()
    renderer.lights.clear()
    
    print("Creating artistic scene...")
    
    # Tema: "Jardín de cristal futurista"
    
    # Orbes de cristal flotantes con emisión interna
    crystal_materials = [
        MaterialPresets.create_glass((0.9, 0.7, 1.0), ior=2.4),  # Cristal violeta
        MaterialPresets.create_glass((0.7, 1.0, 0.9), ior=1.8),  # Cristal verde
        MaterialPresets.create_glass((1.0, 0.9, 0.7), ior=1.6),  # Cristal dorado
    ]
    
    # Configuración en espiral dorada
    golden_ratio = 1.618
    for i in range(8):
        angle = i * golden_ratio * 2 * np.pi / 8
        radius = 3 + i * 0.5
        height = np.sin(i * 0.8) * 2
        
        x = radius * np.cos(angle)
        z = radius * np.sin(angle) - 8
        y = height
        
        material = crystal_materials[i % 3]
        
        # Alternar entre esferas y elipsoides
        if i % 2 == 0:
            orb = Sphere((x, y, z), 0.6 + i * 0.1, material)
        else:
            orb = Ellipsoid((x, y, z), [0.5, 0.8, 0.5], material)
        
        renderer.scene.append(orb)
    
    # Centro: Dodecaedro principal como foco
    center_material = AdvancedMaterial(
        color=(0.95, 0.95, 1.0),
        ka=0.05, kd=0.2, ks=0.8,
        shininess=256,
        reflectivity=0.7,
        transparency=0.2,
        ior=2.0,
        emission_color=(0.5, 0.7, 1.0),
        emission_strength=1.5
    )
    
    centerpiece = Dodecahedron(
        position=(0, 1, -8),
        size=1.2,
        material=center_material
    )
    renderer.scene.append(centerpiece)
    
    # Pilares de soporte
    pillar_material = MaterialPresets.create_metal((0.3, 0.4, 0.5))
    
    for i in range(4):
        angle = i * np.pi / 2
        x = 6 * np.cos(angle)
        z = 6 * np.sin(angle) - 8
        
        pillar = Capsule(
            position=(x, -1, z),
            height=4,
            radius=0.2,
            material=pillar_material
        )
        renderer.scene.append(pillar)
    
    # Suelo reflectante con patrón hexagonal
    hex_texture = ProceduralTexture("dots")  # Simular hexágonos con puntos
    floor_material = AdvancedMaterial(
        color=(0.1, 0.15, 0.2),
        ka=0.1, kd=0.3, ks=0.9,
        shininess=128,
        reflectivity=0.6,
        diffuse_texture=hex_texture
    )
    
    floor = Plane(
        point=(0, -3, 0),
        normal=(0, 1, 0),
        material=floor_material
    )
    renderer.scene.append(floor)
    
    # Iluminación artística
    
    # Luz principal suave desde arriba
    main_light = PointLight(
        position=(0, 8, -5),
        color=(0.9, 0.95, 1.0),
        intensity=2.0,
        attenuation_linear=0.05
    )
    renderer.lights.append(main_light)
    
    # Luces de colores para crear ambiente
    color_lights = [
        PointLight((4, 3, -6), (1.0, 0.6, 0.8), 1.5),   # Rosa
        PointLight((-4, 3, -6), (0.6, 0.8, 1.0), 1.5),  # Azul
        PointLight((0, 2, -12), (0.8, 1.0, 0.6), 1.2),  # Verde
        PointLight((0, 5, -2), (1.0, 0.9, 0.7), 1.0),   # Dorado
    ]
    
    for light in color_lights:
        renderer.lights.append(light)
    
    # Spot light dramático hacia el centro
    dramatic_spot = SpotLight(
        position=(6, 6, -2),
        direction=np.array([0, 1, -8]) - np.array([6, 6, -2]),
        color=(1.0, 0.8, 0.9),
        intensity=3.0,
        inner_angle=15,
        outer_angle=35
    )
    renderer.lights.append(dramatic_spot)
    
    print("Artistic scene created successfully!")
    print("Theme: Futuristic Crystal Garden")
    print("Features: Reflective materials, emission, complex lighting, golden ratio composition")

# Función principal para construir escena según configuración
def create_basketball_court_scene(renderer):
    """Crea una cancha de basketball con suelo y canastas"""
    from advanced_materials import AdvancedMaterial, MaterialPresets
    from texture import ProceduralTexture, ImageTexture
    from figure import Sphere, Plane, Cylinder, Cube, Box, AxisCylinder, Torus
    from advanced_shapes import Capsule
    from lighting import PointLight, DirectionalLight, SpotLight
    from config import TEXTURE_DIR, USE_PROCEDURAL_TEXTURES, FLOOR_TILE_U, FLOOR_TILE_V, FLOOR_TEXTURE_FILENAME, FLOOR_UV_ROTATION_DEG, FLOOR_WRAP_MODE
    
    renderer.scene.clear()
    renderer.lights.clear()
    
    print("Creating basketball court scene...")
    
    # === SUELO DE LA CANCHA ===
    # Intentar cargar textura de madera y repetirla (tiling) sobre el piso
    wood_tex = None
    try:
        wood_path = TEXTURE_DIR / FLOOR_TEXTURE_FILENAME
        if wood_path.exists() and not USE_PROCEDURAL_TEXTURES:
            wood_tex = ImageTexture(str(wood_path))
            wood_tex.tile_u = float(FLOOR_TILE_U)
            wood_tex.tile_v = float(FLOOR_TILE_V)
            try:
                wood_tex.wrap_mode = str(FLOOR_WRAP_MODE)
            except Exception:
                pass
    except Exception:
        wood_tex = None

    if wood_tex is None:
        # Fallback a textura procedimental de madera (sin tiling explícito)
        wood_tex = ProceduralTexture("wood")
    
    # Material del suelo de la cancha (texturizado con madera)
    court_material = AdvancedMaterial(
        color=(1.0, 1.0, 1.0),
        ka=0.2, kd=0.7, ks=0.1,
        shininess=16,
        diffuse_texture=wood_tex
    )
    
    # Suelo de la cancha: usaremos un Box del tamaño de la cancha para que no se salga del marco
    floor_y = -1.0  # altura de superficie del piso
    
    # === CANASTAS ===
    
    # Material para los postes (metal gris)
    pole_material = MaterialPresets.create_metal(
        color=(0.6, 0.6, 0.65),
        roughness=0.3
    )
    
    # Material para los aros (metal naranja/rojo)
    rim_material = MaterialPresets.create_metal(
        color=(0.9, 0.4, 0.1),
        roughness=0.1
    )
    
    # Material para los tableros (vidrio)
    backboard_material = MaterialPresets.create_glass(color=(0.9, 0.95, 1.0), ior=1.5)
    
    # === PROPORCIONES REALES APROXIMADAS ===
    # Longitud total: 28.65 unidades (eje X) => límites -14.325 a 14.325
    # Ancho total: 15.24 unidades (eje Z) => límites -7.62 a 7.62 (centrado)
    court_x_min, court_x_max = -14.325, 14.325
    court_z_min, court_z_max = -7.62, 7.62
    # Altura aro: 3 unidades sobre el piso => rim_y = floor_y + 3
    rim_y = floor_y + 3.0  # = 2.0 con floor_y = -1
    # Distancia rim-center a línea de fondo: 1.575 unidades
    rim_offset = 1.575
    rim_left_x = court_x_min + rim_offset   # -14 + 1.575 = -12.425
    rim_right_x = court_x_max - rim_offset  # 14 - 1.575 = 12.425
    rim_z = 0.0
    # Crear piso limitado a las dimensiones de la cancha (delimitación)
    floor_thickness = 0.02
    floor_center_y = floor_y - floor_thickness/2.0  # para que la cara superior quede en y = floor_y
    floor_width_x = (court_x_max - court_x_min)
    floor_depth_z = (court_z_max - court_z_min)
    court_floor_box = Box(
        center=((court_x_min + court_x_max)/2.0, floor_center_y, (court_z_min + court_z_max)/2.0),
        size=(floor_width_x, floor_thickness, floor_depth_z),
        material=court_material
    )
    # Indicar al Box que repita UVs solo si la textura es procedimental (para ImageTexture ya se usa tile_u/v)
    try:
        # Rotación de la veta de la madera (si se quiere alargar en X o Z)
        court_floor_box.uv_rotation_deg = float(FLOOR_UV_ROTATION_DEG)
        if isinstance(wood_tex, ProceduralTexture):
            court_floor_box.uv_tiles = (float(FLOOR_TILE_U), float(FLOOR_TILE_V))
    except Exception:
        pass
    renderer.scene.append(court_floor_box)
    # Backboard: 1.80 ancho (Z), 1.05 alto, 0.08 espesor (X)
    # Dimensiones reales del tablero: 1.80 m de ancho (eje Z), 1.05 m de alto (eje Y)
    BACKBOARD_THICKNESS_X = 0.08
    BACKBOARD_HEIGHT_Y = 1.05
    BACKBOARD_WIDTH_Z = 1.8
    backboard_size = (BACKBOARD_THICKNESS_X, BACKBOARD_HEIGHT_Y, BACKBOARD_WIDTH_Z)
    backboard_height_center = floor_y + 3.425  # rim + 0.425 aprox (centro del tablero)
    # Distancia desde plano del tablero al centro del aro: 0.15
    backboard_plane_left = rim_left_x - 0.15
    backboard_plane_right = rim_right_x + 0.15
    backboard_center_left_x = backboard_plane_left - backboard_size[0]/2.0
    backboard_center_right_x = backboard_plane_right + backboard_size[0]/2.0

    # Postes: detrás de la línea final (fuera de la cancha)
    post_overhang = 1.0  # distancia del poste a la línea final
    post_left_x = court_x_min - post_overhang  # -15
    post_right_x = court_x_max + post_overhang # 15
    post_height = 3.5
    post_radius = 0.12

    # Poste izquierdo
    pole1 = Cylinder(
        center=(post_left_x, floor_y + post_height/2.0, rim_z),
        radius=post_radius,
        height=post_height,
        material=pole_material
    )
    renderer.scene.append(pole1)
    # Poste derecho
    pole2 = Cylinder(
        center=(post_right_x, floor_y + post_height/2.0, rim_z),
        radius=post_radius,
        height=post_height,
        material=pole_material
    )
    renderer.scene.append(pole2)

    # Tableros
    backboard1 = Box(
        center=(backboard_center_left_x, backboard_height_center, rim_z),
        size=backboard_size,
        material=backboard_material
    )
    renderer.scene.append(backboard1)
    backboard2 = Box(
        center=(backboard_center_right_x, backboard_height_center, rim_z),
        size=backboard_size,
        material=backboard_material
    )
    renderer.scene.append(backboard2)

    # === MARCOS DE LOS TABLEROS ===
    
    # Material para los marcos (rojo)
    frame_material = AdvancedMaterial(
        color=(0.8, 0.1, 0.1),  # Rojo
        ka=0.2, kd=0.8, ks=0.2,
        shininess=32
    )
    
    frame_thickness = 0.04  # Grosor de los marcos
    frame_depth = 0.01     # Profundidad
    
    # Ajustar posición de marcos hacia el centro de la cancha para que queden sobre la superficie del tablero
    left_frame_x_offset = backboard_center_left_x + BACKBOARD_THICKNESS_X/2.0 + frame_depth
    right_frame_x_offset = backboard_center_right_x - BACKBOARD_THICKNESS_X/2.0 - frame_depth
    
    # MARCO EXTERIOR (MARGEN DEL TABLERO) - usando las dimensiones completas del tablero
    outer_frame_width = BACKBOARD_WIDTH_Z    # 1.8
    outer_frame_height = BACKBOARD_HEIGHT_Y  # 1.05
    
    # Marco exterior izquierdo - 4 lados
    # Superior
    left_outer_frame_top = Box(
        center=(left_frame_x_offset, backboard_height_center + outer_frame_height/2.0, rim_z),
        size=(frame_depth*2, frame_thickness, outer_frame_width),
        material=frame_material
    )
    renderer.scene.append(left_outer_frame_top)
    # Inferior  
    left_outer_frame_bottom = Box(
        center=(left_frame_x_offset, backboard_height_center - outer_frame_height/2.0, rim_z),
        size=(frame_depth*2, frame_thickness, outer_frame_width),
        material=frame_material
    )
    renderer.scene.append(left_outer_frame_bottom)
    # Lateral superior
    left_outer_frame_top_side = Box(
        center=(left_frame_x_offset, backboard_height_center, rim_z + outer_frame_width/2.0),
        size=(frame_depth*2, outer_frame_height, frame_thickness),
        material=frame_material
    )
    renderer.scene.append(left_outer_frame_top_side)
    # Lateral inferior
    left_outer_frame_bottom_side = Box(
        center=(left_frame_x_offset, backboard_height_center, rim_z - outer_frame_width/2.0),
        size=(frame_depth*2, outer_frame_height, frame_thickness),
        material=frame_material
    )
    renderer.scene.append(left_outer_frame_bottom_side)

    # Marco exterior derecho - 4 lados
    # Superior
    right_outer_frame_top = Box(
        center=(right_frame_x_offset, backboard_height_center + outer_frame_height/2.0, rim_z),
        size=(frame_depth*2, frame_thickness, outer_frame_width),
        material=frame_material
    )
    renderer.scene.append(right_outer_frame_top)
    # Inferior
    right_outer_frame_bottom = Box(
        center=(right_frame_x_offset, backboard_height_center - outer_frame_height/2.0, rim_z),
        size=(frame_depth*2, frame_thickness, outer_frame_width),
        material=frame_material
    )
    renderer.scene.append(right_outer_frame_bottom)
    # Lateral superior
    right_outer_frame_top_side = Box(
        center=(right_frame_x_offset, backboard_height_center, rim_z + outer_frame_width/2.0),
        size=(frame_depth*2, outer_frame_height, frame_thickness),
        material=frame_material
    )
    renderer.scene.append(right_outer_frame_top_side)
    # Lateral inferior  
    right_outer_frame_bottom_side = Box(
        center=(right_frame_x_offset, backboard_height_center, rim_z - outer_frame_width/2.0),
        size=(frame_depth*2, outer_frame_height, frame_thickness),
        material=frame_material
    )
    renderer.scene.append(right_outer_frame_bottom_side)

    # MARCO INTERIOR PEQUEÑO (0.45 x 0.59) - cerca del aro
    inner_frame_width = 0.59   # ancho (Z)
    inner_frame_height = 0.45  # alto (Y)
    
    # Posicionar el marco interior para que su borde inferior quede a la altura del aro
    inner_frame_y_center = rim_y + inner_frame_height/2.0  # Centro del marco = aro + mitad de la altura
    
    # Marco interior izquierdo - 4 lados
    # Superior
    left_inner_frame_top = Box(
        center=(left_frame_x_offset, inner_frame_y_center + inner_frame_height/2.0, rim_z),
        size=(frame_depth*2, frame_thickness, inner_frame_width),
        material=frame_material
    )
    renderer.scene.append(left_inner_frame_top)
    # Inferior
    left_inner_frame_bottom = Box(
        center=(left_frame_x_offset, inner_frame_y_center - inner_frame_height/2.0, rim_z),
        size=(frame_depth*2, frame_thickness, inner_frame_width),
        material=frame_material
    )
    renderer.scene.append(left_inner_frame_bottom)
    # Lateral superior
    left_inner_frame_top_side = Box(
        center=(left_frame_x_offset, inner_frame_y_center, rim_z + inner_frame_width/2.0),
        size=(frame_depth*2, inner_frame_height, frame_thickness),
        material=frame_material
    )
    renderer.scene.append(left_inner_frame_top_side)
    # Lateral inferior
    left_inner_frame_bottom_side = Box(
        center=(left_frame_x_offset, inner_frame_y_center, rim_z - inner_frame_width/2.0),
        size=(frame_depth*2, inner_frame_height, frame_thickness),
        material=frame_material
    )
    renderer.scene.append(left_inner_frame_bottom_side)

    # Marco interior derecho - 4 lados  
    # Superior
    right_inner_frame_top = Box(
        center=(right_frame_x_offset, inner_frame_y_center + inner_frame_height/2.0, rim_z),
        size=(frame_depth*2, frame_thickness, inner_frame_width),
        material=frame_material
    )
    renderer.scene.append(right_inner_frame_top)
    # Inferior
    right_inner_frame_bottom = Box(
        center=(right_frame_x_offset, inner_frame_y_center - inner_frame_height/2.0, rim_z),
        size=(frame_depth*2, frame_thickness, inner_frame_width),
        material=frame_material
    )
    renderer.scene.append(right_inner_frame_bottom)
    # Lateral superior
    right_inner_frame_top_side = Box(
        center=(right_frame_x_offset, inner_frame_y_center, rim_z + inner_frame_width/2.0),
        size=(frame_depth*2, inner_frame_height, frame_thickness),
        material=frame_material
    )
    renderer.scene.append(right_inner_frame_top_side)
    # Lateral inferior
    right_inner_frame_bottom_side = Box(
        center=(right_frame_x_offset, inner_frame_y_center, rim_z - inner_frame_width/2.0),
        size=(frame_depth*2, inner_frame_height, frame_thickness),
        material=frame_material
    )
    renderer.scene.append(right_inner_frame_bottom_side)

    # Aros (Torus) - diámetro 0.46 => radio mayor 0.23
    rim_diameter = 0.46
    rim_radius_major = rim_diameter / 2.0  # = 0.23
    rim_radius_minor = 0.018  # grosor del aro
    # Mover aros hacia el centro de la cancha para que no se incruste en el tablero
    rim_offset_from_backboard = 0.15  # Distancia del aro al tablero
    rim_left_x_adjusted = rim_left_x + rim_offset_from_backboard
    rim_right_x_adjusted = rim_right_x - rim_offset_from_backboard
    
    rim1 = Torus(
        center=(rim_left_x_adjusted, rim_y, rim_z),
        major_radius=rim_radius_major,
        minor_radius=rim_radius_minor,
        material=rim_material,
        rotation_euler=(0.0, 0.0, 0.0)
    )
    renderer.scene.append(rim1)
    rim2 = Torus(
        center=(rim_right_x_adjusted, rim_y, rim_z),
        major_radius=rim_radius_major,
        minor_radius=rim_radius_minor,
        material=rim_material,
        rotation_euler=(0.0, 0.0, 0.0)
    )
    renderer.scene.append(rim2)

    # Brazos (soporte horizontal) desde poste hasta tablero (eje X)
    arm_material = MaterialPresets.create_metal((0.65, 0.65, 0.7), roughness=0.25)
    arm_radius = 0.07
    # Altura de anclaje ~ medio del tablero
    arm_y = backboard_height_center
    arm_left_length = abs(backboard_center_left_x - post_left_x)
    arm_right_length = abs(post_right_x - backboard_center_right_x)
    arm_left_center_x = (backboard_center_left_x + post_left_x)/2.0
    arm_right_center_x = (backboard_center_right_x + post_right_x)/2.0
    arm1 = AxisCylinder(
        center=(arm_left_center_x, arm_y, rim_z),
        radius=arm_radius,
        height=arm_left_length,
        axis='x',
        material=arm_material
    )
    renderer.scene.append(arm1)
    arm2 = AxisCylinder(
        center=(arm_right_center_x, arm_y, rim_z),
        radius=arm_radius,
        height=arm_right_length,
        axis='x',
        material=arm_material
    )
    renderer.scene.append(arm2)
    
    # === BASKETBALL ===
    
    # Material de la pelota (naranja rugoso)
    ball_material = AdvancedMaterial(
        color=(0.9, 0.5, 0.1),  # Naranja basketball
        ka=0.2, kd=0.8, ks=0.2,
        shininess=32,
        roughness=0.6
    )
    
    # Pelota de basketball (diámetro reglamentario ~0.24 => radio 0.12)
    BALL_DIAMETER = 0.24
    BALL_RADIUS = BALL_DIAMETER / 2.0
    basketball = Sphere(
        position=(-8.00, floor_y + BALL_RADIUS + 3, -3.5),  # apoyada exactamente sobre el piso
        radius=BALL_RADIUS,
        material=ball_material
    )
    renderer.scene.append(basketball)
    
    # === MODELO OBJ JUNTO A LA PELOTA (STEVE) ===
    try:
        from obj_loader import OBJLoader  # ensure availability
        # Colocar el personaje (Steve) a la derecha de la pelota, mirando hacia el centro
        model_path = Path("models/steve/source/Steve.obj")
        if model_path.exists():
            scale = 2.0
            char_x = -6.75
            char_z = -4.5
            # Guardar índice inicial para aplicar textura a los nuevos meshes
            start_idx = len(renderer.scene)
            renderer.load_obj_model(
                str(model_path),
                scale=scale,
                position=(char_x, 0.0, char_z),
                rotation=(0.0, -40.0, 0.0),
                material=None,
                align_min_y_to=floor_y
            )
            # Forzar textura de Steve si por alguna razón el MTL no la aplicó
            try:
                from texture import ImageTexture
                steve_tex_path = Path("models/steve/textures/steve.png")
                if steve_tex_path.exists():
                    for obj in renderer.scene[start_idx:]:
                        mat = getattr(obj, 'material', None)
                        if mat is not None and hasattr(mat, 'get_diffuse_color'):
                            mat.diffuse_texture = ImageTexture(str(steve_tex_path))
            except Exception:
                pass
            print("Placed Steve next to the basketball")
        else:
            print(f"Steve OBJ not found at {model_path}")
    except Exception as e:
        print(f"Could not place Steve model: {e}")
    
    # === ELEMENTOS ADICIONALES ===
    
    # Líneas del centro de la cancha (cilindros delgados)
    line_material = AdvancedMaterial(
        color=(0.9, 0.9, 0.9),  # Blanco
        ka=0.3, kd=0.7, ks=0.0,
        shininess=1
    )
    
    # === CÍRCULO CENTRAL Y LÍNEA DE MEDIO CAMPO ===
    
    # Círculo central perfecto usando Disk - diámetro 3.66 => radio 1.83
    center_circle_radius = 3.66 / 2.0  # = 1.83
    
    # Círculo central perfecto como Disk (círculo plano)
    from figure import Ring
    circle_line_width = 0.08  # grosor del trazo
    center_circle = Ring(
        center=(0, floor_y + 0.005, 0),
        normal=(0, 1, 0),
        outer_radius=center_circle_radius,
        inner_radius=max(0.0, center_circle_radius - circle_line_width),
        material=line_material
    )
    renderer.scene.append(center_circle)
    
    # Línea central TRANSVERSAL que divide la cancha (de lado a lado en Z, atraviesa X=0)
    # Desde court_z_min hasta court_z_max en x=0
    center_line_length = court_z_max - court_z_min  # 15
    line_thickness = 0.08  # Grosor de las líneas
    center_line = Box(
        center=(0, floor_y + 0.005, (court_z_min + court_z_max)/2.0),
        size=(line_thickness, 0.01, center_line_length),
        material=line_material
    )
    renderer.scene.append(center_line)
    # === MARCO ÚNICO QUE DELIMITA TODA LA CANCHA ===
    # Creamos un rectángulo (solo borde) alrededor del área de juego.
    # Se seleccionan límites que engloben postes y aros.
    boundary_material = AdvancedMaterial(
        color=(0.95, 0.95, 0.95),
        ka=0.25, kd=0.7, ks=0.05,
        shininess=8
    )
    line_thickness = 0.08
    y_frame = floor_y + 0.01  # evitar z-fighting

    # Límites reales de la cancha
    x_min = court_x_min
    x_max = court_x_max
    z_min = court_z_min
    z_max = court_z_max

    # Segmentos (4 lados)
    top_side = Box(
        center=((x_min + x_max)/2.0, y_frame, z_min),
        size=(x_max - x_min, line_thickness, line_thickness),
        material=boundary_material
    )
    bottom_side = Box(
        center=((x_min + x_max)/2.0, y_frame, z_max),
        size=(x_max - x_min, line_thickness, line_thickness),
        material=boundary_material
    )
    left_side = Box(
        center=(x_min, y_frame, (z_min + z_max)/2.0),
        size=(line_thickness, line_thickness, z_max - z_min),
        material=boundary_material
    )
    right_side = Box(
        center=(x_max, y_frame, (z_min + z_max)/2.0),
        size=(line_thickness, line_thickness, z_max - z_min),
        material=boundary_material
    )
    renderer.scene.extend([top_side, bottom_side, left_side, right_side])

    # Marco exterior adicional (amarillo) - continuación del suelo, pegado a la cancha
    try:
        from config import YELLOW_FLOOR_FRAME_ENABLED, YELLOW_FLOOR_FRAME_WIDTH, YELLOW_FLOOR_FRAME_COLOR
    except Exception:
        YELLOW_FLOOR_FRAME_ENABLED, YELLOW_FLOOR_FRAME_WIDTH, YELLOW_FLOOR_FRAME_COLOR = True, 1.5, (1.0, 0.9, 0.1)
    if YELLOW_FLOOR_FRAME_ENABLED:
        frame_w = float(YELLOW_FLOOR_FRAME_WIDTH)
        yellow_material = AdvancedMaterial(
            color=tuple(YELLOW_FLOOR_FRAME_COLOR),
            ka=0.2, kd=0.8, ks=0.1,
            shininess=8
        )
        # Usar el mismo espesor y centro en Y que el piso para que sea una extensión real
        y_center_band = floor_center_y
        y_size_band = floor_thickness
        # Tiras amarillas (4 lados), pegadas al borde de la cancha
        y_top = Box(
            center=((x_min + x_max)/2.0, y_center_band, z_min - frame_w/2.0),
            size=((x_max - x_min), y_size_band, frame_w),
            material=yellow_material
        )
        y_bottom = Box(
            center=((x_min + x_max)/2.0, y_center_band, z_max + frame_w/2.0),
            size=((x_max - x_min), y_size_band, frame_w),
            material=yellow_material
        )
        y_left = Box(
            center=(x_min - frame_w/2.0, y_center_band, (z_min + z_max)/2.0),
            size=(frame_w, y_size_band, (z_max - z_min)),
            material=yellow_material
        )
        y_right = Box(
            center=(x_max + frame_w/2.0, y_center_band, (z_min + z_max)/2.0),
            size=(frame_w, y_size_band, (z_max - z_min)),
            material=yellow_material
        )
        renderer.scene.extend([y_top, y_bottom, y_left, y_right])

    # === RECTÁNGULOS DE LA ZONA (PAINT) BAJO CADA CANASTA ===
    # Dimensiones solicitadas: 5.8 (profundidad en X) x 3.2 (ancho en Z)
    paint_depth = 5.8
    paint_width = 4.9  # actualizado (ancho en Z)
    paint_line_thickness = 0.08
    paint_y = floor_y + 0.006  # apenas encima del piso
    paint_material = line_material

    # Rectángulo bajo canasta izquierda (desde línea final hacia centro)
    left_rect_x_start = court_x_min
    left_rect_x_end = left_rect_x_start + paint_depth
    left_rect_center_x = (left_rect_x_start + left_rect_x_end) / 2.0
    rect_z_min = -paint_width / 2.0
    rect_z_max = paint_width / 2.0

    left_rect_top = Box(
        center=(left_rect_center_x, paint_y, rect_z_min),
        size=(paint_depth, 0.01, paint_line_thickness),
        material=paint_material
    )
    left_rect_bottom = Box(
        center=(left_rect_center_x, paint_y, rect_z_max),
        size=(paint_depth, 0.01, paint_line_thickness),
        material=paint_material
    )
    left_rect_left = Box(
        center=(left_rect_x_start, paint_y, 0),
        size=(paint_line_thickness, 0.01, paint_width),
        material=paint_material
    )
    left_rect_right = Box(
        center=(left_rect_x_end, paint_y, 0),
        size=(paint_line_thickness, 0.01, paint_width),
        material=paint_material
    )
    renderer.scene.extend([left_rect_top, left_rect_bottom, left_rect_left, left_rect_right])

    # Rectángulo bajo canasta derecha (desde línea final derecha hacia el centro)
    right_rect_x_end = court_x_max
    right_rect_x_start = right_rect_x_end - paint_depth
    right_rect_center_x = (right_rect_x_start + right_rect_x_end) / 2.0

    right_rect_top = Box(
        center=(right_rect_center_x, paint_y, rect_z_min),
        size=(paint_depth, 0.01, paint_line_thickness),
        material=paint_material
    )
    right_rect_bottom = Box(
        center=(right_rect_center_x, paint_y, rect_z_max),
        size=(paint_depth, 0.01, paint_line_thickness),
        material=paint_material
    )
    right_rect_left = Box(
        center=(right_rect_x_start, paint_y, 0),
        size=(paint_line_thickness, 0.01, paint_width),
        material=paint_material
    )
    right_rect_right = Box(
        center=(right_rect_x_end, paint_y, 0),
        size=(paint_line_thickness, 0.01, paint_width),
        material=paint_material
    )
    renderer.scene.extend([right_rect_top, right_rect_bottom, right_rect_left, right_rect_right])

    # Anillos planos (contorno) en la mitad de la línea corta interior de cada rectángulo de la zona
    # Diámetro igual al del círculo central (3.66) => radio 1.83
    from figure import Ring
    paint_ring_radius = center_circle_radius  # 1.83
    # Grosor del trazo (si existe circle_line_width úsalo; si no, define uno)
    try:
        ring_line_width = circle_line_width
    except NameError:
        ring_line_width = 0.08

    # Centro del anillo izquierdo: en el borde interior (x = left_rect_x_end), z = 0
    left_ring = Ring(
        center=(left_rect_x_end, floor_y + 0.005, 0.0),
        normal=(0, 1, 0),
        outer_radius=paint_ring_radius,
        inner_radius=max(0.0, paint_ring_radius - ring_line_width),
        material=line_material
    )
    renderer.scene.append(left_ring)

    # Centro del anillo derecho: borde interior (x = right_rect_x_start)
    right_ring = Ring(
        center=(right_rect_x_start, floor_y + 0.005, 0.0),
        normal=(0, 1, 0),
        outer_radius=paint_ring_radius,
        inner_radius=max(0.0, paint_ring_radius - ring_line_width),
        material=line_material
    )
    renderer.scene.append(right_ring)

    # === LÍNEA DE TRES PUNTOS (SEMICÍRCULOS) ===
    # Radio reglamentario aproximado 6.6 unidades desde el centro del aro.
    # Usaremos ArcRing para un semicírculo frontal (180°) orientado hacia el centro de la cancha.
    from figure import ArcRing
    three_radius = 6.6
    three_line_width = 0.08
    # Para el aro izquierdo (en x = rim_left_x_adjusted) el semicírculo debe abrirse hacia +X (centro de la cancha).
    # Definimos start_angle = -90° y end_angle = +90° en radianes (eje +X = 0 rad, +Z = +90°)
    deg = np.pi / 180.0
    left_three_arc = ArcRing(
        center=(rim_left_x_adjusted, floor_y + 0.005, rim_z),
        normal=(0, 1, 0),
        outer_radius=three_radius,
        inner_radius=max(0.0, three_radius - three_line_width),
        start_angle=-90*deg,
        end_angle=90*deg,
        material=line_material
    )
    renderer.scene.append(left_three_arc)
    # Para el aro derecho (x = rim_right_x_adjusted) el semicírculo se abre hacia -X, equivalente a un arco de 90°..270°
    right_three_arc = ArcRing(
        center=(rim_right_x_adjusted, floor_y + 0.005, rim_z),
        normal=(0, 1, 0),
        outer_radius=three_radius,
        inner_radius=max(0.0, three_radius - three_line_width),
        start_angle=90*deg,
        end_angle=270*deg,
        material=line_material
    )
    renderer.scene.append(right_three_arc)

    # === LÍNEAS RECTAS DE TRIPLE (DESDE EXTREMOS DE SEMICÍRCULOS AL MARCO) ===
    # Calcular puntos donde terminan los semicírculos y extender hasta las líneas de fondo (lado corto)
    
    # Para el semicírculo izquierdo: extremos en ángulos -90° y +90° (en Z)
    left_arc_end_top = (rim_left_x_adjusted, floor_y + 0.005, rim_z + three_radius)    # +90°
    left_arc_end_bottom = (rim_left_x_adjusted, floor_y + 0.005, rim_z - three_radius) # -90°
    
    # Para el semicírculo derecho: extremos en ángulos +90° y +270° (equivalente a -90°)
    right_arc_end_top = (rim_right_x_adjusted, floor_y + 0.005, rim_z + three_radius)    # +90°
    right_arc_end_bottom = (rim_right_x_adjusted, floor_y + 0.005, rim_z - three_radius) # +270°/-90°
    
    # Líneas rectas desde extremos izquierdos hasta la línea de fondo izquierda
    left_line_top_length = abs(left_arc_end_top[0] - court_x_min)
    left_line_top_center_x = (left_arc_end_top[0] + court_x_min) / 2.0
    left_line_top = Box(
        center=(left_line_top_center_x, floor_y + 0.005, left_arc_end_top[2]),
        size=(left_line_top_length, 0.01, three_line_width),
        material=line_material
    )
    renderer.scene.append(left_line_top)
    
    left_line_bottom_length = abs(left_arc_end_bottom[0] - court_x_min)
    left_line_bottom_center_x = (left_arc_end_bottom[0] + court_x_min) / 2.0
    left_line_bottom = Box(
        center=(left_line_bottom_center_x, floor_y + 0.005, left_arc_end_bottom[2]),
        size=(left_line_bottom_length, 0.01, three_line_width),
        material=line_material
    )
    renderer.scene.append(left_line_bottom)
    
    # Líneas rectas desde extremos derechos hasta la línea de fondo derecha
    right_line_top_length = abs(court_x_max - right_arc_end_top[0])
    right_line_top_center_x = (right_arc_end_top[0] + court_x_max) / 2.0
    right_line_top = Box(
        center=(right_line_top_center_x, floor_y + 0.005, right_arc_end_top[2]),
        size=(right_line_top_length, 0.01, three_line_width),
        material=line_material
    )
    renderer.scene.append(right_line_top)
    
    right_line_bottom_length = abs(court_x_max - right_arc_end_bottom[0])
    right_line_bottom_center_x = (right_arc_end_bottom[0] + court_x_max) / 2.0
    right_line_bottom = Box(
        center=(right_line_bottom_center_x, floor_y + 0.005, right_arc_end_bottom[2]),
        size=(right_line_bottom_length, 0.01, three_line_width),
        material=line_material
    )
    renderer.scene.append(right_line_bottom)
    
    # === ILUMINACIÓN DE GIMNASIO ===
    
    # Luces principales del gimnasio (como reflectores)
    gym_lights = [
        # Luz principal central
        PointLight(
            position=(0, 4, 2),
            color=(1.0, 1.0, 0.95),
            intensity=3.0,
            attenuation_linear=0.1,
            attenuation_quadratic=0.01
        ),
        
        # Luces laterales
        PointLight(
            position=(-3, 3, 1),
            color=(1.0, 0.98, 0.9),
            intensity=2.0,
            attenuation_linear=0.15,
            attenuation_quadratic=0.02
        ),
        
        PointLight(
            position=(3, 3, 1),
            color=(1.0, 0.98, 0.9),
            intensity=2.0,
            attenuation_linear=0.15,
            attenuation_quadratic=0.02
        )
    ]
    
    for light in gym_lights:
        renderer.lights.append(light)

    # === LUCES DIRECCIONALES DE ESTADIO ===
    # Dos DirectionalLight arriba de los lados largos, apuntando hacia el centro
    stadium_height = 8.0
    stadium_intensity = 2.5
    stadium_color = (1.0, 0.98, 0.95)
    # Lado izquierdo
    left_dir_pos = (x_min, floor_y + stadium_height, 0.0)
    left_dir_vec = np.array([1.0, -1.4, 0.0])  # hacia el centro, ligeramente inclinado hacia abajo
    left_dir_vec = left_dir_vec / np.linalg.norm(left_dir_vec)
    left_dir = DirectionalLight(
        direction=left_dir_vec,
        color=stadium_color,
        intensity=stadium_intensity
    )
    renderer.lights.append(left_dir)
    # Lado derecho
    right_dir_pos = (x_max, floor_y + stadium_height, 0.0)
    right_dir_vec = np.array([-1.0, -1.4, 0.0])  # hacia el centro, ligeramente inclinado hacia abajo
    right_dir_vec = right_dir_vec / np.linalg.norm(right_dir_vec)
    right_dir = DirectionalLight(
        direction=right_dir_vec,
        color=stadium_color,
        intensity=stadium_intensity
    )
    renderer.lights.append(right_dir)
    
    # Añadir un spotlight en la posición planificada de Steve, apuntando al centro de la cancha
    steve_x, steve_z = -6.75, -4.5
    steve_spot_height = 3.0  # altura sobre el suelo
    steve_spot_pos = (steve_x, floor_y + steve_spot_height, steve_z)
    # Spotlight completamente vertical sobre Steve (apuntando hacia abajo)
    steve_dir = np.array([0.0, -1.0, 0.0])
    steve_spot = SpotLight(
        position=steve_spot_pos,
        direction=steve_dir,
        # Color celeste para mayor visibilidad del spotlight
        color=(0.6, 0.85, 1.0),
        intensity=5.0,
        inner_angle=15,
        outer_angle=30
    )
    renderer.lights.append(steve_spot)
    
    # Añadir cuatro point lights en las esquinas de la cancha
    corner_height = 3.5
    corner_intensity = 1.5
    corners = [
        (x_min, z_min),
        (x_min, z_max),
        (x_max, z_min),
        (x_max, z_max)
    ]
    for cx, cz in corners:
        renderer.lights.append(PointLight(
            position=(cx, floor_y + corner_height, cz),
            color=(1.0, 0.98, 0.9),
            intensity=corner_intensity,
            attenuation_linear=0.12,
            attenuation_quadratic=0.02
        ))
    
    # La cámara se configura desde config.py - no sobrescribir aquí
    
    print("Basketball court scene created successfully!")
    print(f"Scene contains {len(renderer.scene)} objects and {len(renderer.lights)} lights")
    print("Court features:")
    print("- Wooden court floor with lines")  
    print("- 2 Basketball hoops with backboards")
    print("- Basketball in center court")
    print("- Gymnasium lighting setup")

def build_scene_from_preset(renderer, preset_name):
    """Construye escena según el preset especificado"""
    
    if preset_name == "materials":
        create_materials_showcase_scene(renderer)
    elif preset_name == "geometry":
        create_geometry_showcase_scene(renderer)
    elif preset_name == "complex":
        create_complex_scene_with_obj(renderer)
    elif preset_name == "artistic":
        create_artistic_scene(renderer)
    elif preset_name == "basketball":
        create_basketball_court_scene(renderer)
    else:
        # Escena por defecto que combina todo
        print("Creating comprehensive demo scene...")
        create_complex_scene_with_obj(renderer)
    
    # Cargar environment map adicional si está disponible (se omite para basketball porque es interior)
    if preset_name != "basketball":
        env_maps = [
            "Enviroment/pretoria_gardens_4k.hdr",
            "Enviroment/noon.hdr", 
            "Enviroment/rogland_clear_night_1k.hdr"
        ]
        
        for env_map in env_maps:
            try:
                if Path(env_map).exists():
                    print(f"Loading environment map: {env_map}")
                    renderer.load_environment(env_map)
                    break
            except Exception as e:
                print(f"Could not load environment map {env_map}: {e}")
    else:
        # Ya se puede haber cargado un environment global antes; aquí solo omites uno adicional por preset
        print("Skipping additional environment map for basketball preset (indoor gym)")
    
    print("Scene construction completed!")
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
    from texture import ProceduralTexture
    from figure import Sphere, Plane, Cylinder, Cube
    from advanced_shapes import Capsule
    from lighting import PointLight, DirectionalLight
    
    renderer.scene.clear()
    renderer.lights.clear()
    
    print("Creating basketball court scene...")
    
    # === SUELO DE LA CANCHA ===
    
    # Crear textura procedimental para líneas de la cancha
    court_texture = ProceduralTexture("court_lines")
    
    # Material del suelo de la cancha (color madera clara)
    court_material = AdvancedMaterial(
        color=(0.8, 0.6, 0.3),  # Color madera clara
        ka=0.2, kd=0.7, ks=0.1,
        shininess=16,
        diffuse_texture=court_texture
    )
    
    # Suelo de la cancha (más grande que las escenas anteriores)
    court_floor = Plane(
        point=(0, -1, 0),
        normal=(0, 1, 0),
        material=court_material
    )
    renderer.scene.append(court_floor)
    
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
    
    # Material para los tableros (blanco)
    backboard_material = AdvancedMaterial(
        color=(0.95, 0.95, 0.95),
        ka=0.2, kd=0.7, ks=0.3,
        shininess=64
    )
    
    # === CANASTA 1 (Lado izquierdo) ===
    
    # Poste de la canasta 1
    pole1 = Cylinder(
        center=(-4, 1, -2),
        radius=0.1,
        height=2.5,
        material=pole_material
    )
    renderer.scene.append(pole1)
    
    # Tablero de la canasta 1
    backboard1 = Cube(
        center=(-3.2, 2, -2),
        size=0.8,  # Tamaño del tablero
        material=backboard_material
    )
    renderer.scene.append(backboard1)
    
    # Aro de la canasta 1 (simplificado como cilindro delgado)
    rim1 = Cylinder(
        center=(-3.0, 1.8, -2),
        radius=0.25,
        height=0.05,
        material=rim_material
    )
    renderer.scene.append(rim1)
    
    # === CANASTA 2 (Lado derecho) ===
    
    # Poste de la canasta 2
    pole2 = Cylinder(
        center=(4, 1, -2),
        radius=0.1,
        height=2.5,
        material=pole_material
    )
    renderer.scene.append(pole2)
    
    # Tablero de la canasta 2
    backboard2 = Cube(
        center=(3.2, 2, -2),
        size=0.8,
        material=backboard_material
    )
    renderer.scene.append(backboard2)
    
    # Aro de la canasta 2
    rim2 = Cylinder(
        center=(3.0, 1.8, -2),
        radius=0.25,
        height=0.05,
        material=rim_material
    )
    renderer.scene.append(rim2)
    
    # === BASKETBALL ===
    
    # Material de la pelota (naranja rugoso)
    ball_material = AdvancedMaterial(
        color=(0.9, 0.5, 0.1),  # Naranja basketball
        ka=0.2, kd=0.8, ks=0.2,
        shininess=32,
        roughness=0.6
    )
    
    # Pelota de basketball en el centro de la cancha
    basketball = Sphere(
        position=(0, -0.6, 0),
        radius=0.15,
        material=ball_material
    )
    renderer.scene.append(basketball)
    
    # === ELEMENTOS ADICIONALES ===
    
    # Líneas del centro de la cancha (cilindros delgados)
    line_material = AdvancedMaterial(
        color=(0.9, 0.9, 0.9),  # Blanco
        ka=0.3, kd=0.7, ks=0.0,
        shininess=1
    )
    
    # Círculo central (simplificado como cilindro plano)
    center_circle = Cylinder(
        center=(0, -0.98, 0),
        radius=1.0,
        height=0.02,
        material=line_material
    )
    renderer.scene.append(center_circle)
    
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
    
    # Cargar environment map si está disponible (no para basketball)
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
        print("Skipping environment map for basketball court (indoor gym lighting)")
    
    print("Scene construction completed!")
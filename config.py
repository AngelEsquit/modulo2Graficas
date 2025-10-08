"""
Configuración central del raytracer: resoluciones, environment maps,
escenas/modelos (placeholder), cámara, calidad de render y salida.

Edita este archivo para cambiar parámetros sin tocar la lógica.
"""
from __future__ import annotations
from pathlib import Path

# Rutas base
BASE_DIR: Path = Path(__file__).parent
ENV_DIR: Path = BASE_DIR / "Enviroment"
BMP_DIR: Path = BASE_DIR / "BMPs"

# Salida
OUTPUT_FILENAME: str = "output.bmp"
OUTPUT_PATH: Path = BASE_DIR / OUTPUT_FILENAME

# Ventana / resolución
WIDTH: int = 300
HEIGHT: int = 300
WINDOW_TITLE: str = "RayTracer"

# Environment map
# Coloca aquí el nombre del archivo .hdr/.png/.jpg que exista bajo ENV_DIR
# Opciones actuales (en repo):
#  - "pretoria_gardens_4k.hdr"
#  - "noon.hdr"
#  - "rogland_clear_night_1k.hdr"
ENVIRONMENT_MAP: str = ""

# Cámara inicial
CAMERA_PRESET: str = "cancha" # "centro", "canasta", "cancha", "tablero"
if CAMERA_PRESET == "centro":
    CAMERA_POSITION: tuple[float, float, float] = (0.0, 3, 5.0)
    CAMERA_ROTATION: tuple[float, float, float] = (-35.0, 0.0, 0.0)  # pitch, yaw, roll en grados
elif CAMERA_PRESET == "canasta":
    CAMERA_POSITION: tuple[float, float, float] = (-13.0, 3, 5.0)
    CAMERA_ROTATION: tuple[float, float, float] = (-25.0, 0.0, 0.0)
elif CAMERA_PRESET == "cancha":
    CAMERA_POSITION: tuple[float, float, float] = (0.0, 20.0, 20.0)
    CAMERA_ROTATION: tuple[float, float, float] = (-45.0, 0.0, 0.0)
elif CAMERA_PRESET == "tablero":
    CAMERA_POSITION: tuple[float, float, float] = (10.0, 3.0, 0.0)
    CAMERA_ROTATION: tuple[float, float, float] = (0.0, -90.0, 0.0)

# Render progresivo
PIXELS_PER_FRAME: int = 4000  # mayor valor = converge más rápido, pero consume más CPU por frame
MAX_DEPTH: int | None = None  # si es int, y el Renderer lo soporta, forzar profundidad de rayos

# Luz ambiental global (si el Renderer decide leerla)
# Valor bajo recomendado para no sobreexponer
AMBIENT_LIGHT: tuple[float, float, float] | None = (0.65, 0.65, 0.65)

# Intensidad del environment map (multiplicador antes del tone-mapping)
ENV_INTENSITY: float | None = 0.6

# Escala global para intensidades de luces puntuales
LIGHT_INTENSITY_SCALE: float | None = 0.15

# Selección de escena (placeholder para futuras extensiones)
# NUEVAS ESCENAS IMPLEMENTADAS PARA EL PROYECTO
SCENE_PRESET: str = "basketball"  # Opciones disponibles:
# "materials"   - Demuestra 4 materiales diferentes con texturas (20 puntos)
# "geometry"    - Demuestra figuras geométricas avanzadas (20 puntos) 
# "complex"     - Escena compleja con >10 figuras + OBJ + iluminación (70+ puntos)
# "artistic"    - Escena artística para estética (20 puntos estéticos)
# "basketball"  - Cancha de basketball con suelo y canastas
# "default"     - Escena simple original
# "materials", "room", "cylinders", "cones", "tori" - Escenas originales

# Modelos OBJ a cargar (20 PUNTOS POR RENDERIZAR OBJ)
# Lista de modelos OBJ que se cargarán automáticamente
MODELS: list[dict] = [
    # Ejemplos - descomenta si tienes estos archivos OBJ:
    # {
    #     "path": BASE_DIR / "models" / "teapot.obj",
    #     "position": (0.0, 1.0, -8.0),
    #     "rotation": (0.0, 45.0, 0.0),  # pitch, yaw, roll (grados)
    #     "scale": (2.0, 2.0, 2.0),
    #     "material": {
    #         "color": (0.9, 0.7, 0.2), "ka": 0.1, "kd": 0.7, "ks": 0.3,
    #         "shininess": 64, "reflectivity": 0.3, "transparency": 0.0, "ior": 1.5
    #     }
    # },
    # {
    #     "path": BASE_DIR / "models" / "suzanne.obj",
    #     "position": (3.0, 0.0, -6.0),
    #     "rotation": (0.0, 0.0, 0.0),
    #     "scale": (1.5, 1.5, 1.5),
    #     "material": {
    #         "color": (0.8, 0.2, 0.2), "ka": 0.1, "kd": 0.8, "ks": 0.2,
    #         "shininess": 32, "reflectivity": 0.1, "transparency": 0.0, "ior": 1.0
    #     }
    # }
]

# === CONFIGURACIÓN PARA MAXIMIZAR PUNTOS DEL PROYECTO ===

# Configuración de texturas (OBLIGATORIO - al menos un material debe usar textura)
TEXTURE_DIR: Path = BASE_DIR / "textures"
USE_PROCEDURAL_TEXTURES: bool = True  # Usar texturas procedurales si no hay archivos de imagen

# Configuración de materiales avanzados (20 PUNTOS - máximo 4 materiales)
ENABLE_ADVANCED_MATERIALS: bool = True
ENABLE_EMISSION: bool = True          # Materiales emisivos
ENABLE_NORMAL_MAPPING: bool = True    # Mapas de normales para bump mapping
MAX_MATERIALS_FOR_POINTS: int = 4     # Máximo evaluado para puntos

# Configuración de iluminación avanzada (10 PUNTOS)
ENABLE_MULTIPLE_LIGHTS: bool = True      # Múltiples luces
ENABLE_SPOT_LIGHTS: bool = True          # Spot lights
ENABLE_DIRECTIONAL_LIGHTS: bool = True   # Luces direccionales  
ENABLE_POINT_LIGHTS: bool = True         # Luces puntuales
MAX_LIGHTS: int = 10                     # Límite de luces para performance

# Configuración de figuras geométricas (20 PUNTOS - máximo 4 figuras nuevas)
ENABLE_ADVANCED_SHAPES: bool = True      # Habilitar figuras avanzadas
MAX_SHAPES_FOR_POINTS: int = 4           # Máximo evaluado para puntos

# Environment Map (5 PUNTOS)
ENVIRONMENT_MAP: str = ""  # Cambiar si tienes otro archivo

# Complejidad de escena (30 PUNTOS)
TARGET_SCENE_COMPLEXITY: str = "high"   # "low" (<5), "medium" (5-10), "high" (>10)
MIN_FIGURES_FOR_MAX_POINTS: int = 10


def env_path() -> Path:
    """Ruta absoluta al environment map seleccionado."""
    return ENV_DIR / ENVIRONMENT_MAP


def ensure_dirs() -> None:
    """Crea carpetas de salida útiles si no existen."""
    try:
        BMP_DIR.mkdir(parents=True, exist_ok=True)
    except Exception:
        # Evita fallar si no se puede crear; se usará BASE_DIR
        pass

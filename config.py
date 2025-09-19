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
WIDTH: int = 1024
HEIGHT: int = 1024
WINDOW_TITLE: str = "Simple RayTracer - Esferas (Phong)"

# Environment map
# Coloca aquí el nombre del archivo .hdr/.png/.jpg que exista bajo ENV_DIR
# Opciones actuales (en repo):
#  - "pretoria_gardens_4k.hdr"
#  - "noon.hdr"
#  - "rogland_clear_night_1k.hdr"
ENVIRONMENT_MAP: str = ""

# Cámara inicial
CAMERA_POSITION: tuple[float, float, float] = (0.0, 0.0, 5.0)
CAMERA_ROTATION: tuple[float, float, float] = (0.0, 0.0, 0.0)  # pitch, yaw, roll en grados

# Render progresivo
PIXELS_PER_FRAME: int = 4000  # mayor valor = converge más rápido, pero consume más CPU por frame
MAX_DEPTH: int | None = None  # si es int, y el Renderer lo soporta, forzar profundidad de rayos

# Luz ambiental global (si el Renderer decide leerla)
# Valor bajo recomendado para no sobreexponer
AMBIENT_LIGHT: tuple[float, float, float] | None = (2.55, 2.55, 2.55)

# Intensidad del environment map (multiplicador antes del tone-mapping)
ENV_INTENSITY: float | None = 0.6

# Escala global para intensidades de luces puntuales
LIGHT_INTENSITY_SCALE: float | None = 0.05

# Selección de escena (placeholder para futuras extensiones)
# "materials" usa la escena de 6 esferas en gl.Renderer._build_materials_scene
# "default" usa la escena alternativa gl.Renderer._build_default_scene (si se cablea en el futuro)
SCENE_PRESET: str = "room"  # opciones: "materials", "default", "room"

# Modelos (placeholder): lista de rutas a modelos cuando exista soporte de carga
# Por ahora no hay loader de modelos en el repo; esto es referencia futura.
MODELS: list[dict] = [
    # Ejemplo (descomenta y ajusta si tienes un .obj):
    # {
    #     "path": BASE_DIR / "models" / "teapot.obj",
    #     "position": (0.0, 0.0, 0.0),
    #     "rotation": (0.0, 0.0, 0.0),  # pitch, yaw, roll (grados)
    #     "scale": (1.0, 1.0, 1.0),
    #     "material": {
    #         "color": (0.9, 0.7, 0.2), "ka": 0.1, "kd": 0.7, "ks": 0.3,
    #         "shininess": 32, "reflectivity": 0.2, "transparency": 0.0, "ior": 1.5
    #     }
    # }
]


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

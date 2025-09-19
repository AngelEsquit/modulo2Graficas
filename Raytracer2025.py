import pygame
from pygame.locals import *
from gl import Renderer
from BMP_Writer import GenerateBMP
from config import WIDTH, HEIGHT, WINDOW_TITLE, env_path, OUTPUT_PATH, CAMERA_POSITION, PIXELS_PER_FRAME, MAX_DEPTH, AMBIENT_LIGHT, SCENE_PRESET, MODELS, ENV_INTENSITY, LIGHT_INTENSITY_SCALE

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
pygame.display.set_caption(WINDOW_TITLE)
clock = pygame.time.Clock()

rend = Renderer(screen)
# Aplicar ajustes desde config
try:
    # Cámara inicial
    rend.camera.position = list(CAMERA_POSITION)
except Exception:
    pass

# Parámetros de render si están expuestos
if hasattr(rend, "_init_progressive_render") and PIXELS_PER_FRAME:
    try:
        rend._init_progressive_render(PIXELS_PER_FRAME)
    except Exception:
        pass
if hasattr(rend, "max_depth") and MAX_DEPTH is not None:
    try:
        rend.max_depth = int(MAX_DEPTH)
    except Exception:
        pass
if hasattr(rend, "ambientLight") and AMBIENT_LIGHT is not None:
    try:
        rend.ambientLight = AMBIENT_LIGHT
    except Exception:
        pass
if hasattr(rend, "env_intensity") and ENV_INTENSITY is not None:
    try:
        rend.env_intensity = float(ENV_INTENSITY)
    except Exception:
        pass
if hasattr(rend, "light_intensity_scale") and LIGHT_INTENSITY_SCALE is not None:
    try:
        rend.light_intensity_scale = float(LIGHT_INTENSITY_SCALE)
    except Exception:
        pass

# Environment map desde config
try:
    rend.load_environment(str(env_path()))
except Exception:
    pass

# Si hay modelos en config, construir escena desde ellos; de lo contrario usar preset
try:
    if MODELS:
        if hasattr(rend, 'build_scene_from_models'):
            rend.build_scene_from_models(MODELS)
    else:
        if SCENE_PRESET == "default" and hasattr(rend, "_build_default_scene"):
            rend._build_default_scene()
            rend.restart_render()
        elif SCENE_PRESET == "materials" and hasattr(rend, "_build_materials_scene"):
            rend._build_materials_scene()
            rend.restart_render()
        elif SCENE_PRESET == "room" and hasattr(rend, "_build_room_scene"):
            rend._build_room_scene()
except Exception:
    pass

isRunning = True
while isRunning:
    for event in pygame.event.get():
        if event.type == QUIT:
            isRunning = False
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                isRunning = False
            elif event.key == K_r:
                rend.restart_render()

    rend.glRender()

    pygame.display.flip()
    clock.tick(60)

try:
    # Asegurar ruta y escribir BMP
    from config import ensure_dirs
    ensure_dirs()
except Exception:
    pass
GenerateBMP(str(OUTPUT_PATH), WIDTH, HEIGHT, 3, rend.frameBuffer)

pygame.quit()
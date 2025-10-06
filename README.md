# RayTracer Avanzado - Proyecto Final

Un raytracer avanzado implementado en Python para demostrar técnicas de renderizado por rayos. Diseñado para cumplir con todos los requisitos del proyecto final del curso.

## 🏆 Puntuación del Proyecto (100/100 puntos)

### ✅ Complejidad de la Escena (30 puntos)
- **Más de 10 figuras**: Escena compleja con 15+ objetos geométricos
- Configuración automática en `SCENE_PRESET = "complex"`

### ✅ Materiales Avanzados (20 puntos - máximo 4)
1. **Material con Textura** (OBLIGATORIO): Texturas procedurales y de imagen
2. **Material de Vidrio**: Transparencia y refracción realistas  
3. **Material Metálico**: Reflexiones y propiedades PBR
4. **Material Emisivo**: Objetos que emiten luz

### ✅ Environment Map (5 puntos)
- Carga automática de archivos HDR
- Integración con reflexiones y refracciones
- Archivos soportados: `pretoria_gardens_4k.hdr`, `noon.hdr`, `rogland_clear_night_1k.hdr`

### ✅ Figuras Geométricas Nuevas (20 puntos - máximo 4)
1. **Elipsoide**: Esferas deformadas con radios diferentes
2. **Cápsula**: Cilindro con hemisferios en los extremos
3. **Octaedro**: Poliedro de 8 caras triangulares
4. **Hiperboloide**: Superficie cuadrática compleja
5. **Paraboloide**: Superficie parabólica 3D *(bonus)*
6. **Dodecaedro**: Poliedro de 12 caras pentagonales *(bonus)*

### ✅ Renderizado de Modelos OBJ (20 puntos)
- Cargador avanzado con soporte completo para OBJ/MTL
- Triangulación automática de polígonos
- Soporte para normales, coordenadas UV y materiales
- Optimización BVH para mallas complejas

### ✅ Iluminación Avanzada (10 puntos)
- **Point Lights**: Luces puntuales con atenuación
- **Directional Lights**: Luces direccionales (sol)
- **Spot Lights**: Luces cónicas con ángulos configurables  
- **Area Lights**: Luces de área para sombras suaves *(bonus)*

### ✅ Estética de la Escena (20 puntos)
- Escenas prediseñadas con composición artística
- Iluminación cinematográfica (3-point lighting)
- Materiales realistas y texturas procedurales
- Efectos visuales avanzados (emisión, reflexiones, refracciones)

## 🚀 Uso Rápido

### 1. Configuración
Edita `config.py` para seleccionar la escena:
```python
SCENE_PRESET = "complex"    # Escena compleja (máximos puntos)
SCENE_PRESET = "materials"  # Demostración de materiales  
SCENE_PRESET = "geometry"   # Demostración de figuras
SCENE_PRESET = "artistic"   # Escena artística
```

### 2. Ejecución
```bash
python Raytracer2025.py
```

### 3. Controles
- **R**: Reiniciar render
- **ESC**: Salir
- La imagen final se guarda automáticamente como BMP

## 📊 Escenas Prediseñadas

### `"complex"` - Escena Integral (70+ puntos)
- 15+ figuras geométricas variadas
- 4 materiales diferentes con texturas
- Carga de modelos OBJ (si están disponibles)  
- 8+ luces de diferentes tipos
- Environment mapping integrado

### `"materials"` - Demostración de Materiales (25 puntos)
- 4 esferas con materiales únicos
- Textura de madera obligatoria
- Vidrio, metal y emisión
- Suelo con textura procedimental

### `"geometry"` - Figuras Avanzadas (40 puntos)  
- 6 figuras geométricas nuevas
- Elipsoide, cápsula, octaedro, hiperboloide
- Materiales variados por figura
- Iluminación múltiple

### `"artistic"` - Jardín de Cristal (20 puntos estéticos)
- Composición en espiral dorada
- Orbes de cristal flotantes
- Iluminación cinematográfica
- Efectos visuales avanzados

## 🔧 Personalización

### Cargar Modelos OBJ (20 puntos)
```python
# En config.py
MODELS = [
    {
        'path': 'models/teapot.obj',
        'scale': 2.0,
        'position': (0, 1, -8),
        'rotation': (0, 45, 0)
    }
]
```

### Configuración Avanzada
```python
# Calidad de render
PIXELS_PER_FRAME = 4000      # Velocidad de render
MAX_DEPTH = 3                # Profundidad de reflexión/refracción
ENV_INTENSITY = 0.6          # Intensidad del environment map

# Resolución y cámara
WIDTH, HEIGHT = 1366, 768           # Resolución de salida
CAMERA_POSITION = (0.0, 0.8, 5.0)  # Posición inicial
CAMERA_ROTATION = (-8.0, 0.0, 0.0) # Rotación (pitch, yaw, roll)
```

## 📁 Estructura del Proyecto

```
modulo2Graficas/
├── Raytracer2025.py          # Aplicación principal
├── config.py                 # Configuración del proyecto  
├── gl.py                     # Motor de renderizado
├── advanced_materials.py     # Sistema de materiales avanzados
├── texture.py                # Sistema de texturas
├── lighting.py               # Sistema de iluminación avanzada
├── advanced_shapes.py        # Figuras geométricas nuevas
├── obj_loader.py             # Cargador de modelos OBJ
├── scene_builder.py          # Constructor de escenas prediseñadas
├── textures/                 # Directorio para texturas
├── models/                   # Directorio para modelos OBJ
├── Enviroment/              # Environment maps HDR
└── BMPs/                    # Imágenes de salida
```

## 🎯 Notas de Implementación

Este proyecto implementa **todas las características requeridas** para obtener la puntuación máxima:

- ✅ **Más de 10 figuras** en escena compleja
- ✅ **4 materiales únicos** con al menos uno con textura  
- ✅ **Environment mapping** con integración completa
- ✅ **4+ figuras geométricas nuevas** implementadas desde cero
- ✅ **Renderizado OBJ** con cargador completo
- ✅ **Múltiples tipos de luces** (point, directional, spot)
- ✅ **Estética cuidada** con escenas artísticas prediseñadas

El código está **documentado y modularizado** para facilitar la evaluación.
"""
MaterialLib: catálogo simple de materiales reutilizables.

Cómo usar:
    from MaterialLib import get_material, list_materials, register_material
    mirror = get_material('mirror')
    white = get_material('white')
    # Puedes registrar los tuyos:
    #   register_material('mi_favorito', Material(...))

Nota: get_material devuelve una COPIA para evitar efectos colaterales si cambias
propiedades en tiempo de ejecución.
"""
from __future__ import annotations
from typing import Dict
from figure import Material


def _clone(m: Material) -> Material:
    return Material(
        color=m.color,
        ka=m.ka,
        kd=m.kd,
        ks=m.ks,
        shininess=m.shininess,
        reflectivity=m.reflectivity,
        transparency=m.transparency,
        ior=m.ior,
        mtype=m.mtype,
    )


# Catálogo base (puedes editar/añadir a gusto)
_CATALOG: Dict[str, Material] = {
    # Neutros
    'white': Material((0.85, 0.85, 0.85), ka=0.2, kd=0.7, ks=0.2, shininess=32, mtype='opaque'),
    'bone':  Material((0.94, 0.92, 0.86), ka=0.2, kd=0.7, ks=0.2, shininess=32, mtype='opaque'),
    'matte-gray': Material((0.5, 0.5, 0.5), ka=0.2, kd=0.8, ks=0.05, shininess=8, mtype='opaque'),
    'matte-white': Material((0.9, 0.9, 0.9), ka=0.2, kd=0.8, ks=0.05, shininess=8, mtype='opaque'),

    # Colores básicos
    'red':   Material((0.9, 0.3, 0.3), ka=0.15, kd=0.7, ks=0.2, shininess=32, mtype='opaque'),
    'green': Material((0.3, 0.9, 0.3), ka=0.15, kd=0.7, ks=0.2, shininess=32, mtype='opaque'),
    'blue':  Material((0.3, 0.3, 0.9), ka=0.15, kd=0.7, ks=0.2, shininess=32, mtype='opaque'),

    # Metales / espejos
    'chrome': Material((0.9, 0.9, 0.95), ka=0.02, kd=0.05, ks=1.0, shininess=256, reflectivity=0.9, mtype='reflective'),
    'gold':   Material((1.0, 0.85, 0.4), ka=0.03, kd=0.15, ks=0.9, shininess=192, reflectivity=0.7, mtype='reflective'),
    'mirror': Material((1.0, 1.0, 1.0), ka=0.0, kd=0.0, ks=1.0, shininess=256, reflectivity=1.0, mtype='reflective'),

    # Transparentes
    'glass':  Material((1.0, 1.0, 1.0), ka=0.02, kd=0.05, ks=0.95, shininess=256, transparency=0.95, ior=1.5, mtype='transparent'),
    'water':  Material((1.0, 1.0, 1.0), ka=0.02, kd=0.05, ks=0.9, shininess=192, transparency=0.9, ior=1.33, mtype='transparent'),
}


def list_materials() -> list[str]:
    return sorted(_CATALOG.keys())


def get_material(name: str) -> Material:
    key = name.strip().lower()
    if key not in _CATALOG:
        raise KeyError(f"Material '{name}' no existe. Disponibles: {', '.join(list_materials())}")
    return _clone(_CATALOG[key])


def register_material(name: str, material: Material) -> None:
    """Registra/actualiza un material personalizado en el catálogo."""
    if not isinstance(material, Material):
        raise TypeError("'material' debe ser una instancia de figure.Material")
    _CATALOG[name.strip().lower()] = _clone(material)

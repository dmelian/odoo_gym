# 01 — Estructura de un módulo Odoo 17

Un módulo Odoo es simplemente una carpeta dentro de `addons/` con un
`__manifest__.py` y un `__init__.py`. A partir de ahí, el resto son
convenciones.

## Árbol de carpetas típico

```
mi_modulo/
├── __init__.py                 # importa los subpaquetes Python
├── __manifest__.py             # metadatos del módulo (obligatorio)
├── models/
│   ├── __init__.py             # importa cada modelo
│   └── mi_modelo.py
├── views/
│   ├── mi_modelo_views.xml     # tree/form/search + action del modelo
│   └── menu.xml                # menús (se cargan al final)
├── controllers/
│   ├── __init__.py
│   └── main.py                 # rutas http (portal o web)
├── security/
│   └── ir.model.access.csv     # permisos mínimos de cada modelo
├── data/
│   └── mi_modelo_data.xml      # datos maestros (opcional)
├── demo/
│   └── mi_modelo_demo.xml      # datos de prueba (opcional)
└── static/
    └── src/
        ├── js/
        ├── css/
        └── img/
```

## Plantilla de `__manifest__.py`

```python
# __manifest__.py
{
    'name': 'Mi Módulo',                  # nombre visible
    'version': '17.0.1.0.0',              # versión (Odoo 17 + tu semver)
    'summary': 'Qué hace este módulo',    # una línea
    'author': 'Tu nombre',
    'category': 'Services',               # categoría en Aplicaciones
    'license': 'LGPL-3',

    # Otros módulos necesarios para que el tuyo funcione.
    # 'base' está implícito; añade los que USES de verdad.
    'depends': [
        'base',
        'mail',       # si vas a usar chatter (mail.thread / mail.activity.mixin)
        'website',    # si vas a servir páginas web públicas
        'portal',     # si vas a añadir secciones en /my
    ],

    # Archivos XML/CSV que se cargan al instalar/actualizar.
    # ¡El ORDEN IMPORTA! Seguridad primero, luego datos, vistas y por último menús.
    'data': [
        'security/ir.model.access.csv',
        'data/mi_modelo_data.xml',
        'views/mi_modelo_views.xml',
        'views/menu.xml',                 # menús siempre al final
    ],

    # Datos que solo se cargan si Odoo arranca con --load-demo
    'demo': [
        'demo/mi_modelo_demo.xml',
    ],

    'installable': True,
    'application': True,                  # aparece como “App” en el menú de apps
}
```

## Plantilla de `__init__.py` raíz

```python
# __init__.py
from . import models
from . import controllers
```

## Plantilla de `models/__init__.py`

```python
# models/__init__.py
# Una línea por archivo de modelo.
# El orden importa si un modelo hace referencia a otro (importa primero el
# modelo “base” y después los que lo usan).
from . import mi_modelo
from . import otro_modelo
```

## Plantilla de `controllers/__init__.py`

```python
# controllers/__init__.py
from . import main
# from . import portal    # si separas el controlador del portal en otro archivo
```

## Comandos habituales al desarrollar

```bash
# Instalar el módulo por primera vez
odoo -d mi_bd -i mi_modulo

# Actualizar el módulo tras cambios en código o XML
odoo -d mi_bd -u mi_modulo

# Con datos demo
odoo -d mi_bd -i mi_modulo --load-demo
```

## Errores típicos al crear un módulo

- Olvidar importar el modelo en `models/__init__.py` → el modelo no existe
  y la vista explota con *“Model not found”*.
- Olvidar añadir el XML al `data` del manifest → las vistas no se cargan.
- Poner `menu.xml` antes que las vistas con acciones → error *“External ID
  not found: action_xxx”* porque el menú referencia una acción que aún no
  existe.
- Cambiar el nombre de un campo sin actualizar con `-u` → error al renderizar.

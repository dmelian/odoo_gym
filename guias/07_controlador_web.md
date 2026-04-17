# 07 — Controlador web básico

Un controlador expone URLs a las que responde tu módulo. Es el
equivalente a una vista de Django / un controller de Rails. Una ruta =
un método Python decorado con `@http.route`.

## Mínimos para tener una página pública en `/mi-pagina`

### 1. Asegúrate del manifest y dependencias

```python
# __manifest__.py
{
    # ...
    'depends': ['web'],    # suficiente para servir páginas con layout web
    'data': ['views/templates.xml'],
}
```

### 2. Controlador

```python
# controllers/main.py
from odoo import http
from odoo.http import request


class MiControlador(http.Controller):

    @http.route('/mi-pagina', type='http', auth='public', website=True)
    def mi_pagina(self, **kwargs):
        return request.render('mi_modulo.mi_pagina_template', {})
```

Desglose de `@http.route`:

| Parámetro | Qué hace |
|---|---|
| `'/mi-pagina'` | URL que atiende el método. Puede tener parámetros: `/item/<int:item_id>`. |
| `type='http'` | Respuesta HTML normal. El otro valor es `'json'` (API JSON). |
| `auth='public'` | Cualquiera puede entrar (visitante no logueado). Otros valores: `'user'` (logueado), `'portal'`. |
| `website=True` | La página se sirve bajo el *website* actual (idioma, tema, etc.). |

### 3. No te olvides del `__init__.py`

```python
# __init__.py (raíz del módulo)
from . import controllers
```

```python
# controllers/__init__.py
from . import main
```

### 4. Plantilla QWeb (`views/templates.xml`)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <template id="mi_pagina_template" name="Mi Página">
        <!-- t-call="web.layout" incluye HTML base, head, body, etc. -->
        <t t-call="web.layout">

            <!-- Contenido del <head>: título, meta, etc. -->
            <t t-set="head">
                <title>Mi Página</title>
            </t>

            <div class="container mt-4">
                <h1>Hola desde mi página estática</h1>
                <p>Esta página la sirve Odoo desde mi módulo.</p>
            </div>

        </t>
    </template>

</odoo>
```

El ID completo de la plantilla es `<nombre_modulo>.<template_id>`, por
eso el `render` usa `mi_modulo.mi_pagina_template`.

## Pasar datos del controlador a la plantilla

```python
@http.route('/saludo/<string:nombre>', type='http', auth='public', website=True)
def saludo(self, nombre, **kwargs):
    return request.render('mi_modulo.saludo_template', {
        'nombre': nombre,
        'ahora': fields.Datetime.now(),
        'items': request.env['mi.modelo'].sudo().search([('active', '=', True)]),
    })
```

```xml
<template id="saludo_template" name="Saludo">
    <t t-call="web.layout">
        <div class="container mt-4">
            <!-- t-esc: imprime texto escapado (seguro) -->
            <h1>Hola, <t t-esc="nombre"/></h1>
            <p>Son las <t t-esc="ahora"/></p>

            <!-- t-foreach: recorre una lista / recordset -->
            <ul>
                <t t-foreach="items" t-as="item">
                    <li>
                        <t t-esc="item.name"/>
                        <!-- t-if / t-else: condicionales -->
                        <t t-if="item.active">
                            <span class="badge bg-success">Activo</span>
                        </t>
                        <t t-else="">
                            <span class="badge bg-secondary">Archivado</span>
                        </t>
                    </li>
                </t>
            </ul>
        </div>
    </t>
</template>
```

## Parámetros de URL y de formulario

- **Path params**: se declaran con `<tipo:nombre>` en la ruta.
  Tipos: `int`, `string`, `model('mi.modelo')` (carga el registro).
- **Query string / form**: llegan en `**kwargs` (o como argumento con
  nombre).

```python
# /buscar?q=hola
@http.route('/buscar', type='http', auth='public', website=True)
def buscar(self, q='', **kwargs):
    results = request.env['mi.modelo'].sudo().search([
        ('name', 'ilike', q),
    ])
    return request.render('mi_modulo.buscar_template', {'q': q, 'results': results})
```

```python
# Recibe el registro ya cargado por la URL (/item/7)
@http.route('/item/<model("mi.modelo"):item>', type='http', auth='public', website=True)
def ver_item(self, item, **kwargs):
    return request.render('mi_modulo.item_template', {'item': item})
```

## `sudo()` y `env.user`

- `request.env` ejecuta con los permisos del usuario actual.
- `request.env.user` es el usuario logueado (o el usuario público si
  `auth='public'`).
- `.sudo()` ignora los permisos de acceso. Úsalo **solo** cuando sabes
  que necesitas leer/escribir algo que el visitante no tendría permiso
  para ver por sí mismo.

## Recursos estáticos

Los archivos en `static/src/img/`, `static/src/js/`, `static/src/css/`
se sirven automáticamente en la URL `/<nombre_modulo>/static/src/...`.

```xml
<img src="/mi_modulo/static/src/img/logo.png"/>
```

Para JavaScript/CSS con el bundle de Odoo se declaran en el manifest:

```python
'assets': {
    'web.assets_frontend': [
        'mi_modulo/static/src/css/mi_estilo.css',
        'mi_modulo/static/src/js/mi_script.js',
    ],
},
```

# 08 — Controlador del portal (`/my`)

El portal es el área privada en `/my` donde los clientes (grupo
`base.group_portal`) ven sus datos: facturas, pedidos, etc. Para añadir
una sección propia hay que:

1. Declarar `portal` como dependencia.
2. Heredar `CustomerPortal` para registrar tu sección en `/my`.
3. Escribir tus rutas `/my/...`.
4. Añadir la tarjeta/entrada en el índice `/my` con una herencia de
   plantilla QWeb.

## 1. Manifest

```python
# __manifest__.py
{
    # ...
    'depends': ['portal'],
    'data': ['views/templates.xml'],
}
```

## 2. Controlador: índice y rutas

```python
# controllers/main.py
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class MiPortal(CustomerPortal):

    # --------------------------------------------------------------
    # _prepare_home_portal_values:
    #   Se ejecuta al renderizar /my y /my/home. Permite inyectar
    #   contadores y valores que se muestran en las tarjetas del índice
    #   (por ejemplo "5 facturas pendientes").
    #   'counters' es la lista de contadores que la plantilla de /my
    #   ha pedido explícitamente: solo calcúlalos si están ahí (ahorra
    #   consultas).
    # --------------------------------------------------------------
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)

        if 'mi_count' in counters:
            values['mi_count'] = request.env['mi.modelo'].sudo().search_count([
                ('user_id', '=', request.env.user.id),
            ])

        return values

    # --------------------------------------------------------------
    # Rutas del área privada. auth='user' obliga a estar logueado.
    # Si el usuario no está logueado, Odoo redirige al login.
    # --------------------------------------------------------------
    @http.route('/my/mi-pagina', type='http', auth='user', website=True)
    def mi_pagina(self, **kwargs):
        # Busca los datos que pertenecen al usuario actual.
        # Usamos sudo() porque el grupo 'base.group_portal' tiene
        # permisos muy limitados por defecto.
        records = request.env['mi.modelo'].sudo().search([
            ('user_id', '=', request.env.user.id),
        ])

        return request.render('mi_modulo.mi_pagina_template', {
            'records': records,
            'page_name': 'mi_pagina',    # útil para breadcrumbs del portal
        })

    @http.route('/my/mi-pagina/<int:record_id>', type='http',
                auth='user', website=True)
    def mi_detalle(self, record_id, **kwargs):
        record = request.env['mi.modelo'].sudo().browse(record_id)

        # Validación: ¿existe y pertenece a este usuario?
        if not record.exists() or record.user_id.id != request.env.user.id:
            return request.redirect('/my')

        return request.render('mi_modulo.mi_detalle_template', {
            'record': record,
        })
```

## 3. Plantillas QWeb del portal

El portal tiene un layout propio con el sidebar y breadcrumbs. Úsalo
con `t-call="portal.portal_layout"`.

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <!-- Página /my/mi-pagina -->
    <template id="mi_pagina_template" name="Mi Página Portal">
        <t t-call="portal.portal_layout">

            <!-- Muestra la barra de búsqueda del portal (opcional) -->
            <t t-set="breadcrumbs_searchbar" t-value="True"/>

            <!-- portal_record_layout: tarjeta con header + body -->
            <t t-call="portal.portal_record_layout">
                <t t-set="card_header">
                    <h5 class="mb-0">Mi Página</h5>
                </t>
                <t t-set="card_body">
                    <h1>Bienvenido, <t t-esc="user.name"/></h1>

                    <t t-if="records">
                        <ul class="list-group">
                            <t t-foreach="records" t-as="rec">
                                <li class="list-group-item">
                                    <a t-attf-href="/my/mi-pagina/{{ rec.id }}">
                                        <t t-esc="rec.name"/>
                                    </a>
                                </li>
                            </t>
                        </ul>
                    </t>
                    <t t-else="">
                        <p>No tienes registros todavía.</p>
                    </t>
                </t>
            </t>
        </t>
    </template>

</odoo>
```

## 4. Añadir la tarjeta en el índice `/my`

Para que aparezca una tarjeta en `/my` que lleve a tu página, hay que
heredar la plantilla `portal.portal_my_home`.

### Variante simple (docs/entry)

```xml
<template id="portal_my_home_entry_mi_modulo"
          inherit_id="portal.portal_my_home"
          customize_show="True"
          name="Mi Página en Portal">
    <!-- xpath: encuentra el contenedor de entradas en el layout base -->
    <xpath expr="//div[hasclass('o_portal_docs')]" position="inside">

        <!-- Una entrada por cada sección. -->
        <t t-call="portal.portal_docs_entry">
            <t t-set="title">Mi Página</t>
            <t t-set="url">/my/mi-pagina</t>
            <t t-set="text">Accede a mi sección</t>
            <t t-set="icon" t-value="'/portal/static/src/img/portal-addresses.svg'"/>
            <t t-set="config_card" t-value="True"/>

            <!-- Contador opcional: debe coincidir con la clave que
                 inyectas en _prepare_home_portal_values. -->
            <t t-set="placeholder_count" t-value="'mi_count'"/>
            <t t-set="show_count" t-value="True"/>
        </t>

    </xpath>
</template>
```

### Variante con tarjeta grande propia

Si quieres un look más destacado (como hace por ejemplo el módulo de
facturas):

```xml
<template id="portal_my_home_mi_modulo"
          inherit_id="portal.portal_my_home"
          priority="30">
    <xpath expr="//div[@id='portal_common_category']" position="before">
        <div class="o_portal_category row g-2 mt-3">
            <div class="o_portal_index_card col-md-6 order-2">
                <a href="/my/mi-pagina" title="Mi sección"
                   class="d-flex gap-2 gap-md-3 py-3 pe-2 px-md-3 h-100
                          rounded text-decoration-none bg-100">
                    <div class="o_portal_icon d-block align-self-start">
                        <img src="/mi_modulo/static/src/img/icono.svg"/>
                    </div>
                    <div>
                        <div class="mt-0 mb-1 fs-5 fw-normal lh-1">
                            <span>Mi sección</span>
                        </div>
                        <div class="opacity-75">
                            Una descripción corta.
                        </div>
                    </div>
                </a>
            </div>
        </div>
    </xpath>
</template>
```

## Puntos clave a recordar

- El portal usa el grupo `base.group_portal`. Dale permisos de lectura
  (como mínimo) a tus modelos en `ir.model.access.csv` si el usuario
  los va a usar sin `sudo()`. Si usas `sudo()`, técnicamente no hace
  falta… pero sigue siendo buena práctica declarar qué permisos
  *debería* tener.
- `auth='user'` exige usuario logueado (sea interno o del portal).
  Para restringir **solo** a usuarios del portal, usa `auth='user'` y
  valida en el método: `if not request.env.user.has_group('base.group_portal'): ...`.
- Las URLs del portal por convención empiezan por `/my/`.
- Para dar de alta a un cliente como usuario del portal: en la ficha
  de contacto → menú Acción → “Conceder acceso al portal”.

## Depuración

- `request.env.user` → usuario actual.
- `request.httprequest.referrer` → de dónde vino.
- `request.session.debug = '1'` (temporal) → activa modo desarrollador.
- Usa un `_logger = logging.getLogger(__name__)` y `_logger.warning(...)`
  para inspeccionar el flujo en los logs.

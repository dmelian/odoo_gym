# Guías de desarrollo Odoo 17

Colección progresiva de plantillas reutilizables para construir un módulo Odoo
paso a paso. Cada guía incluye comentarios didácticos y los huecos que tienes
que rellenar cuando empieces un módulo nuevo.

El hilo conductor es: **construir un módulo nuevo desde cero**, añadiendo en
cada guía una capa más del stack.

## Orden de lectura

1. [01_estructura_modulo.md](01_estructura_modulo.md) — Carpetas, `__manifest__.py`, `__init__.py`.
2. [02_modelo_basico.md](02_modelo_basico.md) — Tu primer modelo con campos, chatter y restricciones.
3. [03_seguridad.md](03_seguridad.md) — Permisos `ir.model.access.csv` mínimos.
4. [04_acciones_menus_vistas.md](04_acciones_menus_vistas.md) — Acción, menú, tree, form y search.
5. [05_modelos_relacionados.md](05_modelos_relacionados.md) — Many2one, One2many, Many2many, related y computed.
6. [06_herencia_partner.md](06_herencia_partner.md) — Extender `res.partner` y vincular contactos a tus modelos.
7. [07_controlador_web.md](07_controlador_web.md) — Página web pública con `http.Controller` y QWeb.
8. [08_controlador_portal.md](08_controlador_portal.md) — Sección en `/my` heredando `CustomerPortal`.

## Regla de oro

Después de añadir un modelo nuevo **siempre** toca:

1. Añadir la clase al `__init__.py` de `models/`.
2. Añadir la línea del permiso al `ir.model.access.csv`.
3. Añadir el archivo XML de vistas al `data` del `__manifest__.py`.
4. Reiniciar Odoo con `-u nombre_modulo` para que aplique cambios de modelo o XML.

Si no ves tus cambios, el 90% de las veces es que has olvidado uno de esos
cuatro pasos.

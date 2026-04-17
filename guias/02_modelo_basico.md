# 02 — Modelo básico

Un modelo es una clase Python que hereda de `models.Model`. Odoo se encarga
de crear su tabla en PostgreSQL, su ORM y sus vistas por defecto.

## Plantilla mínima

```python
# models/mi_modelo.py
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MiModelo(models.Model):
    # Nombre técnico del modelo (minúsculas, puntos como separador).
    # Será también el nombre de la tabla (con _ en lugar de .).
    _name = 'mi.modelo'

    # Texto que aparece en la interfaz (logs, errores, etc).
    _description = 'Descripción legible del modelo'

    # Mixins opcionales: añaden chatter (histórico de mensajes) y
    # panel de actividades. Muy recomendable para modelos importantes.
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Orden por defecto al listar registros.
    _order = 'name'

    # ------------------------------------------------------------------
    # CAMPOS
    # ------------------------------------------------------------------

    # Char: texto corto. tracking=True registra los cambios en el chatter.
    name = fields.Char(
        string='Nombre',      # etiqueta visible
        required=True,        # no puede quedar vacío
        tracking=True,
    )

    # Text: texto largo multilinea.
    description = fields.Text(string='Descripción')

    # Integer / Float: números.
    capacity = fields.Integer(string='Aforo', default=10)
    price = fields.Float(string='Precio', digits=(10, 2))

    # Boolean: casilla. 'active' es un campo especial: si es False, Odoo
    # considera el registro como archivado y lo oculta por defecto.
    active = fields.Boolean(string='Activo', default=True)

    # Date / Datetime.
    date_start = fields.Date(
        string='Fecha inicio',
        required=True,
        default=fields.Date.today,    # por defecto hoy
    )
    date_end = fields.Date(string='Fecha fin')

    # Selection: lista cerrada de opciones. El valor guardado es la primera
    # parte de la tupla, la segunda es la etiqueta visible.
    state = fields.Selection(
        selection=[
            ('draft', 'Borrador'),
            ('confirmed', 'Confirmado'),
            ('done', 'Hecho'),
        ],
        string='Estado',
        default='draft',
        tracking=True,
    )

    # ------------------------------------------------------------------
    # RESTRICCIONES (CONSTRAINTS)
    # ------------------------------------------------------------------

    # @api.constrains valida cada vez que se crea o modifica un registro.
    # Los campos que menciones activan la validación cuando cambian.
    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for record in self:
            if record.date_end and record.date_end < record.date_start:
                raise ValidationError(
                    'La fecha fin no puede ser anterior a la fecha inicio.'
                )

    # _sql_constraints: se traducen en restricciones de PostgreSQL.
    # Más rápidas que @api.constrains pero más limitadas.
    _sql_constraints = [
        (
            'unique_name',                    # identificador interno
            'UNIQUE(name)',                    # SQL
            'Ya existe un registro con ese nombre.',  # mensaje de error
        ),
    ]

    # ------------------------------------------------------------------
    # MÉTODOS DE BOTÓN
    # ------------------------------------------------------------------
    # Estos métodos se llaman desde botones de la vista con type="object".

    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'

    def action_done(self):
        for record in self:
            record.state = 'done'
```

## Tipos de campo más usados

| Tipo de campo | Para qué sirve |
|---|---|
| `Char` | texto corto (≤255 caracteres) |
| `Text` | texto largo multilinea |
| `Html` | contenido HTML, se renderiza con editor WYSIWYG |
| `Integer`, `Float` | números |
| `Monetary` | importes, necesita un campo `currency_id` |
| `Boolean` | casilla |
| `Date`, `Datetime` | fechas y fechas con hora |
| `Selection` | lista cerrada de opciones |
| `Binary` | archivos, imágenes (`Image` es un alias con recorte) |
| `Many2one`, `One2many`, `Many2many` | relaciones (guía 05) |

## Atributos útiles de cualquier campo

```python
field = fields.Char(
    string='Etiqueta',         # texto visible
    required=True,             # obligatorio
    readonly=True,             # solo lectura en la vista
    default='valor',           # valor por defecto (también una lambda)
    default=lambda self: self.env.user.name,
    help='Tooltip en la vista',
    tracking=True,             # registrar cambios en el chatter
    copy=False,                # no copiar al duplicar un registro
    index=True,                # crear índice en la base de datos
)
```

## Sobrescribir `create` y `write`

Muy común para asignar secuencias automáticas:

```python
@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        if vals.get('name', '/') in ('/', ''):
            vals['name'] = self.env['ir.sequence'].next_by_code('mi.modelo')
    return super().create(vals_list)
```

> En Odoo 17 `create` recibe una **lista** de diccionarios gracias a
> `@api.model_create_multi`. Siempre usa este decorador.

## Recordatorio final

Tras crear el modelo:

1. Importarlo en `models/__init__.py`.
2. Crearle un permiso en `ir.model.access.csv` (guía 03).
3. Crearle vistas y una acción (guía 04).
4. Reiniciar Odoo con `-u mi_modulo`.

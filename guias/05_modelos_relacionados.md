# 05 — Modelos relacionados

En Odoo casi ningún modelo vive solo. Los tres tipos de relación son:

- **Many2one**: un registro apunta a otro (como una FK).
- **One2many**: el “otro lado” de un Many2one. Un registro tiene N hijos.
- **Many2many**: tabla intermedia, cada lado puede tener N del otro.

## Many2one: “pertenece a”

```python
# models/linea.py
class Linea(models.Model):
    _name = 'mi.linea'
    _description = 'Línea de una cabecera'

    cabecera_id = fields.Many2one(
        comodel_name='mi.cabecera',    # modelo al que apunta
        string='Cabecera',
        required=True,
        ondelete='cascade',            # si borras la cabecera, se borran las líneas
        tracking=True,
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Producto',
        ondelete='restrict',           # no deja borrar un producto si tiene líneas
    )
    responsable_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsable',
        default=lambda self: self.env.user,
    )
```

### Opciones de `ondelete`

| Valor | Comportamiento al borrar el padre |
|---|---|
| `cascade` | Borra también los hijos. Típico en líneas. |
| `restrict` | No deja borrar el padre si tiene hijos. Protección fuerte. |
| `set null` | Hijos apuntan a NULL. Valor por defecto si no especificas. |

## One2many: “tiene muchos”

Un `One2many` **necesita** un `Many2one` en el otro modelo. Es sólo el
reflejo lógico de esa relación.

```python
# models/cabecera.py
class Cabecera(models.Model):
    _name = 'mi.cabecera'
    _description = 'Cabecera con líneas'

    name = fields.Char(required=True)

    line_ids = fields.One2many(
        comodel_name='mi.linea',    # el modelo hijo
        inverse_name='cabecera_id', # el Many2one en el modelo hijo que apunta aquí
        string='Líneas',
    )

    line_count = fields.Integer(
        string='Nº de líneas',
        compute='_compute_line_count',
    )

    @api.depends('line_ids')
    def _compute_line_count(self):
        for rec in self:
            rec.line_count = len(rec.line_ids)
```

En la vista se edita como una tabla “inline”:

```xml
<notebook>
    <page string="Líneas" name="lines">
        <field name="line_ids">
            <!-- tree embebido: se edita al vuelo dentro del form padre -->
            <tree editable="bottom">
                <field name="product_id"/>
                <field name="responsable_id"/>
            </tree>
        </field>
    </page>
</notebook>
```

## Many2many: “N a N”

```python
# models/mi_modelo.py
tag_ids = fields.Many2many(
    comodel_name='mi.tag',
    # Todos estos son opcionales. Si no los pones, Odoo genera los nombres:
    relation='mi_modelo_tag_rel',       # nombre de la tabla intermedia
    column1='mi_modelo_id',             # FK hacia este modelo
    column2='tag_id',                   # FK hacia el otro modelo
    string='Etiquetas',
)
```

En la vista:

```xml
<field name="tag_ids" widget="many2many_tags"/>
```

## Campos relacionados (`related=`)

Un atajo de solo lectura a un campo de un modelo vinculado. Ahorra
escribir lógica en vistas y búsquedas.

```python
class MiLinea(models.Model):
    _name = 'mi.linea'

    cabecera_id = fields.Many2one('mi.cabecera')

    # Traigo el nombre de la cabecera como si fuera un campo propio.
    # store=True lo guarda físicamente para poder filtrar/agrupar por él.
    cabecera_name = fields.Char(
        related='cabecera_id.name',
        string='Nombre cabecera',
        store=True,
    )
    responsable_id = fields.Many2one(
        comodel_name='res.users',
        related='cabecera_id.responsable_id',
        store=True,
    )
```

## Campos computados (`compute=`)

Valor calculado a partir de otros campos. `@api.depends` indica **cuándo**
recalcular.

```python
price_unit = fields.Float()
quantity = fields.Float()

price_total = fields.Float(
    string='Total',
    compute='_compute_price_total',
    store=True,           # se guarda en DB: se puede filtrar/agrupar por él
)

@api.depends('price_unit', 'quantity')
def _compute_price_total(self):
    for record in self:
        record.price_total = record.price_unit * record.quantity
```

- Si `store=False` (por defecto), el campo se recalcula al vuelo y **no**
  se puede usar en filtros/búsquedas.
- Si `store=True`, Odoo mantiene el valor en DB y recalcula cuando
  cambian sus dependencias.

## `onchange`: reaccionar en el formulario

Se dispara solo en el front-end (no en create/write). Útil para rellenar
campos automáticamente.

```python
@api.onchange('cabecera_id')
def _onchange_cabecera_id(self):
    if self.cabecera_id:
        self.responsable_id = self.cabecera_id.responsable_id
```

## Dominios dinámicos en la vista

Filtrar las opciones de un Many2one según el valor de otro campo:

```xml
<field name="activity_id"/>
<field name="schedule_id"
       domain="[('activity_id', '=', activity_id)]"/>
```

Cuando el usuario cambie `activity_id`, el desplegable de `schedule_id`
sólo mostrará horarios de esa actividad.

## Stat button con acción que filtra

Para enlazar de un registro “padre” a sus “hijos”:

```python
def action_open_lines(self):
    self.ensure_one()
    return {
        'type': 'ir.actions.act_window',
        'name': 'Líneas',
        'res_model': 'mi.linea',
        'view_mode': 'tree,form',
        'domain': [('cabecera_id', '=', self.id)],
        'context': {'default_cabecera_id': self.id},
    }
```

- `domain` filtra para ver solo las líneas de esta cabecera.
- `context` precarga el Many2one al crear un registro nuevo desde esa
  lista (`default_cabecera_id` → rellena `cabecera_id`).

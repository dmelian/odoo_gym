# 06 — Herencia de `res.partner` y relaciones con contactos

`res.partner` es el modelo central de contactos (clientes, proveedores,
empleados, etc.). Hay dos formas de conectar tus modelos con él:

1. **Usarlo con Many2one** — tu modelo tiene un campo `partner_id`.
2. **Heredarlo (`_inherit = 'res.partner'`)** — añades campos y
   comportamiento al propio `res.partner`.

Elige la opción según si lo que quieres guardar son *atributos del
contacto* (hereda) o una *entidad separada* que simplemente se asocia con
un contacto (Many2one).

## Opción A: modelo propio con Many2one a `res.partner`

Úsalo cuando tu modelo tiene sentido por sí mismo (por ejemplo
“Suscripción”, “Reserva”, “Expediente”) y el partner es solo un dato
asociado.

```python
class MiSuscripcion(models.Model):
    _name = 'mi.suscripcion'
    _description = 'Suscripción'

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Cliente',
        required=True,
        ondelete='restrict',
    )

    # Relacionados para ver datos del contacto sin saltar de pantalla
    email = fields.Char(related='partner_id.email', readonly=True)
    phone = fields.Char(related='partner_id.phone', readonly=True)
```

## Opción B: herencia de `res.partner`

Úsalo cuando el concepto de tu modelo **es** un contacto con campos
extra (“Monitor del gimnasio”, “Médico”, “Profesor”).

### Plantilla

```python
# models/mi_entidad.py
from odoo import models, fields


class ResPartner(models.Model):
    # Al repetir _name = 'res.partner' y usar _inherit, estás extendiendo
    # el modelo existente, NO creando uno nuevo. No se crea tabla nueva:
    # las columnas se AÑADEN a la tabla res_partner.
    _inherit = 'res.partner'
    # res.partner ya tiene chatter (mail.thread / mail.activity.mixin).

    # Campos adicionales que pasan a existir en TODOS los res.partner.
    gym_member_type = fields.Selection(
        selection=[
            ('member', 'Abonado'),
            ('instructor', 'Monitor'),
            ('admin', 'Administrativo'),
        ],
        string='Tipo',
        default=False,
        tracking=True,
    )
    date_start = fields.Date(
        string='Fecha de alta',
        default=fields.Date.today,
    )
```

### Seguridad al heredar `res.partner`

Los permisos de `res.partner` ya existen en el módulo `base`. **No**
añades una línea nueva por `res.partner` — los campos nuevos heredan los
permisos del modelo padre. Solo tendrías que crear reglas (`ir.rule`) si
quieres limitar visibilidad.

### Vista + acción filtrada por el tipo

Aunque técnicamente son `res.partner`, quieres que en tu app solo
aparezcan los de tu tipo. El truco es:

- La vista apunta a `model="res.partner"`.
- La acción añade un `domain` que filtra.
- El `context` precarga `default_<campo>` para que al crear ya venga
  marcado.

```xml
<!-- views/mi_entidad_views.xml -->
<odoo>

    <record id="view_gym_instructor_tree" model="ir.ui.view">
        <field name="name">gym.instructor.tree</field>
        <field name="model">res.partner</field>
        <field name="arch" type="xml">
            <tree string="Monitores">
                <field name="name"/>
                <field name="email"/>
                <field name="phone"/>
                <field name="gym_member_type"/>
            </tree>
        </field>
    </record>

    <record id="view_gym_instructor_form" model="ir.ui.view">
        <field name="name">gym.instructor.form</field>
        <field name="model">res.partner</field>
        <field name="arch" type="xml">
            <form string="Monitor">
                <sheet>
                    <!-- Campos nativos de res.partner -->
                    <field name="image_1920" widget="image" class="oe_avatar"/>
                    <div class="oe_title">
                        <label for="name"/>
                        <h1><field name="name" placeholder="Nombre"/></h1>
                    </div>

                    <group>
                        <group string="Datos del gimnasio">
                            <field name="gym_member_type"/>
                            <field name="date_start"/>
                        </group>
                        <group string="Contacto">
                            <field name="email" widget="email"/>
                            <field name="phone" widget="phone"/>
                            <field name="mobile" widget="phone"/>
                        </group>
                    </group>

                    <group string="Dirección">
                        <field name="street"/>
                        <field name="street2"/>
                        <field name="zip"/>
                        <field name="city"/>
                        <field name="state_id"/>
                        <field name="country_id"/>
                    </group>
                </sheet>
                <chatter/>
            </form>
        </field>
    </record>

    <record id="action_gym_instructors" model="ir.actions.act_window">
        <field name="name">Monitores</field>
        <field name="res_model">res.partner</field>
        <field name="view_mode">tree,form</field>

        <!-- Solo muestra los partners de tipo "instructor" -->
        <field name="domain">[('gym_member_type', '=', 'instructor')]</field>

        <!-- Al crear uno nuevo, ya se marca como instructor -->
        <field name="context">{'default_gym_member_type': 'instructor'}</field>

        <!-- Opcional: forzar que use TUS vistas (no las genéricas de res.partner) -->
        <field name="view_ids" eval="[
            (5, 0, 0),
            (0, 0, {'view_mode': 'tree', 'view_id': ref('view_gym_instructor_tree')}),
            (0, 0, {'view_mode': 'form', 'view_id': ref('view_gym_instructor_form')}),
        ]"/>
    </record>

</odoo>
```

> El `view_ids` con `(5, 0, 0)` limpia la lista y luego añade tus vistas.
> Sin esto, Odoo muestra la vista estándar de contactos.

## Extender una vista en lugar de crear una nueva

Si solo quieres **añadir** un campo a la vista de contactos existente:

```xml
<record id="view_partner_form_gym" model="ir.ui.view">
    <field name="name">res.partner.form.gym</field>
    <field name="model">res.partner</field>
    <!-- inherit_id indica que es una herencia de la vista estándar -->
    <field name="inherit_id" ref="base.view_partner_form"/>
    <field name="arch" type="xml">
        <!-- xpath localiza un punto de la vista base y te deja insertar -->
        <xpath expr="//field[@name='vat']" position="after">
            <field name="gym_member_type"/>
        </xpath>
    </field>
</record>
```

Valores de `position`:

| Valor | Qué hace |
|---|---|
| `after` | Inserta justo después del nodo localizado. |
| `before` | Inserta justo antes. |
| `inside` | Inserta dentro (al final) del nodo. |
| `replace` | Sustituye el nodo. |
| `attributes` | Cambia atributos del nodo (sintaxis especial). |

## Vincular tu modelo propio con un usuario del portal

Para que un cliente acceda al portal y vea sus datos, necesitas vincular
su `res.users` con tu modelo:

```python
class GymMember(models.Model):
    _name = 'gym.member'

    name = fields.Char(required=True)
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Usuario Odoo',
        help='Vincula el abonado con un usuario para el portal web',
    )
```

En el controlador del portal luego buscarás por `user_id = current_user`
(ver guía 08).

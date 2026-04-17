# 04 — Acciones, menús y vistas

Un modelo no se ve en la interfaz hasta que le das tres cosas:

1. **Vistas** (tree, form, search, kanban, calendar…): cómo se muestran
   los registros.
2. **Acción de ventana** (`ir.actions.act_window`): qué se abre cuando
   haces clic en un menú o un botón.
3. **Menú** (`menuitem`): el punto de entrada en la navegación.

Todo esto se define en XML dentro de `views/`.

## Plantilla completa: `views/mi_modelo_views.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <!-- ============================================================
         VISTA LISTA (tree)
         Columnas que se ven al listar. decoration-* colorea filas
         según una condición sobre los datos.
         ============================================================ -->
    <record id="view_mi_modelo_tree" model="ir.ui.view">
        <field name="name">mi.modelo.tree</field>
        <field name="model">mi.modelo</field>
        <field name="arch" type="xml">
            <tree string="Mi modelo"
                  decoration-success="state == 'done'"
                  decoration-info="state == 'draft'"
                  decoration-danger="state == 'cancelled'">
                <field name="name"/>
                <field name="date_start"/>
                <field name="state"/>
            </tree>
        </field>
    </record>

    <!-- ============================================================
         VISTA FORMULARIO (form)
         Detalle de un registro. Estructura típica:
           <header>  → botones y statusbar
           <sheet>   → contenido principal (título, grupos, notebook)
           <chatter/>→ mensajes + actividades (requiere mail.thread)
         ============================================================ -->
    <record id="view_mi_modelo_form" model="ir.ui.view">
        <field name="name">mi.modelo.form</field>
        <field name="model">mi.modelo</field>
        <field name="arch" type="xml">
            <form string="Mi modelo">
                <header>
                    <!-- Botones de flujo. type="object" llama a un método Python. -->
                    <button name="action_confirm" string="Confirmar"
                            type="object" class="btn-primary"
                            invisible="state != 'draft'"/>
                    <button name="action_done" string="Finalizar"
                            type="object" class="btn-success"
                            invisible="state != 'confirmed'"/>

                    <!-- Statusbar visible: solo muestra estos estados como pasos. -->
                    <field name="state" widget="statusbar"
                           statusbar_visible="draft,confirmed,done"/>
                </header>

                <sheet>
                    <!-- Título grande arriba del form -->
                    <div class="oe_title">
                        <h1>
                            <field name="name" placeholder="Nombre..."/>
                        </h1>
                    </div>

                    <!-- Dos columnas lado a lado -->
                    <group>
                        <group string="Fechas">
                            <field name="date_start"/>
                            <field name="date_end"/>
                        </group>
                        <group string="Detalles">
                            <field name="capacity"/>
                            <field name="active"/>
                        </group>
                    </group>

                    <!-- Pestañas -->
                    <notebook>
                        <page string="Descripción" name="description">
                            <field name="description" nolabel="1"/>
                        </page>
                    </notebook>
                </sheet>

                <!-- Chatter: requiere _inherit = ['mail.thread', 'mail.activity.mixin'] -->
                <chatter/>
            </form>
        </field>
    </record>

    <!-- ============================================================
         VISTA BÚSQUEDA (search)
         Define qué se puede buscar, filtros predefinidos y agrupaciones.
         ============================================================ -->
    <record id="view_mi_modelo_search" model="ir.ui.view">
        <field name="name">mi.modelo.search</field>
        <field name="model">mi.modelo</field>
        <field name="arch" type="xml">
            <search string="Buscar">
                <!-- Campos por los que se puede buscar escribiendo -->
                <field name="name"/>

                <!-- Filtros con un clic. El 'name' se usa en search_default_X. -->
                <filter name="draft" string="Borrador"
                        domain="[('state', '=', 'draft')]"/>
                <filter name="done" string="Hechas"
                        domain="[('state', '=', 'done')]"/>

                <separator/>
                <filter name="active" string="Activos"
                        domain="[('active', '=', True)]"/>
                <filter name="archived" string="Archivados"
                        domain="[('active', '=', False)]"/>

                <!-- Agrupaciones -->
                <group expand="0" string="Agrupar por">
                    <filter name="group_state" string="Estado"
                            context="{'group_by': 'state'}"/>
                </group>
            </search>
        </field>
    </record>

    <!-- ============================================================
         ACCIÓN DE VENTANA
         Define qué abre el menú y qué vistas están disponibles.
         'context' puede precargar filtros y valores por defecto.
         ============================================================ -->
    <record id="action_mi_modelo" model="ir.actions.act_window">
        <field name="name">Mi modelo</field>
        <field name="res_model">mi.modelo</field>
        <field name="view_mode">tree,form</field>
        <field name="search_view_id" ref="view_mi_modelo_search"/>

        <!-- Preactiva el filtro "draft" de la vista search al abrir. -->
        <field name="context">{'search_default_draft': 1}</field>

        <!-- Texto que aparece cuando no hay registros todavía. -->
        <field name="help" type="html">
            <p class="o_view_nocontent_smiling_face">
                Crea tu primer registro.
            </p>
        </field>
    </record>

</odoo>
```

## Plantilla de `views/menu.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <!-- Menú raíz: aparece como “App” en la barra lateral. -->
    <menuitem id="menu_mi_modulo_root"
              name="Mi Módulo"
              sequence="10"/>

    <!-- Submenú de nivel 1 (agrupador, sin acción). -->
    <menuitem id="menu_mi_modulo_operaciones"
              name="Operaciones"
              parent="menu_mi_modulo_root"
              sequence="10"/>

    <!-- Submenú de nivel 2 con acción: al clicar, abre la vista. -->
    <menuitem id="menu_mi_modelo"
              name="Mi Modelo"
              parent="menu_mi_modulo_operaciones"
              action="action_mi_modelo"
              sequence="10"/>

    <!-- Menú de configuración (común en apps reales). -->
    <menuitem id="menu_mi_modulo_config"
              name="Configuración"
              parent="menu_mi_modulo_root"
              sequence="90"/>

</odoo>
```

> **Orden en el manifest:** primero los XML de vistas (que declaran
> `action_mi_modelo`), luego `menu.xml`. Si inviertes el orden, el menú
> no encuentra la acción y el módulo falla al instalarse.

## Vistas extra habituales

### Kanban

```xml
<record id="view_mi_modelo_kanban" model="ir.ui.view">
    <field name="name">mi.modelo.kanban</field>
    <field name="model">mi.modelo</field>
    <field name="arch" type="xml">
        <kanban default_group_by="state">
            <field name="name"/>
            <field name="state"/>
            <templates>
                <t t-name="kanban-box">
                    <div class="oe_kanban_card oe_kanban_global_click">
                        <strong><field name="name"/></strong>
                        <div>
                            <field name="state" widget="badge"
                                   decoration-success="state == 'done'"/>
                        </div>
                    </div>
                </t>
            </templates>
        </kanban>
    </field>
</record>
```

Luego en la acción añades `kanban` al `view_mode`:
`<field name="view_mode">kanban,tree,form</field>`.

### Calendario

```xml
<record id="view_mi_modelo_calendar" model="ir.ui.view">
    <field name="name">mi.modelo.calendar</field>
    <field name="model">mi.modelo</field>
    <field name="arch" type="xml">
        <calendar date_start="date_start" date_stop="date_end"
                  color="state" mode="month">
            <field name="name"/>
        </calendar>
    </field>
</record>
```

## Condiciones en la vista

```xml
<!-- Odoo 17: se usan expresiones Python directamente, SIN attrs="{…}" -->
<field name="email" readonly="state == 'done'"/>
<button name="action_cancel" invisible="state == 'cancelled'"/>
<field name="date_end" required="state == 'confirmed'"/>
```

## Stat buttons (botones-contador en el form)

Muy útil para enlazar a registros relacionados (ver guía 05).

```xml
<div class="oe_button_box" name="button_box">
    <button name="%(action_otro_modelo)d"
            type="action"
            class="oe_stat_button"
            icon="fa-calendar">
        <field name="booking_count" widget="statinfo" string="Reservas"/>
    </button>
</div>
```

- `name="%(action_otro_modelo)d"` abre esa acción (resolviendo la ID al
  vuelo).
- `%(id)d` es la sintaxis para referenciar un External ID como número
  en un XML.
- `widget="statinfo"` es el “look” de número grande encima de la
  etiqueta.

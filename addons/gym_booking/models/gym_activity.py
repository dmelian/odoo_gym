from odoo import models, fields

class GymActivity(models.Model):
    _name = 'gym.activity'
    _description = 'Actividad del gimnasio'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(
        string='Nombre',
        required=True,
        tracking=True
    )
    description = fields.Text(
        string='Descripción'
    )
    capacity = fields.Integer(
        string='Aforo máximo',
        required=True,
        default=10,
        tracking=True
    )
    active = fields.Boolean(
        string='Activo',
        default=True
    )
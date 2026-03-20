from odoo import models, fields

class GymInstructor(models.Model):
#    _name = 'gym.instructor'
#    _description = 'Monitor del gimnasio del gimnasio'. Usamos res.partner

    _inherit = 'res.partner' # ya hereda 'mail.thread', 'mail.activity.mixin'


    full_name_x = fields.Char(
        string='Nombre Completisimo',
        required=True,
        tracking=10
    )
    
    date_start_x = fields.Date(
        string='Fecha de alta X',
        required=True,
        default=fields.Date.today
    )

    gym_member_type = fields.Selection(
        selection=[
            ('member', 'Abonado'),
            ('instructor', 'Monitor'),
            ('admin', 'Administrativo'),
        ],
        string='Tipo en el gimnasio',
        default=False,
        tracking=20
    )
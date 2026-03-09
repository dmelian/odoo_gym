from odoo import models, fields, api

class GymConfig(models.Model):
    _name = 'gym.config'
    _description = 'Configuración del gimnasio'

    name = fields.Char(default='Configuración', readonly=True)
    auto_generate = fields.Boolean(
        string='Generación automática de reservas',
        default=False
    )
    generation_day = fields.Selection(
        selection=[
            ('3', 'Jueves'),
            ('4', 'Viernes'),
        ],
        string='Día de generación',
        default='3',
        required=True
    )
    generation_hour = fields.Float(
        string='Hora de generación',
        default=8.0,
        required=True
    )

    @api.model
    def get_config(self):
        config = self.search([], limit=1)
        if not config:
            config = self.create({})
        return config
    
    def action_generate_bookings_manual(self):
        self.env['gym.booking']._generate_weekly_bookings(force=True)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Reservas generadas',
                'message': 'Las reservas de la semana siguiente han sido generadas correctamente.',
                'type': 'success',
                'sticky': False,
            }
        }


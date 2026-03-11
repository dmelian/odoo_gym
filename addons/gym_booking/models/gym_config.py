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

    # Franjas horarias del grid semanal
    morning_start = fields.Float(string='Inicio mañana', default=9.0)
    morning_hours = fields.Integer(string='Horas mañana', default=4)
    afternoon_start = fields.Float(string='Inicio tarde', default=17.0)
    afternoon_hours = fields.Integer(string='Horas tarde', default=4)

    @api.model
    def get_config(self):
        config = self.search([], limit=1)
        if not config:
            config = self.create({})
        return config

    @api.model
    def action_open_config(self):
        config = self.get_config()  # obtiene o crea el singleton
        return {
            'type': 'ir.actions.act_window',
            'name': 'Configuración',
            'res_model': self._name,
            'res_id': config.id,       # <-- fuerza abrir ESE registro
            'view_mode': 'form',
            'target': 'current',
            'views': [(False, 'form')],
        }
    
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


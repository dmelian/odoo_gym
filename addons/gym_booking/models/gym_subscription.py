from odoo import models, fields, api
from odoo.exceptions import ValidationError

class GymSubscriptionLine(models.Model):
    _name = 'gym.subscription.line'
    _description = 'Línea de suscripción semanal'
    _order = 'member_id, schedule_id'

    member_id = fields.Many2one(
        comodel_name='gym.member',
        string='Abonado',
        required=True,
        ondelete='cascade'
    )
    schedule_id = fields.Many2one(
        comodel_name='gym.schedule',
        string='Sesión',
        required=True,
        ondelete='restrict'
    )
    sessions_per_week = fields.Integer(
        string='Sesiones por semana',
        required=True,
        default=1
    )
    active = fields.Boolean(
        string='Activo',
        default=True
    )

    # Campos relacionados para facilitar las vistas
    activity_id = fields.Many2one(
        comodel_name='gym.activity',
        string='Actividad',
        related='schedule_id.activity_id',
        store=True
    )
    day_of_week = fields.Selection(
        string='Día',
        related='schedule_id.day_of_week',
        store=True
    )
    time_start = fields.Float(
        string='Hora inicio',
        related='schedule_id.time_start',
        store=True
    )

    _sql_constraints = [
        (
            'unique_member_schedule',
            'UNIQUE(member_id, schedule_id)',
            'El abonado ya tiene esta sesión en su suscripción.'
        )
    ]

    @api.constrains('sessions_per_week')
    def _check_sessions_per_week(self):
        for record in self:
            if record.sessions_per_week < 1:
                raise ValidationError(
                    'El número de sesiones por semana debe ser al menos 1.'
                )
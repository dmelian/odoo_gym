from odoo import models, fields, api
from odoo.exceptions import ValidationError

class GymSchedule(models.Model):
    _name = 'gym.schedule'
    _description = 'Horario semanal de actividad'
    _order = 'day_of_week, time_start'

    activity_id = fields.Many2one(
        comodel_name='gym.activity',
        string='Actividad',
        required=True,
        ondelete='cascade'
    )
    day_of_week = fields.Selection(
        selection=[
            ('0', 'Lunes'),
            ('1', 'Martes'),
            ('2', 'Miércoles'),
            ('3', 'Jueves'),
            ('4', 'Viernes'),
            ('5', 'Sábado'),
            ('6', 'Domingo'),
        ],
        string='Día de la semana',
        required=True
    )
    time_start = fields.Float(
        string='Hora de inicio',
        required=True
    )
    time_end = fields.Float(
        string='Hora de fin',
        required=True
    )
    capacity = fields.Integer(
        string='Aforo',
        compute='_compute_capacity',
        store=True
    )
    active = fields.Boolean(
        string='Activo',
        default=True
    )

    @api.depends('activity_id.capacity')
    def _compute_capacity(self):
        for record in self:
            record.capacity = record.activity_id.capacity

    @api.constrains('time_start', 'time_end')
    def _check_times(self):
        for record in self:
            if record.time_end <= record.time_start:
                raise ValidationError(
                    'La hora de fin debe ser posterior a la hora de inicio.'
                )

    @api.depends('activity_id', 'day_of_week', 'time_start')
    def _compute_display_name(self):
        day_names = {
            '0': 'Lunes', '1': 'Martes', '2': 'Miércoles',
            '3': 'Jueves', '4': 'Viernes', '5': 'Sábado', '6': 'Domingo'
        }
        for record in self:
            hours = int(record.time_start)
            minutes = int((record.time_start - hours) * 60)
            time_str = f"{hours:02d}:{minutes:02d}"
            day_str = day_names.get(record.day_of_week, '')
            record.display_name = f"{record.activity_id.name} - {day_str} {time_str}"
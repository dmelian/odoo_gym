from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta

class GymBooking(models.Model):
    _name = 'gym.booking'
    _description = 'Reserva de sesión'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, schedule_id'

    name = fields.Char(
        string='Referencia',
        readonly=True,
        default='Nueva reserva'
    )
    member_id = fields.Many2one(
        comodel_name='gym.member',
        string='Abonado',
        required=True,
        ondelete='restrict',
        tracking=True
    )
    schedule_id = fields.Many2one(
        comodel_name='gym.schedule',
        string='Sesión',
        required=True,
        ondelete='restrict',
        tracking=True
    )
    date = fields.Date(
        string='Fecha',
        required=True,
        tracking=True
    )
    state = fields.Selection(
        selection=[
            ('confirmed', 'Confirmada'),
            ('cancelled', 'Cancelada'),
            ('attended', 'Asistida'),
        ],
        string='Estado',
        default='confirmed',
        tracking=True
    )
    origin = fields.Selection(
        selection=[
            ('manual', 'Manual'),
            ('automatic', 'Automática'),
        ],
        string='Origen',
        default='manual',
        readonly=True
    )

    # Campos relacionados para vistas y filtros
    activity_id = fields.Many2one(
        comodel_name='gym.activity',
        string='Actividad',
        related='schedule_id.activity_id',
        store=True
    )
    day_of_week = fields.Selection(
        string='Día de la semana',
        related='schedule_id.day_of_week',
        store=True
    )
    time_start = fields.Float(
        string='Hora inicio',
        related='schedule_id.time_start',
        store=True
    )
    capacity = fields.Integer(
        string='Aforo',
        related='schedule_id.capacity',
        store=True
    )
    bookings_count = fields.Integer(
        string='Reservas confirmadas',
        compute='_compute_bookings_count'
    )

    @api.depends('schedule_id', 'date')
    def _compute_bookings_count(self):
        for record in self:
            if record.schedule_id and record.date:
                record.bookings_count = self.search_count([
                    ('schedule_id', '=', record.schedule_id.id),
                    ('date', '=', record.date),
                    ('state', '=', 'confirmed'),
                    ('id', '!=', record.id or 0),
                ])
            else:
                record.bookings_count = 0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('gym.booking')
        return super().create(vals_list)

    @api.constrains('schedule_id', 'date', 'member_id', 'state')
    def _check_booking(self):
        for record in self:
            if record.state == 'cancelled':
                continue

            # Regla 1: antelación mínima de 24 horas
            if record.date:
                min_date = fields.Date.today() + timedelta(days=1)
                if record.date < min_date:
                    raise ValidationError(
                        'La reserva debe hacerse con al menos 24 horas de antelación.'
                    )

            # Regla 2: aforo no superado
            confirmed = self.search_count([
                ('schedule_id', '=', record.schedule_id.id),
                ('date', '=', record.date),
                ('state', '=', 'confirmed'),
                ('id', '!=', record.id),
            ])
            if confirmed >= record.schedule_id.capacity:
                raise ValidationError(
                    f'La sesión de {record.activity_id.name} del '
                    f'{record.date} está completa.'
                )

            # Regla 3: el abonado no tiene otra reserva ese día a la misma hora
            overlap = self.search_count([
                ('member_id', '=', record.member_id.id),
                ('date', '=', record.date),
                ('time_start', '=', record.time_start),
                ('state', '=', 'confirmed'),
                ('id', '!=', record.id),
            ])
            if overlap:
                raise ValidationError(
                    f'{record.member_id.name} ya tiene una reserva '
                    f'a las {record.time_start}h ese día.'
                )

    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'

    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'

    def action_attended(self):
        for record in self:
            record.state = 'attended'
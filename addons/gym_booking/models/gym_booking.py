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

    batch_id = fields.Many2one(
        comodel_name='gym.booking.batch',
        string='Lote',
        readonly=True
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
    
    @api.model
    def _generate_weekly_bookings(self, force=False):
        if not force:
            config = self.env['gym.config'].search([], limit=1)
            if config and not config.auto_generate:
                return

        today = fields.Date.today()
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        next_monday = today + timedelta(days=days_until_monday)

        subscriptions = self.env['gym.subscription.line'].search([
            ('active', '=', True),
            ('member_id.state', '=', 'active'),
        ])

        created = 0
        skipped = 0
        origin = 'manual' if force else 'automatic'

        batch = self.env['gym.booking.batch'].create({
            'origin': origin,
        })

        for sub in subscriptions:
            day_offset = int(sub.schedule_id.day_of_week)
            booking_date = next_monday + timedelta(days=day_offset)

            existing = self.search_count([
                ('member_id', '=', sub.member_id.id),
                ('schedule_id', '=', sub.schedule_id.id),
                ('date', '=', booking_date),
                ('state', '!=', 'cancelled'),
            ])
            if existing:
                skipped += 1
                continue

            confirmed = self.search_count([
                ('schedule_id', '=', sub.schedule_id.id),
                ('date', '=', booking_date),
                ('state', '=', 'confirmed'),
            ])
            if confirmed >= sub.schedule_id.capacity:
                sub.member_id.message_post(
                    body=f'No se ha podido generar la reserva automática de '
                        f'{sub.activity_id.name} para el {booking_date} '
                        f'por falta de aforo.',
                    subject='Reserva automática no disponible'
                )
                skipped += 1
                continue

            self.create({
                'member_id': sub.member_id.id,
                'schedule_id': sub.schedule_id.id,
                'date': booking_date,
                'state': 'confirmed',
                'origin': origin,
                'batch_id': batch.id,
            })
            created += 1

        batch.write({
            'bookings_created': created,
            'bookings_skipped': skipped,
        })

        return f'Generadas {created} reservas. Omitidas {skipped}.'

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

            # Regla 4: el día de la semana de la fecha debe coincidir con el horario
            if record.date and record.schedule_id:
                # date.weekday() devuelve 0=lunes, 1=martes... igual que nuestro Selection
                day_of_date = str(record.date.weekday())
                if day_of_date != record.schedule_id.day_of_week:
                    day_names = {
                        '0': 'Lunes', '1': 'Martes', '2': 'Miércoles',
                        '3': 'Jueves', '4': 'Viernes', '5': 'Sábado', '6': 'Domingo'
                    }
                    expected_day = day_names.get(record.schedule_id.day_of_week, '')
                    raise ValidationError(
                        f'La fecha elegida no es un {expected_day}. '
                        f'Este horario solo se imparte los {expected_day}s.'
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
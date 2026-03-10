from odoo import models, fields, api

class GymBookingBatch(models.Model):
    _name = 'gym.booking.batch'
    _description = 'Lote de generación de reservas'
    _order = 'date desc'

    name = fields.Char(
        string='Número',
        readonly=True,
        default='Nuevo lote'
    )
    date = fields.Datetime(
        string='Fecha y hora',
        readonly=True,
        default=fields.Datetime.now
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Usuario',
        readonly=True,
        default=lambda self: self.env.user
    )
    origin = fields.Selection(
        selection=[
            ('manual', 'Manual'),
            ('automatic', 'Automática'),
        ],
        string='Origen',
        readonly=True,
        default='manual'
    )
    bookings_created = fields.Integer(
        string='Reservas creadas',
        readonly=True,
        default=0
    )
    bookings_skipped = fields.Integer(
        string='Reservas omitidas',
        readonly=True,
        default=0
    )
    booking_ids = fields.One2many(
        comodel_name='gym.booking',
        inverse_name='batch_id',
        string='Reservas generadas'
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'gym.booking.batch'
            )
        return super().create(vals_list)
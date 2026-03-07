from odoo import models, fields, api
from odoo.exceptions import ValidationError

class GymMember(models.Model):
    _name = 'gym.member'
    _description = 'Abonado del gimnasio'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(
        string='Nombre',
        required=True,
        tracking=True
    )
    email = fields.Char(
        string='Email',
        tracking=True
    )
    phone = fields.Char(
        string='Teléfono'
    )
    date_start = fields.Date(
        string='Fecha de alta',
        required=True,
        default=fields.Date.today
    )
    date_end = fields.Date(
        string='Fecha de baja'
    )
    state = fields.Selection(
        selection=[
            ('active', 'Activo'),
            ('inactive', 'Baja'),
        ],
        string='Estado',
        default='active',
        tracking=True
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Usuario Odoo',
        help='Vincula el abonado con un usuario para el portal web'
    )
    subscription_line_ids = fields.One2many(
        comodel_name='gym.subscription.line',
        inverse_name='member_id',
        string='Sesiones semanales'
    )
    booking_ids = fields.One2many(
        comodel_name='gym.booking',
        inverse_name='member_id',
        string='Reservas'
    )
    booking_count = fields.Integer(
        string='Nº Reservas',
        compute='_compute_booking_count'
    )

    @api.depends('booking_ids')
    def _compute_booking_count(self):
        for record in self:
            record.booking_count = len(record.booking_ids)

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for record in self:
            if record.date_end and record.date_end < record.date_start:
                raise ValidationError(
                    'La fecha de baja no puede ser anterior a la fecha de alta.'
                )
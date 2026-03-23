from odoo import models, fields, api

class GymMember(models.Model):
    # Heredamos res.partner: el abonado ES un contacto de Odoo
    _name = 'gym.member'
    _inherits = {'res.partner': 'partner_id'}   # _inherits delega campos
    _description = 'Gym Member'

    # Campo delegado obligatorio con _inherits
    partner_id = fields.Many2one(
        'res.partner',
        required=True,
        ondelete='restrict',   # No borrar el partner si existe el abonado
        auto_join=True,
    )

    # Campos propios del gimnasio
    membership_number = fields.Char(string='Nº Abonado', copy=False)
    
    subscription_id = fields.Many2one(
        'sale.order',          # En v17 sale.subscription hereda sale.order
        string='Suscripción Mensual',
        domain=[('is_subscription', '=', True)],
    )

    # Límite de deuda acumulable antes de bloquear nuevas compras
    credit_limit = fields.Float(
        string='Límite de crédito (€)',
        default=100.0,
    )

    pending_charges_total = fields.Float(
        string='Total cargos pendientes',
        compute='_compute_pending_charges',
        store=True,
    )

    charge_ids = fields.One2many(
        'gym.product.charge',
        'member_id',
        string='Consumos pendientes',
    )

    @api.depends('charge_ids.amount', 'charge_ids.state')
    def _compute_pending_charges(self):
        for member in self:
            pending = member.charge_ids.filtered(
                lambda c: c.state == 'pending'
            )
            member.pending_charges_total = sum(pending.mapped('amount'))

    def action_view_subscription(self):
        """Botón para ir a la suscripción desde la ficha del abonado"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': self.subscription_id.id,
            'view_mode': 'form',
        }
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class GymProductCharge(models.Model):
    """
    Representa un producto vendido al abonado que queda 'pendiente'
    hasta que se factura junto con la mensualidad a final de mes.
    
    CONCEPTO PEDAGÓGICO: Este modelo actúa como un 'ticket' de consumo.
    Al cerrar el mes, estos tickets se convierten en líneas de factura.
    """
    _name = 'gym.product.charge'
    _description = 'Cargo pendiente de abonado'

    member_id = fields.Many2one(
        'gym.member',
        string='Abonado',
        required=True,
        ondelete='cascade',
    )

    product_id = fields.Many2one(
        'product.product',
        string='Producto/Servicio',
        required=True,
    )

    quantity = fields.Float(string='Cantidad', default=1.0)
    unit_price = fields.Float(string='Precio unitario')
    amount = fields.Float(
        string='Importe',
        compute='_compute_amount',
        store=True,
    )

    date = fields.Date(
        string='Fecha',
        default=fields.Date.today,
    )

    state = fields.Selection([
        ('pending', 'Pendiente'),
        ('invoiced', 'Facturado'),
        ('cancelled', 'Cancelado'),
    ], default='pending', string='Estado')

    subscription_line_id = fields.Many2one(
        'sale.order.line',
        string='Línea de suscripción generada',
        readonly=True,
    )

    @api.depends('quantity', 'unit_price')
    def _compute_amount(self):
        for charge in self:
            charge.amount = charge.quantity * charge.unit_price

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Rellena el precio unitario al seleccionar el producto"""
        if self.product_id:
            self.unit_price = self.product_id.lst_price

    @api.constrains('member_id', 'amount')
    def _check_credit_limit(self):
        """
        CONCEPTO PEDAGÓGICO: Validación que comprueba el límite de crédito.
        Se ejecuta al guardar. Si se supera el límite, lanza un error.
        """
        for charge in self:
            member = charge.member_id
            if member.pending_charges_total > member.credit_limit:
                raise ValidationError(
                    f'El abonado {member.name} ha superado su límite de '
                    f'crédito ({member.credit_limit} €). '
                    f'Total pendiente: {member.pending_charges_total} €'
                )
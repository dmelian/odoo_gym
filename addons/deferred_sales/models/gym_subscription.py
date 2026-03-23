from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class GymSubscription(models.Model):
    """
    Ampliamos sale.order (que en v17 gestiona suscripciones con
    is_subscription=True) para añadir la lógica de cargos del gimnasio.

    FLUJO PEDAGÓGICO:
    1. El abonado compra productos → se crean gym.product.charge
    2. A final de mes Odoo genera la factura de la suscripción
    3. Antes de generar la factura, nuestro override añade los cargos
       como líneas adicionales en esa misma factura
    4. Los cargos pasan a estado 'invoiced'
    """
    _inherit = 'sale.order'

    gym_member_id = fields.Many2one(
        'gym.member',
        string='Abonado del gimnasio',
        compute='_compute_gym_member',
        store=True,
    )

    @api.depends('partner_id')
    def _compute_gym_member(self):
        """Busca si el cliente de la suscripción es un abonado"""
        for order in self:
            member = self.env['gym.member'].search(
                [('partner_id', '=', order.partner_id.id)],
                limit=1,
            )
            order.gym_member_id = member or False

    def _create_recurring_invoice(self, automatic=False):
        """
        OVERRIDE CLAVE: Interceptamos la creación de la factura recurrente
        de sale.subscription para inyectar los cargos pendientes.

        En v17, este método (o _recurring_create_invoice) es llamado
        por el cron job de suscripciones.
        """
        # Llamamos primero al método estándar de Odoo
        invoices = super()._create_recurring_invoice(automatic=automatic)

        # Ahora añadimos nuestros cargos a la factura recién creada
        for invoice in invoices:
            # Buscamos el abonado relacionado con esta factura
            member = self.env['gym.member'].search(
                [('partner_id', '=', invoice.partner_id.id)],
                limit=1,
            )

            if not member:
                continue

            # Obtenemos los cargos pendientes de este abonado
            pending_charges = member.charge_ids.filtered(
                lambda c: c.state == 'pending'
            )

            if not pending_charges:
                _logger.info(
                    'Abonado %s sin cargos pendientes este mes.',
                    member.name,
                )
                continue

            # Añadimos una línea por cada cargo pendiente
            for charge in pending_charges:
                invoice.write({
                    'invoice_line_ids': [(0, 0, {
                        'product_id': charge.product_id.id,
                        'name': (
                            f'[Consumo {charge.date}] '
                            f'{charge.product_id.name}'
                        ),
                        'quantity': charge.quantity,
                        'price_unit': charge.unit_price,
                    })]
                })

            # Marcamos los cargos como facturados
            pending_charges.write({'state': 'invoiced'})

            _logger.info(
                'Añadidos %d cargos a la factura %s del abonado %s',
                len(pending_charges),
                invoice.name,
                member.name,
            )

        return invoices

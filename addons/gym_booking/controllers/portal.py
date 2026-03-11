from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class GymPortal(CustomerPortal):

@http.route('/my/gym', type='http', auth='user', website=True)
def gym_home(self, **kwargs):
    member = request.env['gym.member'].sudo().search([
        ('user_id', '=', request.env.user.id)
    ], limit=1)

    # DEBUG - quitar después
    import logging
    _logger = logging.getLogger(__name__)
    _logger.warning("USER ID: %s", request.env.user.id)
    _logger.warning("MEMBER: %s", member)
    _logger.warning("MEMBER NAME: %s", member.name if member else 'NO ENCONTRADO')

    return request.render('gym_module.portal_gym_home', {
        'member': member,
    })

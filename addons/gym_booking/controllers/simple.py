from odoo import http
from odoo.http import request

class GymSimple(http.Controller):

    @http.route('/inicio', auth='public', website=True)
    def mostrar_pagina(self, **kw):
        return request.render('gym_booking.inicio', {})
from odoo import http
from odoo.http import request

class MiControlador(http.Controller):

    @http.route('/mi-pagina', auth='public')
    def mi_pagina(self, **kwargs):
        return request.render('simple.mi_pagina_template')
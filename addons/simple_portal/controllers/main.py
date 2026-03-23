from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

class MiPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        
        if 'mi_count' in counters:
            values['mi_count'] = 42  # Aquí iría tu query real
        
        return values

    @http.route('/my/mi-pagina', auth='user', website=True)
    def mi_pagina(self, **kwargs):
        return request.render('simple_portal.mi_pagina_template')
    
    @http.route('/my/mi-pagina2', auth='user', website=True)
    def mi_pagina2(self, **kwargs):
        return request.render('simple_portal.mi_pagina2_template')
from odoo import http
from odoo.http import request

class MyModelController(http.Controller):
    @http.route('/requests', type='http', auth="user", website=True)
    def request_data(self):
        records = request.env['garpad.request'].sudo().search([('partner_id', '=', request.env.user.partner_id.id)])
        return request.render('garpad.website_garpad_request_templatenew', {'records': records})
class GarpdLand(http.Controller):
    @http.route('/ownlands', type='http', auth="user", website=True)
    def request_data(self):
        records = request.env['product.template'].sudo().search([('x_studio_owner', '=', request.env.user.id)])
        return request.render('garpad.website_garpad_lands_templatenew', {'records': records})
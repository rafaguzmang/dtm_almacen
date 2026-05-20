from odoo import http
form odoo.http import request
import json

class Ordenes(http.Controller):

    @http.route('/almacen_ordenes_revision', type='http', auth='public', csrf=False)
    def ordenRevision(self):
        ordenes = request.env['dtm.odt'].sudo().search([('estado', '=', True)])

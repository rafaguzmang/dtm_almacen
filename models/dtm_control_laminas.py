from odoo import fields, models, api

class Control(models.Model):
    _name = 'dtm.control.laminas'
    _description = 'Description'


    lamina = fields.Char(string='Nombre')
    cantidad = fields.Integer(string='Cantidad')
    orden_trabajo = fields.Integer(string='Orden de Trabajo')

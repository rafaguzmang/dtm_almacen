from odoo import fields, models, api

class Control(models.Model):
    _name = 'dtm.control.laminas'
    _description = 'Description'


    lamina = fields.Char(string='Nombre')

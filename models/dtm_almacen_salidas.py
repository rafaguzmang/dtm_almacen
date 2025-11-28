from odoo import models, fields, api

class DTMAlmacenSalidas(models.Model):
    _name = 'dtm.almacen.salidas'
    _description = 'Registro de Salidas de Almacén'

    codigo_material = fields.Char(string='Código de Material')
    nombre = fields.Char(string='Nombre')
    tipo = fields.Char(string='Tipo')
    cantidad_salida = fields.Float(string='Cantidad de Salida')
    responsable = fields.Char(string='Responsable que Recibe')
    fecha_salida = fields.Datetime(string='Fecha de Salida')
    

from odoo import models, fields, api

class StockStorageTag(models.Model):
    _name = 'stock.storage.tag'
    _description = 'Etiqueta Inteligente de Almacenamiento'

    name = fields.Char(string='Nombre', required=True)
    color = fields.Selection([
        ('0', 'Sin Color'),
        ('1', 'Rojo'),
        ('2', 'Naranja'),
        ('3', 'Amarillo'),
        ('4', 'Azul claro'),
        ('5', 'Morado oscuro'),
        ('6', 'Rosa'),
        ('7', 'Turquesa'),
        ('8', 'Azul oscuro'),
        ('9', 'Vinotinto'),
        ('10', 'Verde'),
        ('11', 'Morado claro'),
    ], string='Color', default='0')

    description = fields.Text(string='Descripción')
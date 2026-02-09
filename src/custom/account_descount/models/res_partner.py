from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    tipo_cliente = fields.Selection([
        ('minorista', 'Minorista'),
        ('mayorista', 'Mayorista'),
        ('vip', 'VIP')
    ], string='Tipo de Cliente')
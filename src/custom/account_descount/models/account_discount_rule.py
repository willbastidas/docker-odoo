from odoo import models, fields, _

class AccountDiscountRule(models.Model):
    _name = 'account.discount.rule'
    _description = 'Reglas de Descuento por Cliente'

    tipo_cliente = fields.Selection([
        ('minorista', 'Minorista'),
        ('mayorista', 'Mayorista'),
        ('vip', 'VIP')
    ], string='Tipo de Cliente', required=True)
    
    descuento = fields.Float(string='% Descuento', required=True)

    _sql_constraints = [
        ('unique_tipo', 'unique(tipo_cliente)', '¡Ya existe una regla para este tipo de cliente!')
    ]
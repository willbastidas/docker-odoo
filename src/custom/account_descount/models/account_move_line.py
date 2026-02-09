from odoo import models, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('product_id')
    def _onchange_product_id_apply_custom_discount(self):
        """ 
        Al cambiar el producto, buscamos la regla de descuento 
        basada en el tipo de cliente de la factura.
        """
        for line in self:
            if line.move_id.move_type in ['out_invoice', 'out_refund'] and line.move_id.partner_id.tipo_cliente:
                
                rule = self.env['account.discount.rule'].search([
                    ('tipo_cliente', '=', line.move_id.partner_id.tipo_cliente)
                ], limit=1)
                
                if rule:
                    line.discount = rule.descuento
from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    stock_min_alert = fields.Float(
        string="Mínimo de Regla de Stock",
        compute="_compute_stock_min_alert",
        store=True
    )

    @api.depends('product_variant_ids.orderpoint_ids.product_min_qty', 'qty_available', 'product_variant_ids.orderpoint_ids.qty_on_hand')
    def _compute_stock_min_alert(self):
        for template in self:
            total_diff = 0.0
            for variant in template.product_variant_ids:
                if variant.orderpoint_ids:
                    # Sumamos todos los mínimos de las reglas de esta variante
                    min_qty = sum(variant.orderpoint_ids.mapped('product_min_qty'))
                    # Restamos la cantidad a mano (qty_available es el nombre técnico)
                    # min_qty - cantidad_a_mano
                    total_diff += (min_qty - variant.qty_available)
            
            # Si el resultado es positivo, falta stock. Si es negativo, sobra.
            template.stock_min_alert = total_diff
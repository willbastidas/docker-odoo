from odoo import models, api, _

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def write(self, vals):
        """ Se dispara al actualizar el stock a mano o inventariar """
        res = super(StockQuant, self).write(vals)
        if 'inventory_quantity' in vals or 'quantity' in vals:
            for quant in self:
                self._check_orderpoint_and_notify(quant.product_id, quant.location_id)
        return res

    def _check_orderpoint_and_notify(self, product, location):
        """ Busca si el producto tiene regla de stock en esa ubicación y notifica """
        if not product or not location:
            return

        orderpoint = self.env['stock.warehouse.orderpoint'].search([
            ('product_id', '=', product.id),
            ('location_id', '=', location.id)
        ], limit=1)

        if orderpoint and product.qty_available < orderpoint.product_min_qty:
            self.env['stock.warehouse.orderpoint'].check_stock_and_notify(specific_product_id=product.id)
from odoo import models, api, _, fields
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.constrains('order_line')
    def _check_max_order_lines(self):
        for order in self:
            # Filtramos para contar solo productos (ignorando notas y secciones)
            product_lines = order.order_line.filtered(lambda l: not l.display_type)
            if len(product_lines) > 10:
                raise ValidationError(_(
                    "Para poder procesar este pedido, debe tener un máximo de 10 productos. "
                    "Su pedido actual tiene %s productos y excede el límite permitido para la impresión."
                ) % len(product_lines))
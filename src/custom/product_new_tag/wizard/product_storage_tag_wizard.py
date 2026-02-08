from odoo import models, fields, api

class ProductStorageTagWizard(models.TransientModel):
    _name = 'product.storage.tag.wizard'
    _description = 'Asistente de Etiquetado Masivo'

    product_ids = fields.Many2many(
        'product.template', 
        string='Productos a Etiquetar',
        default=lambda self: self.env.context.get('active_ids', [])
    )
    
    storage_tag_ids = fields.Many2many(
        'stock.storage.tag', 
        string='Etiquetas a Aplicar',
        required=True
    )

    def action_apply_tags(self):
        if not self.product_ids:
            return {'type': 'ir.actions.act_window_close'}
            
        for product in self.product_ids:
            product.write({
                'storage_tag_ids': [(4, tag.id) for tag in self.storage_tag_ids]
            })
        return {'type': 'ir.actions.act_window_close'}
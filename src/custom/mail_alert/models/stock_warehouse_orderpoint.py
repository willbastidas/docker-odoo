from odoo import models, fields, api, _
from datetime import date

class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    last_notification_date = fields.Date(string="Última notificación de stock bajo")

    @api.model
    def cron_check_stock_and_notify(self):
        """ Versión corregida y segura para el Cron """
        today = fields.Date.today()
        all_rules = self.search([
            '|', 
            ('last_notification_date', '<', today),
            ('last_notification_date', '=', False)
        ])

        count = 0
        for rule in all_rules:
            if count >= 5: # Límite de 5 productos
                break
            if rule.product_id.qty_available < rule.product_min_qty:
                self.check_stock_and_notify(specific_product_id=rule.product_id.id)
                count += 1
        
        return True
    
    @api.model
    def create_alert_channel(self):
        channel_name = "Alerta de producto"
        channel = self.env['discuss.channel'].search([('name', '=', channel_name)], limit=1)
        if not channel:
            channel = self.env['discuss.channel'].create({
                'name': channel_name,
                'channel_type': 'channel',
                'description': 'Notificaciones automáticas de stock mínimo',
            })

        group_user = self.env.ref('stock.group_stock_user')
        group_manager = self.env.ref('stock.group_stock_manager')

        all_inventory_users = group_user.users | group_manager.users
        partners_to_subscribe = all_inventory_users.mapped('partner_id')

        current_member_partners = channel.channel_partner_ids
        new_partners = partners_to_subscribe - current_member_partners

        if new_partners:
            channel.add_members(partner_ids=new_partners.ids)
            
        return channel

    @api.model
    def check_stock_and_notify(self, specific_product_id=None):
        channel = self.create_alert_channel()
        odoobot_partner_id = self.env.ref('base.partner_root').id
        hoy = fields.Date.today()
        
        domain = [('qty_to_order', '>', 0)]
        if specific_product_id:
            domain.append(('product_id', '=', specific_product_id))
            
        rules = self.search(domain)
        
        for rule in rules:
            if rule.last_notification_date == hoy:
                continue

            product_name = rule.product_id.display_name
            qty_available = rule.product_id.qty_available
            qty_min = rule.product_min_qty
            qty_to_buy = qty_min - qty_available

            mensaje = _(
                "🤖 **Alerta**:\n"
                "El producto **%(name)s** está por debajo del stock mínimo.\n"
                "Actual: %(current)s | Mínimo: %(min)s.\n"
                "Debe comprar **%(buy)s** unidades."
            ) % {
                'name': product_name,
                'current': qty_available,
                'min': qty_min,
                'buy': qty_to_buy,
            }

            # 1. Publicar el mensaje (esto ya genera una notificación interna de Odoo)
            channel.message_post(
                body=mensaje, 
                author_id=odoobot_partner_id, 
                message_type='comment'
            )
            
            rule.last_notification_date = hoy
            if specific_product_id:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('ALERTA DE STOCK MÍNIMO'),
                        'message': mensaje,
                        'type': 'warning',
                        'sticky': True,
                    }
                }
        return True
# -*- coding: utf-8 -*-
###############################################################################
# Author      : SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyright(c): 2021-Present.
# License URL : AGPL-3
###############################################################################
from odoo import models, fields, api, _
from datetime import timedelta
from odoo.exceptions import UserError, ValidationError
import re
import logging

_logger = logging.getLogger(__name__)

def truncate(number, decimals=2):
        """
        Trunca un número flotante a la cantidad de decimales indicada sin redondear.
        """
        if not isinstance(number, float):
            number = float(number)
        factor = 10 ** decimals
        return int(number * factor) / factor

class AccountMove(models.Model):

    _inherit = 'account.move'

    nro_ctrl = fields.Char(string='Número de Control', help='Número de control asignado por el proveedor del servicio fiscal.')

    @api.constrains('invoice_line_ids')
    def _check_max_lines(self):
        for move in self:
            # Filtramos para contar solo líneas que son productos (no notas o secciones)
            product_lines = move.invoice_line_ids.filtered(lambda l: not l.display_type)
            if len(product_lines) > 10:
                raise ValidationError("Para poder imprimir esta factura debe ser de máximo 10 productos, su factura actual excede ese máximo.")
            
    def print_escpos_new_reports(self):
        """
        Envía las líneas de la factura a la API local de FastAPI para impresión ESC/POS.
        """ 

        view = self.env.ref('inmarket.view_account_move_print_wizard_form', raise_if_not_found=False)
        discount = 0.0
        subt_sum = 0.0

        debit_note_number = ''
        credit_note_number = ''
        factura_afectada = ''
        factura = ''
        invoice_date = ''
        con_pago = ''
        invoice_date_due = ''
        journal_id_code = ''
        debit_origin_id = ''
        move_type = ''

        for move in self:
            if move.discount_amount:
                discount = move.discount_amount
            if move.partner_id.parent_id:
                RIF = move.partner_id.parent_id.rif or move.partner_id.parent_id.identification_id or move.partner_id.parent_id.vat
            else:
                RIF = move.partner_id.rif or move.partner_id.identification_id or move.partner_id.vat
            
            if not RIF:
                raise UserError("El RIF del cliente es obligatorio para imprimir la factura.")
            lines = []

            # Debemos formatear la direccion del cliente para que no exceda los 50 caracteres
            street_lines = []
            current_line = ""
            for word in move.partner_id.street.split(" "):
                if len(current_line) + len(word) + 1 <= (MAX_LINE_LENGTH := 50):
                    if current_line:
                        current_line += f" {word}"
                    else:
                        current_line += word
                else:
                    street_lines.append(current_line)
                    current_line = ""
                    current_line += word

            street_lines.append(current_line)

            # Encabezado fijo
            razon_social = f"{move.partner_id.name or ''}"
            rif_social = f"{RIF}"
            domi_social = f"{street_lines[0] or ''}"

            lines.append(f"{'Razón Social:':<35}{move.partner_id.name or ''}")
            lines.append(f"{'RIF:':<35}{RIF}")
            lines.append(f"{'Domicilio Fiscal:':<35}{street_lines[0] or ''}")

            for line in street_lines[1:]:
                if line:
                    lines.append(f"{'':<35}{line}")

            
            # Datos de factura
            move_type = move.move_type
            if move.move_type == 'out_invoice':
                journal_id_code = move.journal_id.code
                debit_origin_id = move.debit_origin_id
                if move.journal_id.code == 'ND' or move.debit_origin_id:
                    debit_note_number = f"{move.debit_note_number or ''}"
                    lines.append(f"{'NOTA DE DÉBITO:':<35}{move.debit_note_number or '':<20}{'FECHA DE NOTA DE DÉBITO:':<25}{(move.invoice_date or '').strftime('%d/%m/%Y') if move.invoice_date else '':<15}")
                    invoice_date = f"{(move.invoice_date or '').strftime('%d/%m/%Y') if move.invoice_date else '':<15}"
                    factura_afectada = move.debit_origin_id.invoice_number if move.debit_origin_id else ''
                    con_pago = f"{move.invoice_payment_term_id.name or ''}"
                    lines.append(f"{'FACTURA AFECTADA:':<35}{factura_afectada or '':<20}{'Condic. Pago:':<25}{move.invoice_payment_term_id.name or '':<15}")
                else:
                    factura = f"{(move.invoice_number or move.name or '')}"
                    invoice_date_due = f"{(move.invoice_date_due or '').strftime('%d/%m/%Y') if move.invoice_date_due else ''}"
                    con_pago = f"{move.invoice_payment_term_id.name or ''}"
                    lines.append(f"{'FACTURA:':<35}{(move.invoice_number or move.name or ''):<20}{'FECHA DE FACTURA:':<25}{(move.invoice_date or '').strftime('%d/%m/%Y') if move.invoice_date else '':<15}")
                    lines.append(f"{'FECHA DE VENCIMIENTO:':<35}{(move.invoice_date_due or '').strftime('%d/%m/%Y') if move.invoice_date_due else '':<20}{'Condic. Pago:':<25}{move.invoice_payment_term_id.name or '':<15}")
            elif move.move_type == 'out_refund' or move.reversed_entry_id:
                credit_note_number= f"{move.credit_note_number or move.name or ''}"
                lines.append(f"{'NOTA DE CRÉDITO:':<35}{move.credit_note_number or move.name or '':<20}")
                factura_afectada = move.reversed_entry_id.invoice_number if move.reversed_entry_id else ''
                lines.append(f"{'FACTURA AFECTADA:':<35}{factura_afectada or '':<20}{'FECHA DE NOTA DE CRÉDITO:':<35}{(move.invoice_date or '').strftime('%d/%m/%Y') if move.invoice_date else '':<15}")
                
            obs= f"{move.ref or ''}"
            lines.append(f"{'Observaciones:':<35}{move.ref or ''}")


            lines.append("")
            lines.append("-" * 107)
            # Encabezado de detalle de productos ajustado a la longitud de las líneas de factura (180 caracteres)
            # Agregamos un poco mas de espacio para que no se vea tan comprimido
            lines.append(
                f"{'Descripción':<35}{'Unid.':>8}{'Cajas':>7}{'Precio Unit.':>16}{'Desc (%)':>11}{'Subtotal':>18}"
            )
            lines.append("-" * 107)
            # Detalle de productos
            for line in move.invoice_line_ids:
                code = line.product_id.default_code or ''
                desc = line.name or ''
                # Si el producto tiene una sola variante, agregar el nombre de la variante entre paréntesis
                product = line.product_id
                if product and product.product_tmpl_id and len(product.product_tmpl_id.product_variant_ids) == 1:
                    variant_name = product.product_template_attribute_value_ids.mapped('name')
                    if variant_name:
                        desc = f"{desc} ({', '.join(variant_name)})"
                # Extraer el número después del último punto dentro de los corchetes y el texto posterior
                match = re.match(r"\[(?:\d+\.)*(\d+)\]\s*(.*)", desc)
                if match:
                    desc = f"{match.group(1)} {match.group(2)}"
                qty = f"{int(line.quantity):,}".replace(",", "#").replace(".", ",").replace("#", ".")
                cajas = f"{int(getattr(line, 'product_packaging_qty', 0)):,}".replace(",", "#").replace(".", ",").replace("#", ".")
                price = f"{truncate(line.price_unit, 2):,.2f}".replace(",", "#").replace(".", ",").replace("#", ".")
                # Calcular el subtotal SIN descuento aplicado
                if line.discount and False: # Desactivar el cálculo del subtotal con descuento
                    subtotal_sin_descuento = line.price_unit * line.quantity
                else:
                    subtotal_sin_descuento = line.price_subtotal
                subt_sum += subtotal_sin_descuento
                discount = line.discount or 0.0
                subtotal = f"{truncate(subtotal_sin_descuento, 2):,.2f}".replace(",", "#").replace(".", ",").replace("#", ".")
                currency = (move.currency_id.name or 'Bs').replace('USD', '$').replace('VEF', 'Bs')
                lines.append(f"{desc[:35]:<35}{qty:>6}{cajas:>6}{price:>15} {currency}{discount:>10}{subtotal:>17} {currency}")
            total_packages = sum(line.product_packaging_qty for line in move.invoice_line_ids)
            lines.append("-" * 107)
            # Totales en Bs
            base_imponible = sum(l.price_subtotal for l in move.invoice_line_ids)
            iva = sum(t.amount / 100 * l.price_subtotal for l in move.invoice_line_ids for t in l.tax_ids if t.amount)
            total_bsf = base_imponible + iva

            # === Calcular totales en USD usando la tasa del día ===
            usd_currency = self.env.ref('base.USD')
            bcv = 1.0
            if usd_currency and usd_currency.rate_ids:
                rate = usd_currency.rate_ids.sorted('name', reverse=True)[0]
                bcv = rate.inverse_company_rate or 1.0

            # Si la moneda de la factura NO es USD, convierte los totales
            usd_total = subt_sum / bcv if bcv else 0.0
            usd_iva = iva / bcv if bcv else 0.0
            usd_total_con_iva = total_bsf / bcv if bcv else 0.0
            if move.currency_id.name != 'USD':
                lines.append(f"{'Tasa BCV:':<35}{truncate(bcv,2):>25,.2f}".replace(",", "#").replace(".", ",").replace("#", ".") + f"{'':>10}" +  f"{'TOTAL DE CAJAS:':<15}{int(total_packages):>5}".replace(",", "#").replace(".", ",").replace("#", "."))
                lines.append("-" * 107)
                lines.append(f"{'Subtotal:':<35}{truncate(subt_sum,2):>25,.2f} Bs   |   {truncate(usd_total,2):>18,.2f} $".replace(",", "#").replace(".", ",").replace("#", "."))
                lines.append(f"{'IVA 16%:':<35}{truncate(iva,2):>25,.2f} Bs   |   {truncate(usd_iva,2):>18,.2f} $".replace(",", "#").replace(".", ",").replace("#", "."))
                # lines.append(f"{'Descuento %:':<35}{discount:>25} %    |".replace(",", "#").replace(".", ",").replace("#", "."))
                lines.append(f"{'TOTAL:':<35}{truncate(total_bsf,2):>25,.2f} Bs   |   {truncate(usd_total_con_iva,2):>18,.2f} $".replace(",", "#").replace(".", ",").replace("#", "."))
                # lines.append(f"{'TOTAL DE CAJAS:':<35}{int(total_packages):>25}".replace(",", "#").replace(".", ",").replace("#", "."))
            else:
                lines.append(f"{'Tasa BCV:':<35}{truncate(bcv,2):>25,.2f}".replace(",", "#").replace(".", ",").replace("#", ".") + f"{'':>10}" +  f"{'TOTAL DE CAJAS:':<15}{int(total_packages):>5}".replace(",", "#").replace(".", ",").replace("#", "."))
                lines.append("-" * 107)
                lines.append(f"{'Base Imponible USD:':<35}{truncate(usd_total,2):>25,.2f} $".replace(",", "#").replace(".", ",").replace("#", "."))
                lines.append(f"{'IVA USD:':<35}{truncate(usd_iva,2):>25,.2f} $".replace(",", "#").replace(".", ",").replace("#", "."))
                lines.append(f"{'TOTAL USD:':<35}{truncate(usd_total_con_iva,2):>25,.2f} $".replace(",", "#").replace(".", ",").replace("#", "."))
                # lines.append(f"{'TOTAL DE CAJAS:':<35}{int(total_packages):>25}".replace(",", "#").replace(".", ",").replace("#", "."))

            lines.append("-" * 107)
            lines.append("De conformidad con la normativa vigente que rige la materia, siempre y cuando no esté bajo los supuestos")
            lines.append("de exoneración, exención o no sujeción, de realizar el pago de la presente factura en moneda distinta")
            lines.append("a la de curso legal en el país, se generará un cobro adicional del 3% correspondiente al IGTF, sobre")
            lines.append("el monto de lo pagado.")

            base_imponible_formateado = f"{base_imponible:,.2f}".replace(",", "#").replace(".", ",").replace("#", ".")
            iva_fomateado = f"{iva:,.2f}".replace(",", "#").replace(".", ",").replace("#", ".")
            total_bsf_formateado = f"{total_bsf:,.2f}".replace(",", "#").replace(".", ",").replace("#", ".")

            _logger.info("Preparando líneas para impresión ESC/POS.")
            _logger.info(lines)
            for line in lines:
                _logger.debug(f"Línea preparada: {line}")

            if len(self.line_ids) > 10:
                raise UserError("Estimado usuario, por favor no exceda el límite de diez (10) líneas de productos por factura.")
                
            return {
                'type': 'ir.actions.act_window',
                'name': 'Imprimir Factura',
                'res_model': 'account.move.print.wizard',
                'view_mode': 'form',
                'view_id': self.env.ref('cosmosys_reports_universal.view_account_move_print_wizard_form_new_buttom').id,
                'target': 'new',
                'context': {
                    'active_ids': self.ids, 
                    'default_currency_name': move.currency_id.name,
                    'active_model': 'account.move',
                    'default_invoice_text': "\n".join(lines),
                    'default_line_ids': [(6, 0, move.invoice_line_ids.ids)],
                    'default_razon_social': razon_social,
                    'default_rif': rif_social,
                    'default_domi': domi_social,
                    'default_debit_note_number': debit_note_number,
                    'default_credit_note_number': credit_note_number,
                    'default_invoice_date': move.invoice_date,
                    'default_invoice_date_due': move.invoice_date_due,
                    'default_journal_id_code': journal_id_code,
                    'default_debit_origin_id': debit_origin_id,
                    'default_move_type': move_type,
                    'default_bcv': bcv,
                    'default_total_packages': total_packages,
                    'default_factura': factura,
                    'default_obs': obs,
                    'default_base_imponible': base_imponible_formateado,
                    'default_iva': iva_fomateado,
                    'default_usd_total': f"{truncate(usd_total, 2):,.2f}".replace(",", "#").replace(".", ",").replace("#", "."),
                    'default_usd_iva': f"{truncate(usd_iva, 2):,.2f}".replace(",", "#").replace(".", ",").replace("#", "."),
                    'default_usd_total_con_iva': f"{truncate(usd_total_con_iva, 2):,.2f}".replace(",", "#").replace(".", ",").replace("#", "."),
                    'default_total_bsf': total_bsf_formateado,
                    'default_factura_afectada': factura_afectada,
                    'default_con_pago': con_pago,
                    'default_state': move.state if move.state else 'draft',
                },
            }




class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # Campos para empaques y USD
    product_packaging_qty = fields.Float(
        string='Cantidad de empaque del producto',
        default=1.0,
    )
    
    product_packaging_id = fields.Many2one(
        comodel_name='product.packaging',
        string='Empaque del producto',
        help='Empaque del producto utilizado en la factura',
    )
    
    @api.onchange('product_packaging_id', 'product_packaging_qty')
    def _onchange_packaging_quantity(self):
        if self.product_packaging_id:
            # Calcula la cantidad total de unidades
            self.quantity = self.product_packaging_qty * self.product_packaging_id.qty
        else:
            # Si no hay empaque, la cantidad es la que se ingrese manualmente
            self.quantity = self.product_packaging_qty

    @api.depends('product_packaging_qty')
    def _onchange_product_packaging_qty(self):
        """Actualiza la cantidad cuando cambia la cantidad de empaques"""
        for line in self:
            if line.product_packaging_id:
                line.quantity = line.product_packaging_id.qty * line.product_packaging_qty

    @api.depends('quantity')
    def _compute_quantity(self):
        """Calcula la cantidad de empaques basado en la cantidad total"""
        for line in self:
            if line.product_packaging_id and line.product_packaging_id.qty and line.quantity:
                line.product_packaging_qty = line.quantity / line.product_packaging_id.qty
            else:
                line.product_packaging_qty = 1.0

    @api.onchange('product_id')
    def _onchange_product_id_set_packaging(self):
        """Establece el empaque por defecto cuando se selecciona un producto"""
        for line in self:
            if line.product_id:
                packaging = self.env['product.packaging'].search([
                    ('product_id', '=', line.product_id.id),
                ], limit=1)
                if packaging:
                    line.product_packaging_id = packaging
                    line.product_packaging_qty = 1.0
                else:
                    line.product_packaging_id = False
                    line.product_packaging_qty = 1.0
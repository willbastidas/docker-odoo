# -*- coding: utf-8 -*-
from odoo import models, fields
import logging
import requests
from urllib.parse import urlparse # Necesario para procesar la URL

_logger = logging.getLogger(__name__)

class AccountMovePrintWizard(models.TransientModel):
    _name = 'account.move.print.wizard'
    _description = 'Account Move Print Wizard'

    move_ids = fields.Many2many('account.move', string='Moves')

    invoice_text = fields.Text(string='Invoice Text', help='Text to be printed on the invoice')

    razon_social = fields.Text(string='razon_social', help='Text to be printed on the invoice')

    rif = fields.Text(string='RIF', help='Text to be printed on the invoice')

    domi = fields.Text(string='Domicilio Fiscal', help='Text to be printed on the invoice')

    debit_note_number = fields.Text(string='debit_note_number', help='Text to be printed on the invoice')

    credit_note_number = fields.Text(string='credit_note_number', help='Text to be printed on the invoice')

    journal_id_code = fields.Text(string='journal_id_code', help='Text to be printed on the invoice')

    move_type = fields.Text(string='move_type', help='Text to be printed on the invoice')

    debit_origin_id = fields.Text(string='debit_origin_id', help='Text to be printed on the invoice')

    con_pago = fields.Text(string='con_pago', help='Text to be printed on the invoice')

    factura = fields.Text(string='factura', help='Text to be printed on the invoice')

    factura_afectada = fields.Text(string='factura_afectada', help='Text to be printed on the invoice')

    obs = fields.Text(string='obs', help='Text to be printed on the invoice')

    bcv = fields.Text(string='bcv', help='Text to be printed on the invoice')

    total_packages = fields.Text(string='total_packages', help='Text to be printed on the invoice')

    base_imponible = fields.Text(string='base_imponible', help='Text to be printed on the invoice')

    iva = fields.Text(string='iva', help='Text to be printed on the invoice')
    
    total_bsf = fields.Text(string='total_bsf', help='Text to be printed on the invoice')

    usd_total = fields.Text(string='usd_total', help='Text to be printed on the invoice')

    usd_iva = fields.Text(string='usd_iva', help='Text to be printed on the invoice')
    
    usd_total_con_iva = fields.Text(string='usd_total_con_iva', help='Text to be printed on the invoice')
    
    currency_name = fields.Text(string='Moneda')

    invoice_date = fields.Date(string='invoice_date', help='Text to be printed on the invoice')

    invoice_date_due = fields.Date(string='invoice_date_due', help='Text to be printed on the invoice')

    line_ids = fields.Many2many('account.move.line', string='Líneas de Factura')



    state = fields.Selection(
        [('draft', 'Draft'), ('posted', 'Posted'), ('cancel', 'Cancelled')],
        string='State',
        default='draft',
        help='State of the invoice',
    )
    
    def action_generate_pdf_new(self):
        # Retorna la acción de reporte definida en el XML
        # Asegúrate que el string coincida con "nombre_modulo.id_del_xml"
        print(self, self.id)
        return self.env.ref('cosmosys_reports_universal.action_report_print_wizard_pdf').report_action(self)
{
    'name': 'Factura Venezolana universal',
    'version': '17.0.0.1',
    'description': """
    **Comprobantes para Factura Venezolana**
    ¡Felicidades!. Este es el módulo para Generar Comprobantes PDF de
    Factura Venezolana para la implementación de la **Localización Venezolana**
    """,
    'author': 'will bas',
    'website': 'https://github.com/willbastidas',
    'license': 'AGPL-3',
    'category': 'Localization / Venezuela',
    'depends': [
        'base',
        'account',
        'sale',
        'sale_management',
        # 'l10n_ve',
        'l10n_ve_full',
        'dollar_rate',
        'account_dual_currency'
    ],
    'data': [
        'security/ir.model.access.csv',
        'templates/report_invoice_text.xml',
        'templates/fix_sale_report.xml',
        'wizard/account_move_print_wizard.xml',
        # 'data/external_layout_report.xml',
        'views/account_move.xml',
    ],
    'auto_install': False,
    'application': False,
    'installable': True,
}

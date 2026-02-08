{
    'name': 'mail alert',
    'version': '17.0.0.1',
    'description': """
    """,
    'author': 'will bas',
    'website': 'https://github.com/willbastidas',
    'license': '',
    'category': '',
    'depends': [
        'base',
        'account',
        'mail',
        'mail_bot',
        'stock'
    ],
    'data': [
        'data/ir_cron.xml',
        'views/product_template_view.xml',
    ],
    'auto_install': False,
    'application': False,
    'installable': True,
}

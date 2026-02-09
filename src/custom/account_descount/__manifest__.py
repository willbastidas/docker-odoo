{
    'name': 'descount contact',
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
        'account_accountant',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/discount_policy_views.xml',
    ],
    'auto_install': False,
    'application': False,
    'installable': True,
}

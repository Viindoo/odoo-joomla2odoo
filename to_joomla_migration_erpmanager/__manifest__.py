{
    'name': "Joomla Migration ERPManager",
    'summary': """Migrate ERPManager to Odoo""",
    'description': """""",
    'author': "T.V.T Marine Automation (aka TVTMA)",
    'website': 'https://ma.tvtmarine.com',
    'support': 'support@ma.tvtmarine.com',
    'category': 'Extra Tools',
    'version': '0.1',
    'depends': [
        'to_joomla_migration',
        'to_migration_track_erpmanager',
        'to_odoo_saas_sale'
    ],
    'data': [
        'wizard/joomla_migration_views.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}

# -*- coding: utf-8 -*-
{
    'name': "Website Migration Track - Website",

    'summary': """
Provide tracking information for data that have been migrated from other website
""",

    'description': """
        Long description of module's purpose
    """,

    'author': "T.V.T Marine Automation (aka TVTMA)",
    'website': 'https://ma.tvtmarine.com',
    'live_test_url': 'https://v12demo-joomla.erponline.vn',
    'support': 'support@ma.tvtmarine.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Extra Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_migration_track', 'website'],

    # always loaded
    'data': [
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}

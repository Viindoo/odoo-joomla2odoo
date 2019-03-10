# -*- coding: utf-8 -*-
{
    'name': "Multi Websites",
    'summary': """Improve Multi-websites Features""",
    'description': """
    1. Improve Multi-websites Features
    2. This is not needed since Odoo v12.0
    """,
    'author': "T.V.T Marine Automation (aka TVTMA)",
    'website': 'https://ma.tvtmarine.com',
    'live_test_url': 'https://v11demo-joomla.erponline.vn',
    'support': 'support@ma.tvtmarine.com',
    'category': 'Hidden',
    'version': '0.1',
    'depends': ['website'],
    'data': [
        'views/website_views.xml',
        'views/website_menu_views.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}

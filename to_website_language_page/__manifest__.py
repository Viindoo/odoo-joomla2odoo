# -*- coding: utf-8 -*-
{
    'name': "Website pages Language Restriction",

    'summary': """
Restrict Pages from display on unsupported language website""",

    'summary_vi_VN': """
        """,

    'description': """
Restrict Pages from display on unsupported language website
    """,

    'description_vi_VN': """
    """,

    'author': "T.V.T Marine Automation (aka TVTMA)",
    'website': "https://www.tvtmarine.com",
    'live_test_url': "https://v12demo-int.erponline.vn",
    'support': "support@ma.tvtmarine.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Website',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website'],

    # always loaded
    'data': [
        'views/website_page_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1',
}


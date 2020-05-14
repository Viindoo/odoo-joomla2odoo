# -*- coding: utf-8 -*-
{
    'name': "Http Reroute Encoding",
    'summary': """Fix URL encoding error on rerouting""",
    'description': """
Related issue: https://github.com/odoo/odoo/issues/25176

For multi language website, when request http:/localhost/en_US/something, odoo
reroutes from the requested path "/en_US/something" to the new path "/something"
with lang=en_US in context. If the new path is a unicode string like "/xin-chào",
a error should occur at werkzeug._compat.wsgi_decoding_dance() because the path
was not latin1 string. This module fixes the issue by converting the path to latin1
using corresponding wsgi_encoding_dance() before it is passed to wsgi_decoding_dance().
    """,
    'author': "T.V.T Marine Automation (aka TVTMA)",
    'website': 'https://ma.tvtmarine.com',
    'live_test_url': 'https://v12demo-joomla.erponline.vn',
    'support': 'support@ma.tvtmarine.com',
    'category': 'Extra Tools',
    'version': '0.1',
    'depends': ['http_routing'],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}

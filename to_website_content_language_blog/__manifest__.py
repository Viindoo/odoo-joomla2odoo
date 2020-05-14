# -*- coding: utf-8 -*-
{
    'name': "Website Blog Language Restriction",

    'summary': """
Restrict Blog Posts from display on unsupported language website""",

    'description': """
Restrict Blog Posts from display on unsupported language website
    """,

    'author': "T.V.T Marine Automation (aka TVTMA)",
    'website': 'https://ma.tvtmarine.com',
    'live_test_url': 'https://v11demo-joomla.erponline.vn',
    'support': 'support@ma.tvtmarine.com',
    'category': 'Website',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website_blog', 'to_website_content_language'],

    # always loaded
    'data': [
        'views/blog_post_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}

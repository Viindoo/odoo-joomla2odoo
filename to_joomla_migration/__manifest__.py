# -*- coding: utf-8 -*-
{
    'name': "Joomla - Odoo Migration",
    'summary': """Migrate Joomla to Odoo""",
    'description': """
What this does
==============
This application help you migrate your Joomla Websites to your Odoo system. Here is the data that is migrated by this application

The migration Scope
-------------------

1. Joomla Users -> Odoo Users
2. Joomla Articles (aka com_content) -> Odoo Website Pages
3. Joomla EasyBlog -> Odoo Blog
4. Joomla EasyDiscuss -> Odoo Forum

Before migration, the administrator can

1. Enable/Disable Odoo's Invitation Emails during users migration. A special email template is added to allow the adminsitrator to prepare a message to send to the migrated users
2. Map Joomla Article Categories with either Website Pages or Website Blog

Old URLs redirect
-----------------
During migration, this application creates a map of old URLs (Joomla based URLs) to new Odoo based URLs and store in the Redirect model. Odoo will then know how to do redirect for you.  

Joomla Database Supported
-------------------------
1. MySQL

External Dependencies
---------------------
Python: mysql-connector-python, bbcode which can be installed on your Odoo server by firing command

    .. code:: python
      
      pip install mysql-connector-python

    .. code:: python
    
      pip install bbcode

Eddition Support
================

1. Community Edition
2. Enterprise Edition
    """,
    'author': "T.V.T Marine Automation (aka TVTMA)",
    'website': 'https://ma.tvtmarine.com',
    'live_test_url': 'https://v12demo-joomla.erponline.vn',
    'support': 'support@ma.tvtmarine.com',
    'category': 'Extra Tools',
    'version': '0.1',
    'depends': [
        'auth_signup',
        'to_website_language_page',
        'to_website_language_blog',
        'to_website_language_forum',
        'to_migration_track_website',
        'to_migration_track_website_blog',
        'to_migration_track_website_forum'
    ],
    'data': [
        'data/mail_template_data.xml',
        'views/joomla_model_views.xml',
        'wizard/joomla_migration_views.xml'
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': False,
    'application': True,
    'auto_install': False,
    'price': 495.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}

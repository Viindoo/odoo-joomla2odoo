{
    'name': "Joomla Migration Website Doc",
    'summary': """Migrate Joomla Articles to Website Documents""",
    'description': """
What this does
==============
This application help you migrate your Joomla Websites to your Odoo system. Here is the data that is migrated by this application

The migration Scope
-------------------

1. Joomla Users -> Odoo Users
2. Joomla Articles (aka com_content) -> Odoo Website Pages
3. Joomla Articles -> Website Documents https://apps.odoo.com/apps/modules/11.0/to_website_docs/
4. Joomla EasyBlog -> Odoo Blog
   

Before migration, the administrator can

1. Enable/Disable Odoo's Invitation Emails during users migration. A special email template is added to allow the adminsitrator to prepare a message to send to the migrated users
2. Map Joomla Article Categories with either Website Pages or Website Blog or Website Documents

Joomla Database Supported
-------------------------
1. MySQL

External Dependencies
---------------------
Python: mysql-connector-python which can be installed on your Odoo server by firing command

    .. code:: python
      
      pip install mysql-connector-python

Eddition Support
================

1. Community Edition
2. Enterprise Edition
    """,
    'author': "T.V.T Marine Automation (aka TVTMA)",
    'website': 'https://ma.tvtmarine.com',
    'live_test_url': 'https://v11demo-joomla.erponline.vn',
    'support': 'support@ma.tvtmarine.com',
    'category': 'Extra Tools',
    'version': '0.1',
    'depends': [
        'to_joomla_migration',
        'to_website_docs',
        'to_website_docs_odoo_data'
    ],
    'data': [
        'wizard/migration_views.xml'
    ],
'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}

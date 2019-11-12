from odoo import models


class WebsitePage(models.Model):
    _name = 'website.page'
    _inherit = ['website.page', 'abstract.joomla.migration.track']

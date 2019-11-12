from odoo import models


class WebsiteDocTag(models.Model):
    _name = 'website.doc.tag'
    _inherit = ['website.doc.tag', 'abstract.joomla.migration.track']

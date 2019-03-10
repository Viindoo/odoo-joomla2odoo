from odoo import models


class WebsiteRedirect(models.Model):
    _name = 'website.redirect'
    _inherit = ['website.redirect', 'abstract.joomla.migration.track']

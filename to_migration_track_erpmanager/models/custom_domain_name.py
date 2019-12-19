from odoo import models


class CustomDomainName(models.Model):
    _name = 'custom.domain.name'
    _inherit = ['custom.domain.name', 'abstract.joomla.migration.track']

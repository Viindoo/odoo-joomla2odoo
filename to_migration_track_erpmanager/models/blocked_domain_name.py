from odoo import models


class BlockedDomainName(models.Model):
    _name = 'blocked.domain.name'
    _inherit = ['blocked.domain.name', 'abstract.joomla.migration.track']

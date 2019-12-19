from odoo import models


class DnsDomain(models.Model):
    _name = 'dns.domain'
    _inherit = ['dns.domain', 'abstract.joomla.migration.track']

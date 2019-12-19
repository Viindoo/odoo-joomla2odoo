from odoo import models


class DNSZone(models.Model):
    _name = 'dns.zone'
    _inherit = ['dns.zone', 'abstract.joomla.migration.track']

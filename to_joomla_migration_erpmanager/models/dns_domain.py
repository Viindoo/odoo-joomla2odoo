from odoo import models
from odoo.addons.to_dns.models.dns_domain import DnsDomain as InitialDnsDomain


class DnsDomain(models.Model):
    _inherit = 'dns.domain'

    def create(self, vals_list):
        if self._context.get('joomla_migration'):
            # Bypass some overridden create methods
            return InitialDnsDomain.create(self, vals_list)
        return super(DnsDomain, self).create(vals_list)

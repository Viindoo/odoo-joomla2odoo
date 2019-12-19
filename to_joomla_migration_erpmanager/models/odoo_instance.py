from odoo import models
from odoo.addons.to_odoo_saas.models.odoo_instance import OdooInstance as InitialOdooInstance


class OdooInstance(models.Model):
    _inherit = 'odoo.instance'

    def create(self, vals_list):
        if self._context.get('joomla_migration'):
            # Bypass instance's overridden create method
            return super(InitialOdooInstance, self).create(vals_list)
        return super(OdooInstance, self).create(vals_list)

from odoo import models


class OdooInstanceHistory(models.Model):
    _inherit = 'odoo.instance.history'

    def split(self, split_date=None):
        if not self._context.get('joomla_migration'):
            super(OdooInstanceHistory, self).split(split_date)

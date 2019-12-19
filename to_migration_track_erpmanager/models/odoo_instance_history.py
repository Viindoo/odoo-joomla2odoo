from odoo import models


class OdooInstanceHistory(models.Model):
    _name = 'odoo.instance.history'
    _inherit = ['odoo.instance.history', 'abstract.joomla.migration.track']

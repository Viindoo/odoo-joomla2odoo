from odoo import models


class OdooInstanceHistorySplit(models.Model):
    _name = 'odoo.instance.history.split'
    _inherit = ['odoo.instance.history.split', 'abstract.joomla.migration.track']

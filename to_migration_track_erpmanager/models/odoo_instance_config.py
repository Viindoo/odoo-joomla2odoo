from odoo import models


class OdooInstanceConfig(models.Model):
    _name = 'odoo.instance.config'
    _inherit = ['odoo.instance.config', 'abstract.joomla.migration.track']

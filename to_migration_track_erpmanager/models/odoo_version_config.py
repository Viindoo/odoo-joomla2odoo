from odoo import models


class OdooVersionConfig(models.Model):
    _name = 'odoo.version.config'
    _inherit = ['odoo.version.config', 'abstract.joomla.migration.track']
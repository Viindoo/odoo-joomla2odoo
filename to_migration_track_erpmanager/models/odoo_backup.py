from odoo import models


class OdooBackup(models.Model):
    _name = 'odoo.backup'
    _inherit = ['odoo.backup', 'abstract.joomla.migration.track']

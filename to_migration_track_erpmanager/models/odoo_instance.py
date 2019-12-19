from odoo import models


class OdooInstance(models.Model):
    _name = 'odoo.instance'
    _inherit = ['odoo.instance', 'abstract.joomla.migration.track']

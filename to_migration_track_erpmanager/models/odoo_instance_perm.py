from odoo import models


class OdooInstancePerm(models.Model):
    _name = 'odoo.instance.perm'
    _inherit = ['odoo.instance.perm', 'abstract.joomla.migration.track']

from odoo import models


class OdooVServer(models.Model):
    _name = 'odoo.vserver'
    _inherit = ['odoo.vserver', 'abstract.joomla.migration.track']

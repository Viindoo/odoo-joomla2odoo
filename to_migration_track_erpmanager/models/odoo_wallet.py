from odoo import models


class OdooWallet(models.Model):
    _name = 'odoo.wallet'
    _inherit = ['odoo.wallet', 'abstract.joomla.migration.track']

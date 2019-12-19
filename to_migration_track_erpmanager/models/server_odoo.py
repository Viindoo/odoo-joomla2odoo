from odoo import models


class ServerOdoo(models.Model):
    _name = 'server.odoo'
    _inherit = ['server.odoo', 'abstract.joomla.migration.track']

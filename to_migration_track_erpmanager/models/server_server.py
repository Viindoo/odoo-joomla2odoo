from odoo import models


class ServerServer(models.Model):
    _name = 'server.server'
    _inherit = ['server.server', 'abstract.joomla.migration.track']

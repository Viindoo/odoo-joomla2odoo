from odoo import models


class ServerPort(models.Model):
    _name = 'server.port'
    _inherit = ['server.port', 'abstract.joomla.migration.track']

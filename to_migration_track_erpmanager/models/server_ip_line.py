from odoo import models


class ServerIPLine(models.Model):
    _name = 'server.ip.line'
    _inherit = ['server.ip.line', 'abstract.joomla.migration.track']

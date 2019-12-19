from odoo import models


class ServerDNS(models.Model):
    _name = 'server.dns'
    _inherit = ['server.dns', 'abstract.joomla.migration.track']
